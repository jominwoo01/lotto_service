from django.urls import path
from django.contrib.auth import views as auth_views  # Django 내장 인증 뷰 사용
from lotto import views

urlpatterns = [
    # 일반 사용자 및 관리자 공용
    path('', views.home, name='home'),  # 홈 페이지
    path('buy/', views.buy_lotto, name='buy_lotto'),  # 로또 구매
    path('buy/complete/<int:ticket_id>/', views.buy_complete, name='buy_complete'),  # 구매 완료
    path('results/', views.check_results, name='check_results'),  # 결과 확인
    path('my-tickets/', views.my_tickets, name='my_tickets'),  # 구매 내역 보기
    path('stats/', views.stats, name='stats'),  # 통계 페이지

    # 관리자 전용
    path('draw/', views.draw_winning_numbers, name='draw_winning_numbers'),  # 당첨 번호 추첨
    path('toggle-sales/', views.toggle_sales, name='toggle_sales'),  # 판매 상태 변경
    path('sales-summary/', views.sales_summary, name='sales_summary'),  # 판매 요약

    # 권한이 없을 때 표시할 페이지
    path('not-authorized/', views.admin_only_view, name='not_authorized'),  # 관리자 권한 부족 시 리디렉션

    # 로그인 및 로그아웃
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),  # 로그아웃 추가
]