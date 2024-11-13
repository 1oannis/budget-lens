from django import forms
from .models import Expense

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['receipt_image', 'category', 'expense_date', 'amount', 'currency']
        widgets = {
            'category': forms.TextInput(attrs={'required': False}),
            'expense_date': forms.DateInput(attrs={'required': False}),
            'amount': forms.NumberInput(attrs={'required': False}),
            'currency': forms.TextInput(attrs={'required': False}),
        }
