from PIL import Image
import pytesseract
import pdfplumber

def extract_text_from_pdf(pdf_v_path):
    text = ""
    with pdfplumber.open(pdf_v_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
    return text

pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'

def extract_text_from_image(image_path):
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang='deu')
        return text
    except Exception as e:
        return f"Ошибка при обработке {image_path}: {e}"