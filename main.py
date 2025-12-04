from modules.rag.content_generator_gemini import generate_related_work, retrieve_context, evaluate_related_work

def main_rag():
    new_paper = input("Nhập nội dung paper cần tổng hợp Related Work: ")

    # Lấy các chunk liên quan
    retrieved_chunks = retrieve_context(new_paper)

    # Sinh Related Work
    related_work = generate_related_work(new_paper)
    print("\n--- Related Work (Gemini) ---\n")
    print(related_work)

    # Evaluate
    eval_result = evaluate_related_work(related_work, new_paper, retrieved_chunks)
    print("\n--- Automated Evaluation ---\n")
    print(eval_result)

    return related_work, eval_result

if __name__ == "_main_":
    main_rag()
