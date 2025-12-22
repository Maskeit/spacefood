import pytesseract
from pdf2image import convert_from_path
import cv2
import numpy as np
import os
from pathlib import Path

# install with brew Tesseract or Poppler

def ocr_pdf(pdf_path):
    """
    Performs OCR on a PDF file and returns the extracted text.
    """
    # Convert PDF pages to a list of images
    pages = convert_from_path(pdf_path) #, poppler_path=POPPLER_PATH) # Use poppler_path if needed

    extracted_text = ""
    for page_num, page in enumerate(pages):
        # Optional: Image preprocessing for better accuracy (convert to grayscale)
        page_arr = np.array(page)
        gray_image = cv2.cvtColor(page_arr, cv2.COLOR_BGR2GRAY)
        
        # Perform OCR on the image
        text = pytesseract.image_to_string(gray_image)
        extracted_text += f"\n--- Page {page_num + 1} ---\n"
        extracted_text += text

    return extracted_text

def save_ocr_result(pdf_path, text_result, output_dir='data_result/2020'):
    """
    Saves the OCR result to a text file in the specified output directory.
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Get the filename without extension
    filename = os.path.splitext(os.path.basename(pdf_path))[0]
    output_path = os.path.join(output_dir, f'{filename}.txt')
    
    # Save the text result
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text_result)
    
    return output_path

# Usage
pdf_file_path = '/Users/alejandre/Developer/jatenx/spacefood/app/data/2020/4436.pdf'
text_result = ocr_pdf(pdf_file_path)
saved_path = save_ocr_result(pdf_file_path, text_result)
print(f"OCR result saved to: {saved_path}")