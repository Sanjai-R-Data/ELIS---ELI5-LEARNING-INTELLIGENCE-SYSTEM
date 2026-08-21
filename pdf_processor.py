from pathlib import Path

from pypdf import PdfReader

def validate_pdf(file_path: str) -> bool:
    path = Path(file_path)
    if not path.exists():
        return False
    if not path.is_file():
        return False
    if path.suffix.lower() != ".pdf":
        return False
    return True

def extract_text(file_path: str) -> list[dict]:
    if not validate_pdf(file_path):
        raise ValueError("Invalid PDF file.")
    reader = PdfReader(file_path)
    pages = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append(
            {
                "page": page_number,
                "text": text,
            }
        )

    return pages