from django.contrib import admin

from .models import Expense
from .models import Income
from .models import Token
from .models import Passwordresetcodes

# Register your models here.
admin.site.register(Expense)
admin.site.register(Income)
admin.site.register(Token)
admin.site.register(Passwordresetcodes)
