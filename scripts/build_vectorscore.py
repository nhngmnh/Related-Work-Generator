# scripts/build_vectorstore.py
from modules.api.openAlex_client import search_openalex
from modules.preprocessing.chunker import chunk_text
from modules.embeddings.embedder import embed_text
from modules.embeddings.vector_db import save_chunk

KEYWORDS = [
    "machine learning",
    "evolutionary algorithms",
    "metaheuristic optimization"
]

def build_vectorstore():
    for kw in KEYWORDS:
        papers = search_openalex(kw, max_results=5)

        for p in papers:
            chunks = chunk_text(p["abstract"])

            for chunk in chunks:
                emb = embed_text(chunk)
                save_chunk(chunk, emb, metadata=p)

    print("Vectorstore build complete!")

if __name__ == "__main__":
    build_vectorstore()
