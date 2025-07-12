# products/ocr_utils.py
import cv2
import numpy as np
import re
from typing import List, Optional, Tuple

def enhance_image_quality(image: np.ndarray) -> List[np.ndarray]:
    """
    Apply advanced image enhancement techniques for better OCR, especially for camera images
    """
    enhanced_images = []
    
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # 1. Noise reduction with bilateral filter
    denoised = cv2.bilateralFilter(gray, 9, 75, 75)
    enhanced_images.append(denoised)

    # 2. Sharpening
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(gray, -1, kernel)
    enhanced_images.append(sharpened)

    # 3. Contrast enhancement with CLAHE
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    enhanced_images.append(enhanced)

    # 4. Adaptive histogram equalization
    clahe_strong = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(8, 8))
    enhanced_strong = clahe_strong.apply(gray)
    enhanced_images.append(enhanced_strong)

    # 5. Edge enhancement
    edges = cv2.Canny(gray, 50, 150)
    edge_enhanced = cv2.addWeighted(gray, 0.7, edges, 0.3, 0)
    enhanced_images.append(edge_enhanced)

    # 6. Adaptive thresholding (good for uneven lighting)
    adaptive_thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY, 31, 10)
    enhanced_images.append(adaptive_thresh)

    # 7. Otsu's thresholding
    _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    enhanced_images.append(otsu)

    # 8. More aggressive denoising (fastNlMeansDenoising)
    denoised2 = cv2.fastNlMeansDenoising(gray, None, 30, 7, 21)
    enhanced_images.append(denoised2)

    # 9. Brightness/contrast adjustment
    for alpha in [1.2, 1.5]:  # Contrast
        for beta in [10, 30]:  # Brightness
            bright = cv2.convertScaleAbs(gray, alpha=alpha, beta=beta)
            enhanced_images.append(bright)

    # 10. Resize to standard DPI (300dpi for OCR, if image is large enough)
    h, w = gray.shape[:2]
    if w < 1000:
        scale = 1000 / w
        resized = cv2.resize(gray, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_CUBIC)
        enhanced_images.append(resized)

    # 11. Gaussian blur (can help with some noisy images)
    gaussian = cv2.GaussianBlur(gray, (5, 5), 0)
    enhanced_images.append(gaussian)

    # 12. Median blur (removes salt-and-pepper noise)
    median = cv2.medianBlur(gray, 3)
    enhanced_images.append(median)

    # 13. More aggressive adaptive thresholding
    adaptive_thresh2 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                             cv2.THRESH_BINARY, 15, 8)
    enhanced_images.append(adaptive_thresh2)

    # 14. Invert (for white text on black background)
    inverted = cv2.bitwise_not(gray)
    enhanced_images.append(inverted)

    # Remove duplicates (by hash)
    import hashlib
    def img_hash(img):
        return hashlib.md5(img.tobytes()).hexdigest()
    unique = {}
    for img in enhanced_images:
        h = img_hash(img)
        if h not in unique:
            unique[h] = img
    return list(unique.values())

def deskew_image(image: np.ndarray) -> np.ndarray:
    """
    Deskew image to correct rotation
    """
    # Convert to binary
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    
    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return image
    
    # Find the largest contour (assumed to be the main text area)
    largest_contour = max(contours, key=cv2.contourArea)
    
    # Get the minimum area rectangle
    rect = cv2.minAreaRect(largest_contour)
    angle = rect[2]
    
    # Correct angle
    if angle < -45:
        angle = 90 + angle
    
    # Rotate image
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    
    return rotated

def remove_background_noise(image: np.ndarray) -> np.ndarray:
    """
    Remove background noise and improve text clarity
    """
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    
    # Apply morphological operations to remove noise
    kernel = np.ones((2, 2), np.uint8)
    
    # Opening to remove small noise
    opening = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
    
    # Closing to fill small holes
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
    
    return closing

def validate_serial_number(serial: str) -> bool:
    """
    Validate if the extracted text looks like a valid serial number
    """
    if not serial or len(serial) < 4:
        return False
    
    # Remove common OCR artifacts
    cleaned = re.sub(r'[^A-Za-z0-9]', '', serial)
    
    if len(cleaned) < 4:
        return False
    
    # Check for common patterns
    patterns = [
        r'^[A-Z]{2,4}\d{4,8}$',  # Letters followed by numbers
        r'^\d{4,8}[A-Z]{2,4}$',  # Numbers followed by letters
        r'^[A-Z0-9]{6,12}$',     # Alphanumeric
        r'^\d{6,12}$',           # Pure numeric
    ]
    
    for pattern in patterns:
        if re.match(pattern, cleaned, re.IGNORECASE):
            return True
    
    return False

def extract_multiple_serials(text: str) -> List[str]:
    """
    Extract multiple potential serial numbers from text
    """
    # Clean text
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Common serial number patterns
    patterns = [
        r'\b[A-Z]{2,4}\d{4,8}\b',
        r'\b\d{4,8}[A-Z]{2,4}\b',
        r'\b[A-Z0-9]{6,12}\b',
        r'\b\d{6,12}\b',
        r'\b[A-Z]{2}\d{6}\b',
        r'\b\d{6}[A-Z]{2}\b',
    ]
    
    found_serials = []
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if validate_serial_number(match):
                found_serials.append(match.upper())
    
    # Remove duplicates while preserving order
    unique_serials = []
    for serial in found_serials:
        if serial not in unique_serials:
            unique_serials.append(serial)
    
    return unique_serials

def get_ocr_confidence_score(text: str, serial: str) -> float:
    """
    Calculate a confidence score for OCR results
    """
    if not text or not serial:
        return 0.0
    
    score = 0.0
    
    # Length score (longer serials are more likely to be correct)
    length_score = min(len(serial) / 10.0, 1.0)
    score += length_score * 0.3
    
    # Pattern validation score
    if validate_serial_number(serial):
        score += 0.4
    
    # Text quality score (less special characters = better)
    special_chars = len(re.findall(r'[^A-Za-z0-9\s]', text))
    text_length = len(text)
    if text_length > 0:
        quality_score = 1.0 - (special_chars / text_length)
        score += quality_score * 0.3
    
    return min(score, 1.0) 