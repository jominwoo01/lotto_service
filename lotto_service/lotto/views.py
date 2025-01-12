from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from .models import LottoSettings, LottoTicket, WinningNumber
from random import sample


# 관리자 권한 확인 데코레이터
def is_admin(user):
    return user.is_staff  # 관리자 여부 확인


# 관리자 권한이 없는 경우 처리하는 뷰
def admin_only_view(request):
    if not request.user.is_authenticated:
        return redirect('/admin/login/')  # 로그인하지 않은 경우 로그인 페이지로 리디렉션
    return render(request, 'not_authorized.html')  # 권한이 없는 경우 페이지 표시


# 홈 페이지 뷰
def home(request):
    return render(request, 'home.html', {'user': request.user})


# 로또 구매 뷰
def buy_lotto(request):
    # 판매 상태 확인
    settings = LottoSettings.objects.first()
    if settings and not settings.is_sales_open:  # 판매 종료 여부 확인
        return render(request, 'buy.html', {'error': '현재 로또 판매가 종료되었습니다.'})

    if request.method == 'POST':
        numbers = request.POST.get('numbers')
        if not numbers:  # 번호가 없으면 랜덤 생성
            numbers = ','.join(map(str, sample(range(1, 46), 6)))
        else:
            try:
                user_numbers = list(map(int, numbers.split(',')))
                if len(user_numbers) != 6 or len(set(user_numbers)) != 6:
                    raise ValueError("1~45 사이의 고유 번호 6개를 입력해야 합니다.")
                if not all(1 <= n <= 45 for n in user_numbers):
                    raise ValueError("번호는 1~45 사이로 입력해야 합니다.")
            except ValueError as e:
                return render(request, 'buy.html', {'error': str(e)})

        # 티켓 생성 (로그인 여부와 관계없이 생성)
        ticket = LottoTicket.objects.create(
            user=request.user if request.user.is_authenticated else None,  # 로그인한 사용자 연결 또는 None
            numbers=numbers
        )

        # 구매 완료 페이지로 리디렉션
        return redirect('buy_complete', ticket_id=ticket.id)

    return render(request, 'buy.html')


# 구매 완료 뷰
def buy_complete(request, ticket_id):
    try:
        ticket = LottoTicket.objects.get(id=ticket_id)
    except LottoTicket.DoesNotExist:
        return render(request, 'buy_complete.html', {'error': '티켓 정보를 찾을 수 없습니다.'})

    return render(request, 'buy_complete.html', {
        'ticket_id': ticket.id,
        'numbers': ticket.numbers,
        'purchased_at': ticket.purchased_at
    })


# 당첨 번호 추첨 뷰
@staff_member_required
def draw_winning_numbers(request):
    if request.method == 'POST':
        numbers = sample(range(1, 46), 7)
        winning_numbers = numbers[:6]
        bonus_number = numbers[6]

        WinningNumber.objects.create(
            numbers=','.join(map(str, winning_numbers)),
            bonus_number=bonus_number
        )

        return render(request, 'draw.html', {
            'numbers': ', '.join(map(str, winning_numbers)),
            'bonus_number': bonus_number,
            'success': True
        })

    return render(request, 'draw.html', {'success': False})


# 당첨 결과 확인 뷰
def check_results(request):
    if request.method == 'POST':
        ticket_id = request.POST.get('ticket_id')

        if not ticket_id:
            return render(request, 'results.html', {'error': '티켓 번호를 입력하세요.'})

        try:
            ticket = LottoTicket.objects.get(id=int(ticket_id))
        except (LottoTicket.DoesNotExist, ValueError):
            return render(request, 'results.html', {'error': '유효하지 않은 티켓 번호입니다.'})

        winning = WinningNumber.objects.last()
        if not winning:
            return render(request, 'results.html', {'error': '당첨 번호가 아직 없습니다.'})

        ticket_numbers = set(map(int, ticket.numbers.split(',')))
        winning_numbers = set(map(int, winning.numbers.split(',')))
        bonus_number = winning.bonus_number

        matched_count = len(ticket_numbers & winning_numbers)
        is_bonus_matched = bonus_number in ticket_numbers

        rank = None
        if matched_count == 6:
            rank = "1등"
        elif matched_count == 5 and is_bonus_matched:
            rank = "2등"
        elif matched_count == 5:
            rank = "3등"
        elif matched_count == 4:
            rank = "4등"
        elif matched_count == 3:
            rank = "5등"

        return render(request, 'results.html', {
            'ticket_id': ticket.id,
            'ticket_numbers': ticket.numbers,
            'winning_numbers': winning.numbers,
            'bonus_number': bonus_number,
            'rank': rank,
            'is_winner': rank is not None,
        })

    return render(request, 'results.html')


# 통계 페이지 뷰
def stats(request):
    winning = WinningNumber.objects.last()
    if not winning:
        return render(request, 'stats.html', {'error': '당첨 번호가 아직 없습니다.'})

    winning_numbers = set(map(int, winning.numbers.split(',')))
    bonus_number = winning.bonus_number

    results = {
        '1등_당첨자_수': 0,
        '2등_당첨자_수': 0,
        '3등_당첨자_수': 0,
        '4등_당첨자_수': 0,
        '5등_당첨자_수': 0,
        '낙첨자_수': 0,
    }

    for ticket in LottoTicket.objects.all():
        ticket_numbers = set(map(int, ticket.numbers.split(',')))
        matched_count = len(ticket_numbers & winning_numbers)
        is_bonus_matched = bonus_number in ticket_numbers

        if matched_count == 6:
            results['1등_당첨자_수'] += 1
        elif matched_count == 5 and is_bonus_matched:
            results['2등_당첨자_수'] += 1
        elif matched_count == 5:
            results['3등_당첨자_수'] += 1
        elif matched_count == 4:
            results['4등_당첨자_수'] += 1
        elif matched_count == 3:
            results['5등_당첨자_수'] += 1
        else:
            results['낙첨자_수'] += 1

    results['전체_티켓_수'] = LottoTicket.objects.count()

    return render(request, 'stats.html', {
        'results': results,
        'winning_numbers': winning.numbers,
        'bonus_number': bonus_number
    })


# 구매 내역 뷰
def my_tickets(request):
    if request.user.is_authenticated:
        tickets = LottoTicket.objects.filter(user=request.user).order_by('purchased_at')
    else:
        tickets = LottoTicket.objects.filter(user=None).order_by('purchased_at')

    ticket_data = []
    for idx, ticket in enumerate(tickets, start=1):
        ticket_data.append({
            'ticket_number': idx,
            'numbers': ticket.numbers,
        })

    return render(request, 'my_tickets.html', {
        'ticket_data': ticket_data,
    })


# 관리자용 판매 상태 변경 뷰
@staff_member_required
def toggle_sales(request):
    settings = LottoSettings.objects.first()
    if not settings:
        settings = LottoSettings.objects.create(is_sales_open=True)
    settings.is_sales_open = not settings.is_sales_open
    settings.save()

    return render(request, 'toggle_sales.html', {'is_sales_open': settings.is_sales_open})


# 관리자용 판매 요약 뷰
@staff_member_required
def sales_summary(request):
    tickets = LottoTicket.objects.all()
    ticket_count = tickets.count()
    ticket_price = 5000
    total_sales = ticket_count * ticket_price

    return render(request, 'sales_summary.html', {
        'ticket_count': ticket_count,
        'total_sales': total_sales,
    })
