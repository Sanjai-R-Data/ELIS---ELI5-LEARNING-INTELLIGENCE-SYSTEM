from pathlib import Path
from pypdf import PdfReader


MAX_FILE_SIZE_MB = 20
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
MAX_PAGES = 100


def validate_pdf(file_path: str) -> dict:
    """
    Validate a PDF before sending it through
    the ELIS content-processing pipeline.

    Checks:
    - File exists
    - File extension is .pdf
    - File is not empty
    - File size is <= 20 MB
    - PDF can be opened
    - PDF contains at least one page
    - PDF contains <= 100 pages
    """

    path = Path(file_path)

    if not path.exists():
        raise ValueError(
            "PDF file does not exist."
        )
    if not path.is_file():
        raise ValueError(
            "The provided path is not a file."
        )
    if path.suffix.lower() != ".pdf":
        raise ValueError(
            "Only PDF files are allowed."
        )
    file_size = path.stat().st_size

    if file_size == 0:
        raise ValueError(
            "The PDF file is empty."
        )
    if file_size > MAX_FILE_SIZE_BYTES:
        raise ValueError(
            "PDF exceeds the maximum allowed "
            "file size of 20 MB."
        )
    try:
        reader = PdfReader(str(path))

        page_count = len(reader.pages)

    except Exception as error:
        raise ValueError(
            "The PDF could not be opened. "
            "It may be corrupted or invalid."
        ) from error
    if page_count == 0:
        raise ValueError(
            "The PDF does not contain any pages."
        )

    if page_count > MAX_PAGES:
        raise ValueError(
            "PDF exceeds the maximum allowed "
            "page limit of 100 pages."
        )
    size_mb = file_size / (
        1024 * 1024
    )

    return {
        "valid": True,
        "filename": path.name,
        "size_bytes": file_size,
        "size_mb": round(size_mb, 2),
        "pages": page_count,
        "max_size_mb": MAX_FILE_SIZE_MB,
        "max_pages": MAX_PAGES,
    }