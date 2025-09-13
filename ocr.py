#!/usr/bin/env python3
"""
OCR PDF Text Extraction Script
Extracts text elements from PDF and outputs as JSON
"""

import cv2
import pytesseract
import fitz  # PyMuPDF
import numpy as np
import os
import sys
import shutil
import json

# --- PDF & Tesseract Setup ---

# PDF path (CLI override)
file_path = sys.argv[1] if len(sys.argv) > 1 else "WhatsApp Image 2025-09-13 at 9.19.pdf"
if not os.path.isabs(file_path):
    file_path = os.path.abspath(file_path)

# Tesseract detection / override
if os.name == "nt":
    default_win = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
    pytesseract.pytesseract.tesseract_cmd = os.environ.get("TESSERACT_PATH", default_win)
else:
    candidates = [
        os.environ.get("TESSERACT_PATH"),
        shutil.which("tesseract"),
        "/usr/bin/tesseract",
        "/usr/local/bin/tesseract",
    ]
    candidates = [c for c in candidates if c]
    for cand in candidates:
        if cand and (os.path.isfile(cand) or shutil.which(cand)):
            pytesseract.pytesseract.tesseract_cmd = cand
            break
    else:
        print("Error: tesseract not found. Install: sudo apt install -y tesseract-ocr")
        print("Or export TESSERACT_PATH=/path/to/tesseract")
        sys.exit(1)

print(f"Using tesseract at: {pytesseract.pytesseract.tesseract_cmd}")
print(f"Opening PDF: {file_path}")

# Open PDF and extract text elements
try:
    pdf_document = fitz.open(file_path)
except Exception as e:
    print(f"Error opening PDF file: {e}")
    print("Please make sure the file path is correct.")
    sys.exit(1)

# Process first page (can be extended for multiple pages)
page = pdf_document[0]
# Using a moderate DPI for good balance between accuracy and performance
pix = page.get_pixmap(dpi=200) 
base_img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3).copy()
rgb_img_for_ocr = cv2.cvtColor(base_img, cv2.COLOR_BGR2RGB)

# Perform OCR and get detailed word data
word_data = pytesseract.image_to_data(rgb_img_for_ocr, output_type=pytesseract.Output.DICT)

# Process and structure the OCR results
pdf_elements = []
for i in range(len(word_data['text'])):
    # Only include text with reasonable confidence
    if int(word_data['conf'][i]) > 60 and word_data['text'][i].strip():
        element = {
            "text": word_data['text'][i].strip(),
            "confidence": int(word_data['conf'][i]),
            "bounding_box": {
                "left": int(word_data['left'][i]),
                "top": int(word_data['top'][i]),
                "width": int(word_data['width'][i]),
                "height": int(word_data['height'][i])
            },
            "page_number": int(word_data['page_num'][i]),
            "block_number": int(word_data['block_num'][i]),
            "paragraph_number": int(word_data['par_num'][i]),
            "line_number": int(word_data['line_num'][i]),
            "word_number": int(word_data['word_num'][i])
        }
        pdf_elements.append(element)

# Create final JSON structure
result = {
    "source_file": file_path,
    "page_count": len(pdf_document),
    "processed_page": 0,
    "image_dimensions": {
        "width": base_img.shape[1],
        "height": base_img.shape[0]
    },
    "total_elements": len(pdf_elements),
    "elements": pdf_elements
}

# Break if no elements found
if result["total_elements"] == 0:
    print("NOT VERIFIED!")
    pdf_document.close()
    sys.exit(0)
'''
# Output JSON
print("\n" + "="*50)
print("PDF OCR RESULTS (JSON)")
print("="*50)
print(json.dumps(result, indent=2, ensure_ascii=False))'''
print("VERIFIED!!")
# Optionally save to file
output_file = f"{os.path.splitext(file_path)[0]}_ocr_results.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"\nResults also saved to: {output_file}")
pdf_document.close()
