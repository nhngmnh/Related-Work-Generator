# modules/preprocessing/chunker.py
def chunk_text(text: str, max_tokens: int = 200):
    """Chunk text into smaller windows"""
    sentences = text.split(". ")
    chunks, current = [], ""

    for s in sentences:
        if len(current) + len(s) < max_tokens:
            current += s + ". "
        else:
            chunks.append(current.strip())
            current = s + ". "
    if current:
        chunks.append(current.strip())

    return chunks
