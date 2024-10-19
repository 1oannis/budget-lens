from django.contrib import admin
from .models import Account, Receipt, Expense

admin.site.register(Account)
admin.site.register(Receipt)
admin.site.register(Expense)
