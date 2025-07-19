from pdf2image import convert_from_path
import pytesseract
from docx import Document
import os

def extract_text_from_file(file_path):
    text = ""
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.pdf':
        images = convert_from_path(file_path)
        for image in images:
            text += pytesseract.image_to_string(image)
    elif file_ext == '.docx':
        doc = Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    elif file_ext == '.txt':
        with open(file_path, 'r') as f:
            text = f.read()
    return text

def preprocess_resume_text(text):
    text = ' '.join(text.split())
    return text
