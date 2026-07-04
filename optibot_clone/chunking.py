import re


def chunk_markdown(markdown: str, chunk_size: int, overlap: int) -> list[str]:
    if chunk_size <= overlap:
        raise ValueError("CHUNK_SIZE must be greater than CHUNK_OVERLAP.")

    sections = re.split(r"(?=^#{1,3} .*$)", markdown, flags=re.MULTILINE)
    chunks: list[str] = []

    for section in sections:
        section = section.strip()
        if not section:
            continue
        start = 0
        while start < len(section):
            end = min(start + chunk_size, len(section))
            chunk = section[start:end].strip()
            if chunk:
                chunks.append(chunk)
            if end == len(section):
                break
            start = max(0, end - overlap)

    return chunks
