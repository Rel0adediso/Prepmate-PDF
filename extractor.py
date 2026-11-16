import os
import re
from pathlib import Path
from typing import Optional, Dict, Any
import pymupdf
import pymupdf4llm

def extract_pdf_to_markdown(
    pdf_path: str, 
    cache_path: Optional[str] = None, 
    force: bool = False
) -> str:
    """
    Converts a PDF document to clean, LLM-ready GitHub-flavored Markdown using C/C++ native pymupdf4llm.
    Preserves tables, formulas, headers and exercises.
    Caches the output to disk if cache_path is provided.
    """
    if cache_path and not force and os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            pass

    md_content = pymupdf4llm.to_markdown(pdf_path)

    if cache_path:
        try:
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            with open(cache_path, "w", encoding="utf-8") as f:
                f.write(md_content)
        except Exception as e:
            print(f"[Extractor] Cache write warning: {e}")

    return md_content

def extract_page_markdown(
    pdf_path: str, 
    page_num: int, 
    cache_path: Optional[str] = None, 
    force: bool = False
) -> str:
    """
    Extracts structured markdown for a specific 1-based page number.
    Runs in sub-10ms using native C-bindings.
    """
    if cache_path and not force and os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            pass

    doc = pymupdf.open(pdf_path)
    total_pages = len(doc)
    if page_num < 1 or page_num > total_pages:
        doc.close()
        raise ValueError(f"Page {page_num} out of bounds (1-{total_pages})")

    # Extract single page markdown via pymupdf4llm page_chunks or page extraction
    page_idx = page_num - 1
    md_page = pymupdf4llm.to_markdown(doc, pages=[page_idx])
    doc.close()

    if cache_path:
        try:
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            with open(cache_path, "w", encoding="utf-8") as f:
                f.write(md_page)
        except Exception as e:
            print(f"[Extractor] Single page cache write warning: {e}")

    return md_page

def get_markdown_summary(markdown_text: str) -> Dict[str, Any]:
    """
    Extracts high-level outline (headings, estimated tokens) for fast grounding.
    """
    lines = markdown_text.splitlines()
    headings = []
    for line in lines:
        match = re.match(r"^(#{1,3})\s+(.+)$", line.strip())
        if match:
            headings.append({
                "level": len(match.group(1)),
                "title": match.group(2).strip()
            })
    
    char_count = len(markdown_text)
    # Rough estimate of tokens (4 chars ~ 1 token)
    est_tokens = char_count // 4

    return {
        "headings": headings[:25],
        "char_count": char_count,
        "est_tokens": est_tokens
    }
