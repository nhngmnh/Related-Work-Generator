# modules/embeddings/embedder.py
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-mpnet-base-v2")

def embed_text(text: str):
    return model.encode(text)
