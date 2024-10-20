from django import forms
from .models import Receipt

class ReceiptUploadForm(forms.ModelForm):
    class Meta:
        model = Receipt  # Bind the form to the Receipt model
        fields = ['image_path']  # Only allow image uploads
        widgets = {
            'image_path': forms.ClearableFileInput(attrs={'accept': 'image/*,application/pdf'})
        }
