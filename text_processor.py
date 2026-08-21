import re
def clean_text(text: str) -> str:
    """
    Clean extracted PDF text while preserving meaningful
    paragraph structure.
    """

    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.strip() for line in text.split("\n")]
    cleaned_lines = []
    for line in lines:
        line = re.sub(r"[ \t]+", " ", line)
        cleaned_lines.append(line)
    cleaned_text = "\n".join(cleaned_lines)
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)
    cleaned_text = re.sub(r"\s+([,.!?;:])", r"\1", cleaned_text)

    return cleaned_text.strip()