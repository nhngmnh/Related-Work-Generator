import requests
import os
import re
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional

OPENALEX_BASE = "https://api.openalex.org"
GROBID_URL = "http://localhost:8070/api/processFulltextDocument"  # GROBID Docker local

def search_openalex(query: str, max_results: int = 5) -> List[Dict]:
    """Tìm kiếm bài báo theo từ khóa trên OpenAlex"""
    params = {
        "search": query,
        "per_page": max_results,
        "sort": "relevance_score:desc"
    }
    try:
        resp = requests.get(f"{OPENALEX_BASE}/works", params=params, timeout=10)
        resp.raise_for_status()
        results = resp.json().get("results", [])
    except Exception as e:
        print("Lỗi search OpenAlex:", e)
        return []

    papers = []
    for item in results:
        title = item.get("title") or ""
        citation = item.get("cited_by_count", 0)
        doi = item.get("doi")  # lấy DOI
        open_access_url = item.get("primary_location", {}).get("pdf_url")  # link PDF nếu có

        papers.append({
            "title": title,
            "citation": citation,
            "doi": doi,
            "pdf_url": open_access_url
        })
    return papers

def download_pdf(url: str, save_path: str) -> bool:
    """Download PDF nếu open-access"""
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        with open(save_path, "wb") as f:
            f.write(resp.content)
        return True
    except Exception as e:
        print("Không thể download PDF:", e)
        return False

def parse_pdf_with_grobid(pdf_path: str) -> str:
    """Gửi PDF đến GROBID Docker local và nhận TEI XML"""
    with open(pdf_path, "rb") as f:
        files = {"input": f}
        resp = requests.post(GROBID_URL, files=files)
        resp.raise_for_status()
        return resp.text

def tei_to_json(tei_xml: str) -> dict:
    # Namespace bắt buộc của TEI
    ns = {"tei": "http://www.tei-c.org/ns/1.0"}
    try:
        root = ET.fromstring(tei_xml)
    except ET.ParseError:
        return {}
    
    sections = {}

    abstract_node = root.find('.//tei:profileDesc/tei:abstract', ns)
    if abstract_node is not None:
        # SỬA LỖI QUAN TRỌNG: 
        # Thay 'tei:p' bằng './/tei:p' để tìm thẻ p ở bất kỳ độ sâu nào (bỏ qua thẻ div bao bên ngoài)
        abs_texts = []
        for p in abstract_node.findall('.//tei:p', ns):
            text = "".join(p.itertext()).strip()
            if text:
                abs_texts.append(text)
        
        if abs_texts:
            sections['Abstract'] = "\n".join(abs_texts)

   
    body_node = root.find('.//tei:text/tei:body', ns)
    
    if body_node is not None:
        for div in body_node.findall('tei:div', ns):
            # Lấy tiêu đề (head)
            head_node = div.find('tei:head', ns)
            
            title = "Untitled Section"
            if head_node is not None:
                # itertext() lấy nội dung text (ví dụ: "Introduction")
                head_text = "".join(head_node.itertext()).strip()
                
                # Lấy số thứ tự từ attribute n (ví dụ: "1.")
                n_attr = head_node.get('n')
                
                
                if n_attr and head_text:
                    title = f"{n_attr} {head_text}"
                elif head_text:
                    title = head_text
                elif n_attr:
                    title = n_attr

            # Lấy nội dung: Chỉ lấy các thẻ <p>
            paragraphs = []
            for p in div.findall('tei:p', ns):
                p_text = "".join(p.itertext()).strip()
                if p_text:
                    paragraphs.append(p_text)
            
            content = "\n".join(paragraphs)
            
            # Chỉ lưu nếu có nội dung
            if content:
                # Xử lý trường hợp trùng tên section
                if title in sections:
                    sections[title] += "\n\n" + content
                else:
                    sections[title] = content

    return sections

def run_search_and_parse():
    query = input("Nhập từ khóa tìm kiếm OpenAlex: ")
    papers = search_openalex(query)

    print(f"\nTìm thấy {len(papers)} bài:\n")
    for i, p in enumerate(papers, 1):
        print(f"--- Paper {i} ---")
        print("Title:", p["title"])
        print("Citations:", p["citation"])
        print("DOI:", p["doi"])
        print("PDF URL:", p["pdf_url"])

        if p["pdf_url"]:
            pdf_file = f"paper_{i}.pdf"
            if download_pdf(p["pdf_url"], pdf_file):
                print("Downloaded PDF, parsing with GROBID...")
                try:
                    tei_xml = parse_pdf_with_grobid(pdf_file)
                    # Save TEI XML to a separate file
                    out_dir = os.path.join("data", "processed", "tei")
                    os.makedirs(out_dir, exist_ok=True)
                    base_name = f"paper_{i}"
                    doi = p.get("doi") or ""
                    title = p.get("title") or ""
                    if doi:
                        base_name = re.sub(r"[^A-Za-z0-9._-]", "_", doi)
                    elif title:
                        base_name = re.sub(r"[^A-Za-z0-9._-]", "_", title)[:100] or base_name
                    xml_path = os.path.join(out_dir, f"{base_name}.xml")
                    with open(xml_path, "w", encoding="utf-8") as xf:
                        xf.write(tei_xml)
                    print(f"Saved TEI XML to: {xml_path}")
                    sections_json = tei_to_json(tei_xml)
                    print("Parsed sections JSON:")
                    for sec, content in sections_json.items():
                        print(f"--- {sec} ---")
                        print(content[:300])  # in 300 chars đầu
                        print("...")
                except Exception as e:
                    print("Error parsing PDF with GROBID:", e)
                finally:
                    os.remove(pdf_file)  # xóa PDF tạm
            else:
                print("Không thể download/parse PDF")
        else:
            print("Không có PDF open-access")

if __name__ == "__main__":
    run_search_and_parse()
