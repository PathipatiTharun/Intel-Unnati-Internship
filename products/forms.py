# products/forms.py
from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    # OCR field for scanning serial numbers
    ocr_image = forms.ImageField(
        required=False,
        label="📷 Scan Serial Number (Optional)",
        help_text="Upload an image containing the serial number to auto-fill the field"
    )
    
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'serial_number': forms.TextInput(attrs={
                'placeholder': 'Enter or scan serial number',
                'id': 'serial_number_field'
            }),
            'device_id': forms.TextInput(attrs={
                'placeholder': 'e.g., DEV001, ABC123'
            }),
            'batch_id': forms.TextInput(attrs={
                'placeholder': 'e.g., BATCH2024-001'
            }),
            'manufacturing_date': forms.DateInput(attrs={
                'type': 'date'
            }),
        }

class OCRImageForm(forms.Form):
    image = forms.ImageField()
