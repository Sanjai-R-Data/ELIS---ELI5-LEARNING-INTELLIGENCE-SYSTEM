from dataclasses import dataclass
@dataclass
class SourceSegment:
    """
    Represents a piece of source material extracted from
    the student's uploaded educational document.
    """

    chunk_id: int
    page: int
    text: str
def create_source_segments(
    pages: list[dict],
    chunk_size: int = 1000,
    overlap: int = 150,
) -> list[SourceSegment]:
    """
    Convert page-level extracted text into structured source segments.

    Each segment preserves:
    - chunk ID
    - source page
    - chunk text
    """
    from backend.content.chunker import create_chunks

    segments = []
    chunk_id = 1

    for page_data in pages:
        page_number = page_data["page"]
        page_text = page_data["text"]

        chunks = create_chunks(
            page_text,
            chunk_size=chunk_size,
            overlap=overlap,
        )

        for chunk in chunks:
            segments.append(
                SourceSegment(
                    chunk_id=chunk_id,
                    page=page_number,
                    text=chunk,
                )
            )

            chunk_id += 1

    return segments