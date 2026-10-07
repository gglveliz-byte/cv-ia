import os
import pdfplumber

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extrae el contenido de texto completo de un CV en formato PDF."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"No se encontró el archivo de CV en: {pdf_path}")
    
    text_content = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            if page_text:
                text_content.append(page_text)
                
    return "\n\n".join(text_content).strip()
