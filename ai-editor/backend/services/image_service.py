"""
Image processing service using Pillow and OpenCV.
Handles both manual adjustments and AI-driven operations.
"""
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import cv2
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# ── Manual adjustments ──
def apply_adjustments(input_path: str, output_path: str, settings: dict) -> str:
    """
    settings keys: brightness, contrast, saturation, sharpness, exposure, noise_reduction
    All values: float, default 1.0 (no change). brightness >1 = brighter.
    """
    img = Image.open(input_path).convert("RGB")

    if b := settings.get("brightness", 1.0):
        img = ImageEnhance.Brightness(img).enhance(b)
    if c := settings.get("contrast", 1.0):
        img = ImageEnhance.Contrast(img).enhance(c)
    if s := settings.get("saturation", 1.0):
        img = ImageEnhance.Color(img).enhance(s)
    if sh := settings.get("sharpness", 1.0):
        img = ImageEnhance.Sharpness(img).enhance(sh)
    if settings.get("noise_reduction", False):
        arr = np.array(img)
        arr = cv2.fastNlMeansDenoisingColored(arr, None, 10, 10, 7, 21)
        img = Image.fromarray(arr)

    img.save(output_path, quality=95)
    return output_path

def remove_background(input_path: str, output_path: str) -> str:
    """Simplified BG removal using GrabCut (replace with rembg for production)."""
    img = cv2.imread(input_path)
    mask = np.zeros(img.shape[:2], np.uint8)
    bgdModel = np.zeros((1, 65), np.float64)
    fgdModel = np.zeros((1, 65), np.float64)
    h, w = img.shape[:2]
    rect = (10, 10, w - 20, h - 20)
    cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype("uint8")
    img_rgba = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    img_rgba[:, :, 3] = mask2 * 255
    cv2.imwrite(output_path.replace(".jpg", ".png"), img_rgba)
    return output_path.replace(".jpg", ".png")

def apply_blur(input_path: str, output_path: str, radius: float = 5.0) -> str:
    img = Image.open(input_path)
    img = img.filter(ImageFilter.GaussianBlur(radius=radius))
    img.save(output_path)
    return output_path

def generate_thumbnail(input_path: str, thumb_path: str, size: tuple = (400, 300)) -> str:
    img = Image.open(input_path)
    img.thumbnail(size, Image.LANCZOS)
    img.save(thumb_path)
    return thumb_path

def detect_faces(input_path: str) -> list:
    """Returns list of face bounding boxes."""
    img = cv2.imread(input_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    return [{"x": int(x), "y": int(y), "w": int(w), "h": int(h)} for x, y, w, h in faces]

def ai_auto_enhance(input_path: str, output_path: str) -> dict:
    """One-click AI enhancement: auto brightness, contrast, sharpening."""
    img = Image.open(input_path).convert("RGB")
    arr = np.array(img)
    # CLAHE on L channel
    lab = cv2.cvtColor(arr, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    enhanced = cv2.merge((l, a, b))
    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)
    result = Image.fromarray(enhanced)
    result = ImageEnhance.Sharpness(result).enhance(1.3)
    result.save(output_path, quality=95)
    faces = detect_faces(input_path)
    return {"faces_detected": len(faces), "face_regions": faces}
