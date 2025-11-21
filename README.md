2.1. Thu thập và Tìm kiếm Dữ liệu (Data Acquisition)
Đầu vào: Hệ thống nhận Context (ví dụ: Abstract, Title, Keywords) từ người dùng.
Tích hợp API:
Sử dụng OpenAlex API để tìm kiếm các bài báo khoa học liên quan, hoặc các nguồn khác như OARelated Work, Semantic Scholar miễn sao là phù hợp.
Nếu khó quá thì có thể tải sẵn những nghiên cứu liên quan để viết related work dưới dạng đầu vào luôn cũng được.
2.2. Lưu trữ và Quản lý Kiến thức (Knowledge Storage)
Vector Database:
Lưu trữ dữ liệu bài báo đã tìm được vào ChromaDB để phục vụ tìm kiếm ngữ nghĩa (Semantic Search), hoặc là lưu dưới dạng Graph để thể hiện được mối quan hệ giữa những bài báo tốt hơn.
2.3. Tổng hợp nội dung (Content Generation - RAG)
Cơ chế: Sử dụng kỹ thuật RAG (Retrieval-Augmented Generation).
Quy trình: Truy vấn dữ liệu từ ChromaDB (hoặc Graph) dựa trên Context đầu vào và gửi dữ liệu đã lọc (retrieved context) tới LLM để yêu cầu viết nội dung.
Đầu ra: Một đoạn văn bản "Related Work" hoàn chỉnh, có trích dẫn nguồn.
2.4. Đánh giá chất lượng tự động (Automated Evaluation)
Sử dụng LLM khác để tự động chấm điểm nội dung vừa tạo ra.
Tiêu chí đánh giá (Metrics) bao gồm nhưng không giới hạn:
Relevance: Độ liên quan của các bài báo được chọn.
Coverage: Độ bao phủ các hướng nghiên cứu chính.
Logic/Coherence: Tính mạch lạc và logic trong cách sắp xếp ý.
Hallucination Check: Kiểm tra độ trung thực của thông tin.
