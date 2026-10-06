import os
import sys
import io
import uuid
import json
import re
from pathlib import Path

# Force UTF-8 encoding on Windows to prevent 'charmap' codec crashes
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        else:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Body
from fastapi.responses import FileResponse, Response, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pdf_utils import get_pdf_info, render_page_image, export_annotated_pdf
from solver import solve_page_hybrid, parse_page_range

# Load environment variables (.env if exists)
load_dotenv()

if getattr(sys, 'frozen', False):
    BUNDLE_DIR = Path(getattr(sys, '_MEIPASS', os.path.dirname(sys.executable)))
    BASE_DIR = Path(os.path.dirname(sys.executable))
else:
    BUNDLE_DIR = Path(__file__).resolve().parent
    BASE_DIR = Path(__file__).resolve().parent

UPLOADS_DIR = BASE_DIR / "uploads"
OUTPUTS_DIR = BASE_DIR / "outputs"
CACHE_DIR = OUTPUTS_DIR / "cache"
STATIC_DIR = BUNDLE_DIR / "static"
ASSETS_DIR = BUNDLE_DIR / "assets"

UPLOADS_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)

app = FastAPI(title="PrepMate PDF - AI Workbook Solver")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Sunucu hatası: {str(exc)}"}
    )

class SolvePageRequest(BaseModel):
    file_id: str
    page_num: int
    api_key: str = ""
    detailed: bool = False
    force: bool = False

class ExportRequest(BaseModel):
    file_id: str
    mode: str # "only_homework" or "full_book"
    selected_pages: list[int]
    pages_annotations: dict[str, list[dict]]

def extract_keys_pool(user_input: str) -> list[str]:
    combined_sources = []
    if user_input and user_input != "ENV_KEY_ACTIVE":
        combined_sources.append(user_input)
    
    for env_name in ["GEMINI_API_KEY", "GEMINI_API_KEYS", "OPENROUTER_API_KEY", "OPENROUTER_API_KEYS"]:
        val = os.getenv(env_name, "").strip()
        if val:
            combined_sources.append(val)
            
    keys = []
    for src in combined_sources:
        for chunk in re.split(r"[\r\n,;]+", src):
            k = chunk.strip()
            # Ignore template placeholders like AIzaSy1..., sk-or-v1-..., etc.
            if (k and not k.startswith("AIzaSy1...") and not k.startswith("sk-or-v1-...") 
                and k != "AIzaSy..." and k != "your_api_key" and k not in keys):
                keys.append(k)
    return keys

@app.get("/api/config")
def get_config():
    keys = extract_keys_pool("")
    count = len(keys)
    if count == 0:
        return {"has_env_key": False, "key_count": 0, "key_type": "", "masked_key": ""}
    
    first = keys[0]
    is_or = any(k.startswith("sk-or-") or k.startswith("sk-") for k in keys)
    label = f"{count} Anahtar Aktif" if count > 1 else ("OpenRouter" if is_or else "Gemini 3.8")
    return {
        "has_env_key": True,
        "key_count": count,
        "key_type": label,
        "masked_key": f"{first[:4]}...{first[-4:]}" if len(first) > 8 else ""
    }

@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Lütfen geçerli bir PDF dosyası yükleyin.")
    
    file_id = uuid.uuid4().hex[:12]
    save_path = UPLOADS_DIR / f"{file_id}.pdf"
    
    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)
        
    try:
        info = get_pdf_info(str(save_path))
    except Exception as e:
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=f"PDF okunamadı: {str(e)}")
        
    return {
        "file_id": file_id,
        "filename": file.filename,
        "total_pages": info["total_pages"]
    }

@app.post("/api/load-sample")
def load_sample():
    sample_path = BUNDLE_DIR / "ornek_ingilizce_odev.pdf"
    if not sample_path.exists():
        sample_path = BASE_DIR / "ornek_ingilizce_odev.pdf"
    if not sample_path.exists():
        raise HTTPException(status_code=404, detail="Örnek dosya bulunamadı.")
    
    file_id = "sample_prep"
    save_path = UPLOADS_DIR / f"{file_id}.pdf"
    import shutil
    shutil.copy(sample_path, save_path)
    
    try:
        info = get_pdf_info(str(save_path))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Örnek PDF okunamadı: {str(e)}")
        
    return {
        "file_id": file_id,
        "filename": "ornek_ingilizce_odev.pdf",
        "total_pages": info["total_pages"]
    }

@app.get("/api/page-image/{file_id}/{page_num}")
def get_page_image(file_id: str, page_num: int):
    pdf_path = UPLOADS_DIR / f"{file_id}.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF bulunamadı.")
        
    try:
        img_bytes = render_page_image(str(pdf_path), page_num, dpi=130, img_format="jpeg")
        return Response(content=img_bytes, media_type="image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sayfa görseli oluşturulamadı: {str(e)}")

@app.post("/api/solve-page")
def solve_page(req: SolvePageRequest):
    pdf_path = UPLOADS_DIR / f"{req.file_id}.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF bulunamadı.")
        
    # 1. Instant Cache Check (Sub-millisecond fast-path)
    det_suffix = "_det" if req.detailed else ""
    cache_file = CACHE_DIR / f"{req.file_id}_{req.page_num}{det_suffix}.json"
    if not req.force and cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
            return {
                "success": True,
                "page_num": req.page_num,
                "annotations": cached_data,
                "cached": True
            }
        except Exception:
            pass

    keys_pool = extract_keys_pool(req.api_key)
    if not keys_pool:
        raise HTTPException(
            status_code=400, 
            detail="API Anahtarı bulunamadı! Lütfen arayüzden veya .env dosyasından API anahtarlarınızı girin."
        )
        
    try:
        img_bytes = render_page_image(str(pdf_path), req.page_num, dpi=130, img_format="jpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sayfa görseli alınamadı: {str(e)}")
        
    try:
        annotations = solve_page_hybrid(str(pdf_path), req.page_num, img_bytes, keys_pool, detailed=req.detailed)
        # Save to cache
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(annotations, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
            
        return {
            "success": True,
            "page_num": req.page_num,
            "annotations": annotations,
            "cached": False
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Yapay zeka çözümü sırasında hata oluştu: {str(e)}")

@app.post("/api/export")
def export_pdf(req: ExportRequest):
    pdf_path = UPLOADS_DIR / f"{req.file_id}.pdf"
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="Orijinal PDF bulunamadı.")
        
    export_id = uuid.uuid4().hex[:12]
    suffix = "odev_sayfalari" if req.mode == "only_homework" else "tum_kitap"
    out_filename = f"cozulmus_{suffix}_{export_id}.pdf"
    out_path = OUTPUTS_DIR / out_filename
    
    try:
        export_annotated_pdf(
            pdf_path=str(pdf_path),
            pages_annotations=req.pages_annotations,
            output_path=str(out_path),
            mode=req.mode,
            selected_pages=req.selected_pages
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF oluşturulurken hata: {str(e)}")
        
    return {
        "success": True,
        "download_url": f"/api/download/{out_filename}",
        "filename": out_filename
    }

@app.get("/api/download/{filename}")
def download_file(filename: str):
    file_path = OUTPUTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Dosya bulunamadı.")
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/pdf"
    )

# Mount static folder for frontend
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    import webbrowser
    import threading
    
    def open_browser():
        webbrowser.open("http://localhost:8000")
        
    threading.Timer(1.2, open_browser).start()
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
