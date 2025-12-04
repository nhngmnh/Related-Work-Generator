# modules/rag/content_generator_gemini.py
from modules.embeddings import vector_db, embedder
from google import genai  # pip install google-generativeai

TOP_K = 20
client = genai.Client(api_key="")

def embed_text(text: str):
    return embedder.embed_text(text).tolist()

def retrieve_context(input_text, top_k=TOP_K):
    """
    Trả về danh sách dict mỗi chunk + metadata + distance.
    """
    query_vec = embed_text(input_text)
    results = vector_db.collection.query(
        query_embeddings=[query_vec],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    retrieved = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        retrieved.append({
            "chunk": doc,
            "metadata": meta,
            "distance": dist
        })
    return retrieved

def build_prompt(input_text, retrieved_chunks):
    """
    Xây dựng prompt RAG, chèn tất cả chunk liên quan và metadata.
    """
    context_lines = []
    for r in retrieved_chunks:
        meta = r["metadata"]
        title = meta.get("title", "unknown")
        source = meta.get("source", "unknown")
        context_lines.append(f"{r['chunk']} (title: {title}, source: {source})")

    context_text = "\n".join(context_lines)
    prompt = (
        f"Bạn là một nhà nghiên cứu. Dựa trên các thông tin sau:\n"
        f"{context_text}\n\n"
        f"Hãy viết một đoạn văn “Related Work” hoàn chỉnh cho paper sau:\n"
        f"\"{input_text}\"\n\n"
        f"Yêu cầu trích dẫn nguồn tương ứng."
    )
    return prompt

def generate_related_work(input_text, model="gemini-2.0-flash"):
    retrieved_chunks = retrieve_context(input_text)
    prompt = build_prompt(input_text, retrieved_chunks)
    print("----- prompt -----")
    print(prompt)
    print("------------------")
    response = client.models.generate_content(
        model=model,
        contents=prompt
    )

    # Lấy text thuần từ candidate đầu tiên và part đầu tiên
    try:
        return response.candidates[0].content.parts[0].text
    except (IndexError, AttributeError):
        return "No output generated."

def evaluate_related_work(related_work_text, input_text, retrieved_chunks, model="gemini-2.0-flash"):
    """
    Sử dụng LLM để đánh giá quality của đoạn Related Work vừa tạo.
    Metrics: Relevance, Coverage, Logic/Coherence, Hallucination
    """
    eval_prompt = f"""
    Bạn là một chuyên gia đánh giá bài báo khoa học. Hãy đánh giá đoạn Related Work dưới đây theo các tiêu chí:

    1. Relevance: Độ liên quan của các bài báo được trích dẫn.
    2. Coverage: Độ bao phủ các hướng nghiên cứu chính.
    3. Logic/Coherence: Tính mạch lạc, logic trong cách sắp xếp ý.
    4. Hallucination Check: Độ trung thực của thông tin, có thông tin sai hay bịa đặt không.

    Đoạn Related Work cần đánh giá:
    \"\"\"{related_work_text}\"\"\"

    Các papers đã retrieved (bao gồm metadata):
    \"\"\" 
    {chr(10).join([f"{i+1}. {c['metadata'].get('title','N/A')} ({c['metadata'].get('year','N/A')})" for i,c in enumerate(retrieved_chunks)])}
    \"\"\"

    Hãy trả về đánh giá dạng JSON như sau:
    {{
        "Relevance": "score/nhận xét",
        "Coverage": "score/nhận xét",
        "Logic/Coherence": "score/nhận xét",
        "Hallucination": "score/nhận xét"
    }}
    """

    eval_response = client.models.generate_content(
        model=model,
        contents=eval_prompt
    )

    try:
        eval_text = eval_response.candidates[0].content.parts[0].text
    except (IndexError, AttributeError):
        eval_text = "No evaluation output generated."

    return eval_text
