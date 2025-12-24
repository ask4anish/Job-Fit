import re
from pdfminer.high_level import extract_text

def extract_text_from_pdf(pdf_path):
    """
    Extracts raw text from a PDF file using pdfminer.six.
    """
    try:
        text = extract_text(pdf_path)
        return text
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""

def clean_text(text):
    """
    Cleans the extracted text by removing excessive whitespace and newlines.
    """
    if not text:
        return ""
    
    # Replace multiple newlines/tabs/spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

if __name__ == "__main__":
    # Test with a dummy file if needed
    pass
