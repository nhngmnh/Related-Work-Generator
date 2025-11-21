# modules/embeddings/vector_db.py
import chromadb

chroma = chromadb.PersistentClient(path="data/vectorstore")
collection = chroma.get_or_create_collection("papers")

def save_chunk(chunk, embedding, metadata):
    collection.add(
        ids=[metadata["id"]],
        documents=[chunk],
        embeddings=[embedding],
        metadatas=[metadata]
    )
