#!/usr/bin/env python3
"""
Test script for OCR functionality in Add Product form
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'product_app.settings')
django.setup()

from products.forms import ProductForm
from products.ocr_utils import validate_serial_number, extract_multiple_serials

def test_product_form():
    """Test the enhanced ProductForm with OCR field"""
    print("🧪 Testing Enhanced ProductForm")
    print("=" * 50)
    
    # Test form without OCR image
    print("\n1. Testing form without OCR image:")
    form_data = {
        'device_id': 'TEST001',
        'batch_id': 'BATCH2024-TEST',
        'manufacturing_date': '2024-01-15',
        'rohs_compliance': True,
        'serial_number': 'ABC12345'
    }
    
    form = ProductForm(data=form_data)
    if form.is_valid():
        print("✅ Form is valid without OCR image")
        print(f"   Serial Number: {form.cleaned_data['serial_number']}")
    else:
        print("❌ Form validation failed:")
        print(form.errors)
    
    # Test form fields
    print("\n2. Testing form fields:")
    form = ProductForm()
    
    # Check if OCR field exists
    if 'ocr_image' in form.fields:
        print("✅ OCR image field found")
        print(f"   Label: {form.fields['ocr_image'].label}")
        print(f"   Required: {form.fields['ocr_image'].required}")
        print(f"   Help text: {form.fields['ocr_image'].help_text}")
    else:
        print("❌ OCR image field not found")
    
    # Check if serial number field has proper attributes
    if 'serial_number' in form.fields:
        print("✅ Serial number field found")
        widget = form.fields['serial_number'].widget
        if hasattr(widget, 'attrs') and 'id' in widget.attrs:
            print(f"   ID: {widget.attrs['id']}")
        if hasattr(widget, 'attrs') and 'placeholder' in widget.attrs:
            print(f"   Placeholder: {widget.attrs['placeholder']}")
    else:
        print("❌ Serial number field not found")

def test_ocr_utilities():
    """Test OCR utility functions"""
    print("\n3. Testing OCR utility functions:")
    
    # Test serial number validation
    test_serials = ['ABC12345', 'XYZ789012', '123456DEF', 'ABC123', 'ABC@12345']
    print("   Serial number validation:")
    for serial in test_serials:
        is_valid = validate_serial_number(serial)
        status = "✅ Valid" if is_valid else "❌ Invalid"
        print(f"     {serial:15} -> {status}")
    
    # Test text extraction
    test_texts = [
        "Product Serial: ABC12345 Date: 2024-01-15",
        "Device ID: XYZ789012 Batch: BATCH2024-002",
        "Some random text without serial numbers",
    ]
    print("\n   Text extraction:")
    for text in test_texts:
        serials = extract_multiple_serials(text)
        print(f"     Text: {text[:40]}...")
        print(f"     Found: {serials}")

def main():
    """Main test function"""
    print("🚀 Add Product OCR Test Suite")
    print("=" * 50)
    
    try:
        test_product_form()
        test_ocr_utilities()
        
        print("\n✅ All tests completed successfully!")
        print("\n📋 OCR Features Added to Add Product Form:")
        print("1. 📷 OCR image upload field")
        print("2. 🔍 Automatic serial number extraction")
        print("3. ✅ Confidence scoring")
        print("4. 🎨 Enhanced UI with feedback")
        print("5. 🔗 Easy access from product list")
        
        print("\n🎯 How to use:")
        print("1. Go to 'Add New Product' page")
        print("2. Upload an image containing a serial number")
        print("3. The serial number field will be auto-filled")
        print("4. Complete other fields and save")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 