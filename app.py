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
from typing import Any, Optional
from pydantic import BaseModel

from pdf_utils import get_pdf_info, render_page_image, export_annotated_pdf
from solver import solve_page_hybrid, parse_page_range, check_page_answers

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
    check_mode: bool = False

class ExportRequest(BaseModel):
    file_id: str
    mode: str = "only_homework" # "only_homework" or "full_book"
    selected_pages: list[int] = []
    pages_annotations: dict[str, Any] = {}

class ZipExportRequest(BaseModel):
    files: list[ExportRequest]

# Permanent user config file (survives app restarts and portable exe runs)
USER_CONFIG_DIR = Path.home() / ".prepmate_pdf"
USER_CONFIG_FILE = USER_CONFIG_DIR / "config.json"
USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def load_saved_user_keys() -> str:
    try:
        if USER_CONFIG_FILE.exists():
            data = json.loads(USER_CONFIG_FILE.read_text(encoding="utf-8"))
            return str(data.get("api_key", "")).strip()
    except Exception:
        pass
    return ""

def save_user_keys(key_str: str):
    try:
        USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        if key_str:
            USER_CONFIG_FILE.write_text(json.dumps({"api_key": key_str}, indent=2), encoding="utf-8")
        else:
            if USER_CONFIG_FILE.exists():
                USER_CONFIG_FILE.unlink(missing_ok=True)
    except Exception as e:
        print(f"[PrepMate PDF] Config save error: {e}")

class SaveKeyRequest(BaseModel):
    api_key: str = ""

def extract_keys_pool(user_input: str) -> list[str]:
    combined_sources = []
    if user_input and user_input != "ENV_KEY_ACTIVE":
        combined_sources.append(user_input)
    
    # 1. Permanently saved user keys
    saved_key = load_saved_user_keys()
    if saved_key:
        combined_sources.append(saved_key)

    # 2. Environment variables (.env if exists)
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
    saved_raw = load_saved_user_keys()
    if count == 0:
        return {"has_env_key": False, "key_count": 0, "key_type": "", "saved_key": ""}
    
    first = keys[0]
    is_or = any(k.startswith("sk-or-") or k.startswith("sk-") for k in keys)
    label = f"{count} Anahtar Aktif" if count > 1 else ("OpenRouter" if is_or else "Gemini 3.8")
    return {
        "has_env_key": True,
        "key_count": count,
        "key_type": label,
        "saved_key": saved_raw if saved_raw else ""
    }

@app.post("/api/save-key")
def save_key_endpoint(req: SaveKeyRequest):
    save_user_keys(req.api_key.strip())
    keys = extract_keys_pool("")
    count = len(keys)
    is_or = any(k.startswith("sk-or-") or k.startswith("sk-") for k in keys)
    label = f"{count} Anahtar Aktif" if count > 1 else ("OpenRouter" if is_or else "Gemini 3.8")
    return {
        "status": "ok",
        "has_key": count > 0,
        "key_count": count,
        "key_type": label if count > 0 else ""
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
    chk_suffix = "_chk" if req.check_mode else ""
    cache_file = CACHE_DIR / f"{req.file_id}_{req.page_num}{det_suffix}{chk_suffix}.json"
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
        if req.check_mode:
            annotations = check_page_answers(str(pdf_path), req.page_num, img_bytes, keys_pool, detailed=req.detailed)
        else:
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
    
    # Merge disk cache so that ALL solved pages are included,
    # even if client refreshed or only sent partial annotations
    merged_annotations = {}
    
    # 1. First, load all solved pages from CACHE_DIR for this file_id
    for c_path in CACHE_DIR.glob(f"{req.file_id}_*.json"):
        m = re.match(rf"^{req.file_id}_(\d+)\.json$", c_path.name)
        if m:
            p_num_str = m.group(1)
            try:
                with open(c_path, "r", encoding="utf-8") as f:
                    cached_data = json.load(f)
                if isinstance(cached_data, list) and cached_data:
                    merged_annotations[p_num_str] = cached_data
            except Exception:
                pass

    # 2. Then overlay / override with annotations passed from client (e.g. user manual edits)
    if isinstance(req.pages_annotations, dict):
        for p_num_str, annots in req.pages_annotations.items():
            if isinstance(annots, list) and annots:
                merged_annotations[str(p_num_str)] = annots

    selected_pages = req.selected_pages
    if req.mode == "only_homework" and not selected_pages:
        selected_pages = sorted([int(k) for k in merged_annotations.keys()])

    try:
        export_annotated_pdf(
            pdf_path=str(pdf_path),
            pages_annotations=merged_annotations,
            output_path=str(out_path),
            mode=req.mode,
            selected_pages=selected_pages
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

@app.post("/api/export-zip")
def export_zip(req: ZipExportRequest):
    import zipfile
    if not req.files:
        raise HTTPException(status_code=400, detail="Dışa aktarılacak dosya bulunamadı.")
        
    zip_id = uuid.uuid4().hex[:8]
    zip_filename = f"PrepMate_Cozulmus_Odevler_{zip_id}.zip"
    zip_path = OUTPUTS_DIR / zip_filename
    
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for idx, f_req in enumerate(req.files, 1):
            src_pdf = UPLOADS_DIR / f"{f_req.file_id}.pdf"
            if not src_pdf.exists():
                continue
            temp_pdf_name = f"Odev_{idx}_{f_req.file_id[:6]}.pdf"
            temp_out = OUTPUTS_DIR / f"temp_{temp_pdf_name}"

            merged_annotations = {}
            for c_path in CACHE_DIR.glob(f"{f_req.file_id}_*.json"):
                m = re.match(rf"^{f_req.file_id}_(\d+)\.json$", c_path.name)
                if m:
                    p_num_str = m.group(1)
                    try:
                        with open(c_path, "r", encoding="utf-8") as f:
                            cached_data = json.load(f)
                        if isinstance(cached_data, list) and cached_data:
                            merged_annotations[p_num_str] = cached_data
                    except Exception:
                        pass
            if isinstance(f_req.pages_annotations, dict):
                for p_num_str, annots in f_req.pages_annotations.items():
                    if isinstance(annots, list) and annots:
                        merged_annotations[str(p_num_str)] = annots

            sel_pages = f_req.selected_pages
            if f_req.mode == "only_homework" and not sel_pages:
                sel_pages = sorted([int(k) for k in merged_annotations.keys()])

            try:
                export_annotated_pdf(
                    pdf_path=str(src_pdf),
                    pages_annotations=merged_annotations,
                    output_path=str(temp_out),
                    mode=f_req.mode,
                    selected_pages=sel_pages
                )
                zip_file.write(temp_out, arcname=temp_pdf_name)
                temp_out.unlink(missing_ok=True)
            except Exception:
                continue
                
    return {
        "success": True,
        "download_url": f"/api/download-zip/{zip_filename}",
        "filename": zip_filename
    }

@app.get("/api/download-zip/{filename}")
def download_zip(filename: str):
    file_path = OUTPUTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="ZIP dosyası bulunamadı.")
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/zip"
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
