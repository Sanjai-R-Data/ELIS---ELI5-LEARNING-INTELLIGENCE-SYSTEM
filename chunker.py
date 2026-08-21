import re
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 150
def _split_into_sentences(text: str) -> list[str]:
    """
    Split text into sentences while preserving sentence content.

    Common sentence-ending punctuation is used to identify
    sentence boundaries.
    """
    text = text.strip()

    if not text:
        return []

    sentence_pattern = re.compile(
        r".+?(?:[.!?](?=\s|$)|$)",
        re.DOTALL,
    )
    sentences = []

    for match in sentence_pattern.finditer(text):
        sentence = match.group().strip()
        sentence = re.sub(r"\s+", " ", sentence)

        if sentence:
            sentences.append(sentence)

    return sentences
def _trim_to_word_boundary(text: str, max_length: int) -> str:
    """
    Keep the trailing `max_length` characters of `text`, then trim
    forward to the next word boundary so a word isn't cut in half.
    """

    if len(text) <= max_length:
        return text
    tail = text[-max_length:]
    space_index = tail.find(" ")

    if space_index == -1:
        return tail

    return tail[space_index + 1:]
def create_chunks(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    """
    Split educational text into semantically meaningful chunks.

    The chunker prioritizes:

    1. Complete sentences
    2. Natural source boundaries
    3. Word boundaries
    4. Approximate chunk size
    5. Sentence-level overlap

    A sentence that is itself longer than chunk_size is kept intact
    rather than being split in the middle.

    Args:
        text: Cleaned source text.
        chunk_size: Target size of each chunk in characters.
        overlap: Approximate overlap between chunks.

    Returns:
        A list of text chunks.
    """

    if not text or not text.strip():
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if overlap < 0:
        raise ValueError("overlap cannot be negative.")

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size.")

    sentences = _split_into_sentences(text)

    if not sentences:
        return []

    chunks = []

    current_sentences = []
    current_length = 0

    for sentence in sentences:
        sentence_length = len(sentence)

        if not current_sentences:
            current_sentences = [sentence]
            current_length = sentence_length
            continue

        proposed_length = current_length + 1 + sentence_length

        if proposed_length <= chunk_size:
            current_sentences.append(sentence)
            current_length = proposed_length
            continue

        chunks.append(" ".join(current_sentences))
        overlap_sentences = []
        overlap_length = 0

        for previous_sentence in reversed(current_sentences):
            additional_length = len(previous_sentence)
            if overlap_sentences:
                additional_length += 1
            if (
                overlap_sentences
                and overlap_length + additional_length > overlap
            ):
                break
            overlap_sentences.insert(0, previous_sentence)
            overlap_length += additional_length

        if len(overlap_sentences) == 1 and overlap_length > overlap:
            overlap_sentences[0] = _trim_to_word_boundary(
                overlap_sentences[0], overlap
            )
            overlap_length = len(overlap_sentences[0])

        if sentence_length > chunk_size:
            chunks.append(sentence)
            current_sentences = []
            current_length = 0
            continue
        current_sentences = overlap_sentences + [sentence]
        current_length = sum(
            len(item) for item in current_sentences
        )
        if len(current_sentences) > 1:
            current_length += len(current_sentences) - 1
    if current_sentences:
        chunks.append(" ".join(current_sentences))
    return chunks

