from django import forms
from .models import Expense

class ExpenseForm(forms.ModelForm):
    """Form to upload an expense"""
    class Meta:
        model = Expense
        fields = ['receipt_image', 'category', 'expense_date', 'amount', 'currency']
        widgets = {
            'category': forms.TextInput(attrs={'required': False}),
            'expense_date': forms.DateInput(attrs={'required': False}),
            'amount': forms.NumberInput(attrs={'required': False}),
            'currency': forms.TextInput(attrs={'required': False}),
        }

class ExpenseEditForm(forms.ModelForm):
    """Form to edit an expense"""
    class Meta:
        model = Expense
        fields = ['category', 'expense_date', 'amount', 'currency']