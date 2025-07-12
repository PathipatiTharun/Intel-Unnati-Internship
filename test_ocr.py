#!/usr/bin/env python3
"""
Test script for OCR enhancements
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'product_app.settings')
django.setup()

from products.models import Product
from products.ocr_utils import (
    validate_serial_number, 
    extract_multiple_serials, 
    get_ocr_confidence_score
)
from datetime import date

def create_test_products():
    """Create test products for OCR testing"""
    test_products = [
        {
            'device_id': 'DEV001',
            'batch_id': 'BATCH2024-001',
            'manufacturing_date': date(2024, 1, 15),
            'rohs_compliance': True,
            'serial_number': 'ABC12345'
        },
        {
            'device_id': 'DEV002',
            'batch_id': 'BATCH2024-002',
            'manufacturing_date': date(2024, 2, 20),
            'rohs_compliance': False,
            'serial_number': 'XYZ789012'
        },
        {
            'device_id': 'DEV003',
            'batch_id': 'BATCH2024-003',
            'manufacturing_date': date(2024, 3, 10),
            'rohs_compliance': True,
            'serial_number': '123456DEF'
        }
    ]
    
    for product_data in test_products:
        Product.objects.get_or_create(
            serial_number=product_data['serial_number'],
            defaults=product_data
        )
    
    print("✅ Test products created successfully!")

def test_serial_validation():
    """Test serial number validation"""
    print("\n🔍 Testing Serial Number Validation:")
    
    test_serials = [
        'ABC12345',      # Valid
        'XYZ789012',     # Valid
        '123456DEF',     # Valid
        'ABC123',        # Too short
        'ABC123456789',  # Too long
        'ABC@12345',     # Invalid characters
        'ABC 12345',     # Contains space
        '',              # Empty
    ]
    
    for serial in test_serials:
        is_valid = validate_serial_number(serial)
        status = "✅ Valid" if is_valid else "❌ Invalid"
        print(f"  {serial:15} -> {status}")

def test_text_extraction():
    """Test text extraction from OCR output"""
    print("\n📝 Testing Text Extraction:")
    
    test_texts = [
        "Product Serial: ABC12345 Date: 2024-01-15",
        "Device ID: XYZ789012 Batch: BATCH2024-002",
        "Serial Number: 123456DEF RoHS: Yes",
        "Some random text without serial numbers",
        "Multiple serials: ABC12345 and XYZ789012",
    ]
    
    for text in test_texts:
        serials = extract_multiple_serials(text)
        print(f"  Text: {text[:50]}...")
        print(f"  Found: {serials}")
        print()

def test_confidence_scoring():
    """Test confidence scoring"""
    print("\n📊 Testing Confidence Scoring:")
    
    test_cases = [
        ("Clean text: ABC12345", "ABC12345"),
        ("Noisy text: A@B#C12345", "ABC12345"),
        ("Short text: ABC123", "ABC123"),
        ("Long text: ABC123456789", "ABC123456789"),
    ]
    
    for text, serial in test_cases:
        confidence = get_ocr_confidence_score(text, serial)
        print(f"  Text: {text}")
        print(f"  Serial: {serial}")
        print(f"  Confidence: {confidence:.2f}")
        print()

def main():
    """Main test function"""
    print("🚀 OCR Enhancement Test Suite")
    print("=" * 50)
    
    try:
        # Create test products
        create_test_products()
        
        # Run tests
        test_serial_validation()
        test_text_extraction()
        test_confidence_scoring()
        
        print("\n✅ All tests completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Install Tesseract OCR if not already installed")
        print("2. Install Python dependencies: pip install -r requirements.txt")
        print("3. Run Django server: python manage.py runserver")
        print("4. Test OCR functionality at: http://localhost:8000/ocr-search/")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 