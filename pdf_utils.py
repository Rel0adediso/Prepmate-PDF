import pymupdf
import io
import os

def get_pdf_info(pdf_path: str) -> dict:
    doc = pymupdf.open(pdf_path)
    total_pages = len(doc)
    doc.close()
    return {
        "total_pages": total_pages,
        "filename": os.path.basename(pdf_path)
    }

def render_page_image(pdf_path: str, page_num: int, dpi: int = 130, img_format: str = "jpeg", quality: int = 85) -> bytes:
    """
    Renders a 1-based page number to image bytes.
    Defaults to high-speed JPEG at 130 DPI (crystal-clear text, 10x smaller payload, zero quality loss).
    """
    doc = pymupdf.open(pdf_path)
    if page_num < 1 or page_num > len(doc):
        doc.close()
        raise ValueError(f"Page {page_num} out of bounds (1-{len(doc)})")
    
    page = doc[page_num - 1]
    pix = page.get_pixmap(dpi=dpi)
    if img_format.lower() in ["jpg", "jpeg"]:
        img_bytes = pix.tobytes("jpeg", jpg_quality=quality)
    else:
        img_bytes = pix.tobytes("png")
    doc.close()
    return img_bytes

def export_annotated_pdf(
    pdf_path: str,
    pages_annotations: dict[int, list[dict]],
    output_path: str,
    mode: str = "only_homework",
    selected_pages: list[int] = None
) -> str:
    """
    Inserts Acrobat-style text annotations into the PDF and saves the result.
    mode:
      - 'only_homework': exports only the selected pages with answers
      - 'full_book': exports the complete book with the answers inserted into corresponding pages
    """
    doc = pymupdf.open(pdf_path)
    total_pages = len(doc)
    
    # 1. Apply annotations to the document pages
    for page_num_str, annotations in pages_annotations.items():
        page_num = int(page_num_str)
        if 1 <= page_num <= total_pages:
            page = doc[page_num - 1]
            page_w = page.rect.width
            page_h = page.rect.height
            
            for item in annotations:
                box = item.get("box_2d", [100, 100, 150, 300])
                ymin, xmin, ymax, xmax = box
                
                x0 = (xmin / 1000.0) * page_w
                y0 = (ymin / 1000.0) * page_h
                x1 = (xmax / 1000.0) * page_w
                y1 = (ymax / 1000.0) * page_h
                rect = pymupdf.Rect(x0, y0, x1, y1)
                
                if item.get("type") == "highlight":
                    # Adobe Acrobat Native Highlighter Annotation (Exact text bounds, ISO 32000 compliant /Highlight)
                    try:
                        annot = page.add_highlight_annot(rect)
                        annot.set_colors(stroke=(1.0, 0.92, 0.23))
                        annot.set_opacity(0.55)
                        annot.update()
                    except Exception:
                        page.draw_rect(
                            rect,
                            color=None,
                            fill=(1.0, 0.92, 0.23),
                            fill_opacity=0.55
                        )
                    continue

                if item.get("type") == "correction":
                    # Acrobat Error Correction: strikethrough line through wrong word + neat compact correction in line gap
                    y_mid = (y0 + y1) / 2.0
                    page.draw_line(
                        pymupdf.Point(x0 - 1, y_mid),
                        pymupdf.Point(x1 + 1, y_mid),
                        color=(0.85, 0.15, 0.15),
                        width=1.1
                    )
                    corr_text = str(item.get("answer", "")).strip()
                    if corr_text:
                        corr_font_size = 5.8
                        t_w = pymupdf.get_text_length(corr_text, fontname="helv", fontsize=corr_font_size)
                        w_w = x1 - x0
                        draw_x = x0 + max(0.0, (w_w - t_w) / 2.0)
                        
                        # Position tucked into the line gap right above the word
                        draw_y = y0 + 1.2
                        
                        # Subtle white pill background so it never blends or clashes with surrounding text
                        bg_rect = pymupdf.Rect(draw_x - 0.8, draw_y - 4.6, draw_x + t_w + 0.8, draw_y + 0.8)
                        page.draw_rect(bg_rect, color=None, fill=(1, 1, 1), fill_opacity=0.92)
                        
                        page.insert_text(
                            pymupdf.Point(draw_x, draw_y),
                            corr_text,
                            fontsize=corr_font_size,
                            fontname="helv",
                            color=(0.08, 0.35, 0.85)
                        )
                    continue

                text = str(item.get("answer", "")).strip()
                if not text:
                    continue
                
                font_size = float(item.get("font_size", 11))
                
                # Adobe Acrobat style: Helvetica, pure black, crisp text
                target_font_size = float(item.get("font_size", 11))
                fit_success = False
                
                # Dynamically try sizes down to 8pt to fit the box neatly
                for sz in range(int(target_font_size), 7, -1):
                    rc = page.insert_textbox(
                        rect,
                        text,
                        fontsize=float(sz),
                        fontname="helv",
                        color=(0, 0, 0),
                        align=0
                    )
                    if rc >= 0:
                        fit_success = True
                        break
                
                if not fit_success:
                    page.insert_text(
                        pymupdf.Point(x0, y0 + target_font_size * 0.85),
                        text,
                        fontsize=target_font_size,
                        fontname="helv",
                        color=(0, 0, 0)
                    )
                    
    # 2. Export based on mode
    dir_name = os.path.dirname(output_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    
    if mode == "only_homework" and selected_pages:
        new_doc = pymupdf.open()
        for p in selected_pages:
            if 1 <= p <= total_pages:
                new_doc.insert_pdf(doc, from_page=p - 1, to_page=p - 1)
        new_doc.save(output_path)
        new_doc.close()
    else:
        doc.save(output_path)
        
    doc.close()
    return output_path
