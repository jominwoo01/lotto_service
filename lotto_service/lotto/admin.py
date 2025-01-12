from django.contrib import admin
from .models import LottoTicket, WinningNumber, LottoSettings

admin.site.register(LottoTicket)
admin.site.register(WinningNumber)
admin.site.register(LottoSettings)
