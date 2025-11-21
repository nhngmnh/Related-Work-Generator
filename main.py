# main.py
from modules.embeddings import vector_db
from sentence_transformers import SentenceTransformer

# 1. Load embedding model
embedder = SentenceTransformer('all-mpnet-base-v2')  # hoặc model bạn dùng khi lưu chunks

def embed_text(text: str):
    return embedder.encode(text).tolist()

def query_related_papers(new_paper_text, top_k=5):
    query_emb = embed_text(new_paper_text)
    results = vector_db.collection.query(
        query_embeddings=[query_emb],
        n_results=top_k,
        include=['metadatas', 'documents', 'distances']
    )
    return results

def main():
    new_paper = input("Nhập nội dung paper cần tìm tương tự: ")
    results = query_related_papers(new_paper, top_k=5)

    print("\n--- Top related papers ---")
    for idx, (doc, metadata, dist) in enumerate(zip(
        results['documents'][0],
        results['metadatas'][0],
        results['distances'][0]
    )):
        print(f"{idx+1}. Score: {1-dist:.4f}, Title: {metadata.get('title','N/A')}")
        print(f"   Document snippet: {doc[:200]}...\n")

if __name__ == "__main__":
    main()
