# modules/preprocessing/extractor.py
def reconstruct_abstract(index_dict):
    """Rebuild abstract text from OpenAlex inverted index"""
    if not index_dict:
        return ""
    try:
        length = max(pos for positions in index_dict.values() for pos in positions) + 1
        words = [""] * length
        for word, positions in index_dict.items():
            for pos in positions:
                words[pos] = word
        return " ".join(words).strip()
    except Exception:
        return ""

def clean_text(text: str) -> str:
    """Basic cleanup"""
    return (
        text.replace("\n", " ")
            .replace("\t", " ")
            .replace("  ", " ")
            .strip()
    )
