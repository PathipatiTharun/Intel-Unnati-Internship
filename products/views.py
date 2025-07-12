# products/views.py
from django.shortcuts import render, redirect
from .forms import ProductForm, OCRImageForm
from .models import Product
from django.urls import reverse
from django.conf import settings
from django.core.files.storage import default_storage
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import os
import re
import cv2
import numpy as np
from .ocr_utils import (
    enhance_image_quality, deskew_image, remove_background_noise,
    validate_serial_number, extract_multiple_serials, get_ocr_confidence_score
)

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image(image_path):
    """
    Preprocess image to improve OCR accuracy using advanced techniques
    """
    # Read image using OpenCV
    img = cv2.imread(image_path)
    if img is None:
        return None
    
    processed_images = []
    
    # 1. Original image (for comparison)
    processed_images.append(img)
    
    # 2. Deskew image to correct rotation
    deskewed = deskew_image(img)
    processed_images.append(deskewed)
    
    # 3. Remove background noise
    denoised = remove_background_noise(img)
    processed_images.append(denoised)
    
    # 4. Enhanced image quality techniques
    enhanced_images = enhance_image_quality(img)
    processed_images.extend(enhanced_images)
    
    # 5. Resize if too large (maintain aspect ratio)
    for i, img in enumerate(processed_images):
        height, width = img.shape[:2]
        if width > 2000:
            scale = 2000 / width
            new_width = int(width * scale)
            new_height = int(height * scale)
            processed_images[i] = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    return processed_images

def extract_serial_number(text):
    """
    Extract serial number using advanced pattern matching and validation
    """
    # Extract multiple potential serial numbers
    serials = extract_multiple_serials(text)
    
    if serials:
        # Return the longest valid serial number (usually more complete)
        return max(serials, key=len)
    
    # Fallback: try to extract first word that looks like a serial number
    words = text.split()
    for word in words:
        word = re.sub(r'[^A-Za-z0-9]', '', word)  # Remove special characters
        if len(word) >= 6 and validate_serial_number(word):
            return word.upper()
    
    return None

def perform_ocr_with_config(image, config):
    """
    Perform OCR with specific configuration
    """
    try:
        text = pytesseract.image_to_string(image, config=config)
        return text.strip()
    except Exception as e:
        print(f"OCR error with config {config}: {e}")
        return ""

def add_product(request):
    ocr_result = None
    ocr_error = None
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            # Check if OCR image was uploaded
            ocr_image = form.cleaned_data.get('ocr_image')
            if ocr_image:
                try:
                    # Process OCR image
                    path = default_storage.save('tmp/' + ocr_image.name, ocr_image)
                    tmp_file = os.path.join(settings.MEDIA_ROOT, path)
                    
                    # Preprocess image
                    processed_images = preprocess_image(tmp_file)
                    
                    if processed_images is None:
                        raise ValueError("Could not load image")
                    
                    # OCR configurations to try
                    ocr_configs = [
                        '--oem 3 --psm 6',  # Default: LSTM OCR Engine + Uniform block of text
                        '--oem 3 --psm 8',  # Single word
                        '--oem 3 --psm 7',  # Single text line
                    ]
                    
                    best_serial = None
                    best_confidence = 0.0
                    
                    # Try OCR with different preprocessing and configurations
                    for processed_img in processed_images:
                        for config in ocr_configs:
                            text = perform_ocr_with_config(processed_img, config)
                            if text:
                                serial = extract_serial_number(text)
                                confidence = get_ocr_confidence_score(text, serial) if serial else 0.0
                                
                                if serial and confidence > best_confidence:
                                    best_serial = serial
                                    best_confidence = confidence
                    
                    # Update form with extracted serial number
                    if best_serial:
                        form.instance.serial_number = best_serial
                        ocr_result = f"✅ Serial number extracted: {best_serial} (Confidence: {best_confidence:.2f})"
                    else:
                        ocr_error = "❌ Could not extract serial number from image. Please enter manually."
                    
                    # Clean up temporary file
                    if os.path.exists(tmp_file):
                        os.remove(tmp_file)
                        
                except Exception as e:
                    ocr_error = f"❌ OCR processing error: {str(e)}"
            
            # Save the product
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    
    return render(request, 'products/product_form.html', {
        'form': form,
        'ocr_result': ocr_result,
        'ocr_error': ocr_error
    })

def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})

def delete_product(request, pk):
    product = Product.objects.get(pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'products/confirm_delete.html', {'product': product})

def ocr_search(request):
    result = None
    serial_number = None
    manual_result = None
    ocr_debug_info = None
    
    if request.method == 'POST':
        form = OCRImageForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = form.cleaned_data['image']
            path = default_storage.save('tmp/' + image_file.name, image_file)
            tmp_file = os.path.join(settings.MEDIA_ROOT, path)
            
            try:
                # Preprocess image
                processed_images = preprocess_image(tmp_file)
                
                if processed_images is None:
                    raise ValueError("Could not load image")
                
                # OCR configurations to try
                ocr_configs = [
                    '--oem 3 --psm 6',  # Default: LSTM OCR Engine + Uniform block of text
                    '--oem 3 --psm 8',  # Single word
                    '--oem 3 --psm 7',  # Single text line
                    '--oem 1 --psm 6',  # Legacy engine + Uniform block
                    '--oem 3 --psm 13', # Raw line
                ]
                
                best_text = ""
                best_serial = None
                best_confidence = 0.0
                debug_info = []
                
                # Try OCR with different preprocessing and configurations
                for i, processed_img in enumerate(processed_images):
                    for j, config in enumerate(ocr_configs):
                        text = perform_ocr_with_config(processed_img, config)
                        if text:
                            serial = extract_serial_number(text)
                            confidence = get_ocr_confidence_score(text, serial) if serial else 0.0
                            
                            debug_info.append({
                                'preprocessing': f'Method {i+1}',
                                'config': config,
                                'raw_text': text[:100] + '...' if len(text) > 100 else text,
                                'extracted_serial': serial,
                                'confidence': f'{confidence:.2f}'
                            })
                            
                            # Choose best result based on confidence and length
                            if serial and (best_serial is None or confidence > best_confidence):
                                best_text = text
                                best_serial = serial
                                best_confidence = confidence
                
                serial_number = best_serial
                ocr_debug_info = debug_info
                
                # Try to find product with extracted serial number
                if serial_number:
                    try:
                        product = Product.objects.get(serial_number=serial_number)
                        result = product
                    except Product.DoesNotExist:
                        # Try partial matching
                        similar_products = Product.objects.filter(
                            serial_number__icontains=serial_number[:6]
                        )
                        if similar_products.exists():
                            result = similar_products.first()
                
            except Exception as e:
                print(f"OCR processing error: {e}")
                ocr_debug_info = [{'error': str(e)}]
            finally:
                # Clean up temporary file
                if os.path.exists(tmp_file):
                    os.remove(tmp_file)
    else:
        form = OCRImageForm()
    
    # Manual search
    manual_serial = request.GET.get('manual_serial')
    if manual_serial:
        try:
            manual_result = Product.objects.get(serial_number=manual_serial)
        except Product.DoesNotExist:
            manual_result = None
    
    return render(request, 'products/ocr_search.html', {
        'form': form,
        'result': result,
        'serial_number': serial_number,
        'manual_result': manual_result,
        'ocr_debug_info': ocr_debug_info
    })
