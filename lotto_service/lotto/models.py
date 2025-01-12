from django.db import models
from django.contrib.auth.models import User

class LottoTicket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # NULL 허용
    numbers = models.CharField(max_length=20)
    purchased_at = models.DateTimeField(auto_now_add=True)

class WinningNumber(models.Model):
    numbers = models.CharField(max_length=20)  # 당첨 번호 (쉼표로 구분된 문자열)
    bonus_number = models.IntegerField()  # 보너스 번호 (1~45 중 하나)
    drawn_at = models.DateTimeField(auto_now_add=True)  # 추첨 시간

class LottoSettings(models.Model):
    is_sales_open = models.BooleanField(default=True)