from PyPDF2 import PdfReader
from docx import Document
import os

def extract_text(file_path):
    """
    Extracts text from a PDF or DOCX file.

    Args:
        file_path (str): The path to the uploaded file.

    Returns:
        str: Extracted text from the document.

    Raises:
        ValueError: If the file format is unsupported or no text could be extracted.
    """
    _, ext = os.path.splitext(file_path.lower())

    if ext == ".pdf":
        reader = PdfReader(file_path)
        text = "\n".join([page.extract_text() or "" for page in reader.pages])

    elif ext == ".docx":
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])

    else:
        raise ValueError("Unsupported file format. Please upload a PDF or DOCX.")

    cleaned = text.strip()

    if not cleaned:
        raise ValueError("No readable text could be extracted from the document.")

    return cleaned
