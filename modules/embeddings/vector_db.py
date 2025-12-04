# modules/embeddings/vector_db.py
import chromadb
import uuid

chroma = chromadb.PersistentClient(path="data/vectorstore")
collection = chroma.get_or_create_collection("papers")

def sanitize_metadata(metadata: dict) -> dict:
    """Loại bỏ hoặc chuyển None sang string để tránh lỗi Chroma"""
    sanitized = {}
    for k, v in metadata.items():
        if v is None:
            sanitized[k] = "None"
        else:
            sanitized[k] = v
    return sanitized

def save_chunk(chunk_text: str, embedding, metadata: dict):
    """Save a text chunk with embedding and metadata, skip duplicate paper"""
    metadata = sanitize_metadata(metadata)
    paper_id = metadata.get("id")
    if paper_id is None:
        paper_id = str(uuid.uuid4())
        metadata["id"] = paper_id

    # Kiểm tra duplicate paper
    try:
        existing = collection.get(ids=[paper_id])
        if existing['ids']:
            print(f"Skipping duplicate paper: {metadata.get('title', paper_id)}")
            return
    except Exception:
        # Nếu chưa tồn tại, get sẽ ném lỗi → safe để add
        pass

    # Tạo chunk id duy nhất
    chunk_id = str(uuid.uuid4())

    collection.add(
        ids=[chunk_id],
        documents=[chunk_text],
        embeddings=[embedding],
        metadatas=[metadata]
    )