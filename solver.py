import os
import sys
import io
import json
import base64
import re
import httpx
import pymupdf
import numpy as np
import time

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

def log_msg(msg: str):
    try:
        print(msg)
    except Exception:
        try:
            print(msg.encode("ascii", errors="replace").decode("ascii"))
        except Exception:
            pass

def safe_close_doc(doc):
    """
    Safely closes a PyMuPDF document if it is open, preventing 'ValueError: document closed'.
    """
    try:
        if doc is not None and not getattr(doc, "is_closed", False):
            doc.close()
    except Exception:
        pass

def parse_page_range(range_str: str, max_pages: int) -> list[int]:
    """
    Parses strings like "15-20", "5, 8, 12", "1-3, 5, 10-12" into a sorted list of 1-based page numbers.
    """
    pages = set()
    parts = [p.strip() for p in range_str.split(",") if p.strip()]
    for part in parts:
        if "-" in part:
            bounds = part.split("-")
            if len(bounds) == 2 and bounds[0].strip().isdigit() and bounds[1].strip().isdigit():
                start = int(bounds[0].strip())
                end = int(bounds[1].strip())
                for p in range(min(start, end), max(start, end) + 1):
                    if 1 <= p <= max_pages:
                        pages.add(p)
        elif part.isdigit():
            p = int(part)
            if 1 <= p <= max_pages:
                pages.add(p)
    return sorted(list(pages))


def deduplicate_overlapping_annotations(annotations: list[dict]) -> list[dict]:
    """
    Guarantees no two annotations ever overlap or collide on top of each other.
    If two annotations occupy essentially the same box, retains the first one.
    """
    if not annotations:
        return []
    
    unique_items = []
    for item in annotations:
        box_a = item.get("box_2d")
        if not box_a or len(box_a) != 4:
            unique_items.append(item)
            continue
            
        ymin_a, xmin_a, ymax_a, xmax_a = box_a
        is_duplicate = False
        
        for kept in unique_items:
            box_b = kept.get("box_2d")
            if not box_b or len(box_b) != 4:
                continue
            ymin_b, xmin_b, ymax_b, xmax_b = box_b
            
            # Check overlap
            v_ovlp = max(0, min(ymax_a, ymax_b) - max(ymin_a, ymin_b))
            h_ovlp = max(0, min(xmax_a, xmax_b) - max(xmin_a, xmin_b))
            
            h_len_a = max(1, xmax_a - xmin_a)
            v_len_a = max(1, ymax_a - ymin_a)
            h_len_b = max(1, xmax_b - xmin_b)
            v_len_b = max(1, ymax_b - ymin_b)
            
            # If vertical overlap >= 60% and horizontal overlap >= 50%
            if v_ovlp >= 0.6 * min(v_len_a, v_len_b) and h_ovlp >= 0.5 * min(h_len_a, h_len_b):
                is_duplicate = True
                break
                
        if not is_duplicate:
            unique_items.append(item)
            
    return unique_items


def extract_page_blanks_and_lines(page) -> tuple[list[dict], list[dict], int]:
    """
    Analyzes the PDF page and cleanly separates:
    1. Normal blanks (fill in the blanks, missing words, questions, word-order corrections)
    2. Ruled writing lines (empty notebook lines for free writing paragraphs)
    3. Occupied lines count (blanks/lines already filled with text, e.g. from previous solves)
    Filters out table headers, dots, and merges split/wrapped underscores cleanly.
    """
    w_page = page.rect.width
    h_page = page.rect.height
    
    normal_blanks = []
    writing_lines = []
    occupied_count = 0
    
    words = page.get_text("words")
    raw_unders = []
    
    for w in words:
        x0, y0, x1, y1 = w[0], w[1], w[2], w[3]
        width_pt = x1 - x0
        raw_text = w[4]
        # Normalize Unicode ellipsis (\u2026 -> ...)
        text = raw_text.replace('\u2026', '...').strip()
        
        extra_before = ""
        extra_after = ""

        # Handle tokens that have underscores attached to text (e.g. '___________from', 'drink________?')
        if re.search(r'[a-zA-Z0-9]', text):
            # Case A: Leading underscores followed by text (e.g. '___________from')
            m_lead = re.match(r'^(_+)([a-zA-Z].*)', text)
            if m_lead and len(m_lead.group(1)) >= 3:
                u_len = len(m_lead.group(1))
                tot_len = len(text)
                x1 = x0 + width_pt * (u_len / tot_len)
                width_pt = x1 - x0
                extra_after = m_lead.group(2)
                text = m_lead.group(1)
            # Case B: Leading text followed by trailing underscores (e.g. 'drink________?')
            elif re.match(r'^(.*?[a-zA-Z0-9\(\)])(_+)([\?\!\.]*)$', text):
                m_trail = re.match(r'^(.*?[a-zA-Z0-9\(\)])(_+)([\?\!\.]*)$', text)
                if len(m_trail.group(2)) >= 3:
                    p_len = len(m_trail.group(1))
                    tot_len = len(text)
                    x0 = x0 + width_pt * (p_len / tot_len)
                    width_pt = x1 - x0
                    extra_before = m_trail.group(1)
                    extra_after = m_trail.group(3)
                    text = m_trail.group(2)
                else:
                    continue
            else:
                continue
            
        # Check if it has underscores, dots, or empty brackets (T/F, Matching: (), [], etc.)
        is_blank_like = ('__' in text or '..' in text or bool(re.match(r'^[\(\[\{]\s*[\)\]\}]$', text)))
        if not is_blank_like:
            continue
            
        if bool(re.match(r'^[\(\[\{]\s*[\)\]\}]$', text)):
            width_pt = max(width_pt, 16.0)

        raw_unders.append({
            "w": w,
            "x0": x0, "y0": y0, "x1": x1, "y1": y1, "width_pt": width_pt,
            "text": text,
            "extra_before": extra_before,
            "extra_after": extra_after
        })

    # Filter out table header dots and merge adjacent or line-wrapped underscores
    skip_indices = set()
    cleaned_unders = []
    
    for i, u in enumerate(raw_unders):
        if i in skip_indices:
            continue
        
        # Check if it is a table header placeholder (e.g. 'Verb be', 'Question word', 'Short Answer')
        same_line = [sw for sw in words if abs(sw[1] - u["y0"]) < 6]
        line_str = " ".join(sw[4] for sw in same_line)
        if any(hdr in line_str for hdr in ["Verb be", "Question word", "Short Answer", "Subject"]):
            if set(u["text"].strip('“"”’\'')).issubset({'.'}):
                continue
            if len(u["text"]) < 8 and not any(c in u["text"] for c in ['_']):
                continue

        # Merge adjacent underscores on the same line (e.g. '____ _____________' for walk)
        if i + 1 < len(raw_unders):
            next_u = raw_unders[i+1]
            if abs(next_u["y0"] - u["y0"]) < 4 and 0 <= (next_u["x0"] - u["x1"]) < 30:
                w_idx = words.index(u["w"])
                next_idx = words.index(next_u["w"])
                if next_idx == w_idx + 1:
                    u["x1"] = next_u["x1"]
                    u["width_pt"] = u["x1"] - u["x0"]
                    u["text"] = u["text"] + " " + next_u["text"]
                    skip_indices.add(i + 1)
                    
        # Merge line-wrapped underscore continuation (e.g. 'She __________ \n _______ (talk)')
        # Strictly applies to short blanks (< 200 pt), NEVER ruled lines
        if i + 1 < len(raw_unders) and (i + 1) not in skip_indices:
            next_u = raw_unders[i+1]
            w_idx = words.index(u["w"])
            next_idx = words.index(next_u["w"])
            if next_idx == w_idx + 1 and 10 <= (next_u["y0"] - u["y0"]) <= 25 and u["width_pt"] < 200 and next_u["width_pt"] < 200:
                # Discard the stub at line end, keep the line-starting one where the verb bracket is
                skip_indices.add(i)
                continue

        cleaned_unders.append(u)

    # Process into normal_blanks and writing_lines
    for u in cleaned_unders:
        x0, y0, x1, y1 = u["x0"], u["y0"], u["x1"], u["y1"]
        width_pt = u["width_pt"]
        text = u["text"]
        w = u["w"]
        
        # Check if this underscore/blank or line ALREADY has text sitting directly on it
        # (e.g. an already solved/exported PDF, or a pre-filled textbook example).
        overlapping_words_found = []
        for sw in words:
            if sw == w or '__' in sw[4] or '..' in sw[4]:
                continue
            v_ovlp = max(0.0, min(y1, sw[3]) - max(y0, sw[1]))
            h_ovlp = max(0.0, min(x1, sw[2]) - max(x0, sw[0]))
            if v_ovlp >= 4.0 and h_ovlp >= 6.0:
                if re.search(r'[a-zA-Z0-9]', sw[4]):
                    overlapping_words_found.append(sw[4])

        if overlapping_words_found:
            occupied_count += 1
            continue
        
        same_line = [sw for sw in words if abs(sw[1] - y0) < 6]
        same_line.sort(key=lambda sw: sw[0])
        try:
            w_idx = same_line.index(w)
        except ValueError:
            continue
            
        before = ' '.join(sw[4] for sw in same_line[:w_idx]).strip()
        if u["extra_before"]:
            before = f"{before} {u['extra_before']}".strip()
        after = ' '.join(sw[4] for sw in same_line[w_idx+1:]).strip()
        if u["extra_after"]:
            after = f"{extra_after} {after}".strip()
        
        # Filter out explanation bullet points (dots with no words before and long explanation after)
        if not before and len(after) > 25 and set(text).issubset({'.'}):
            continue

        # True empty ruled lines: before is empty, after is empty, width >= 170 pt, len(text) >= 20
        if not before and not after and width_pt >= 170 and len(text) >= 20:
            ymin = int((y0 / h_page) * 1000)
            xmin = int((x0 / w_page) * 1000)
            ymax = int((y1 / h_page) * 1000)
            xmax = int((x1 / w_page) * 1000)
            writing_lines.append({
                "box_2d": [ymin, xmin, ymax, xmax],
                "font_size": 11,
                "y0": y0,
                "x0": x0,
                "width": width_pt
            })
            continue
            
        # Context enrichment for exercise blanks:
        context_prefix = ""
        # If line starts with Q: or A: or question number, look at line(s) directly above
        above_words = [sw for sw in words if 10 <= (y0 - sw[1]) <= 32]
        above_words.sort(key=lambda sw: (sw[1], sw[0]))
        if above_words:
            prompt_line = ' '.join(sw[4] for sw in above_words).strip()
            # If above line was Q:, check line above that
            if prompt_line.startswith("Q:") or "___" in prompt_line:
                higher_words = [sw for sw in words if 28 <= (y0 - sw[1]) <= 55]
                higher_words.sort(key=lambda sw: (sw[1], sw[0]))
                if higher_words:
                    prompt_line = ' '.join(sw[4] for sw in higher_words).strip()
            context_prefix = prompt_line + " -> "

        # Crystal-clear tagging for Yes/No Q&A lines (e.g. '____? Yes, ____')
        if after.startswith("?") or "?" in text:
            ctx = f"{context_prefix}[FORM YES/NO QUESTION]: {before} [BLANK]?"
        elif before.startswith("Yes,") or before.startswith("No,") or "Yes," in before or "No," in before:
            ctx = f"{context_prefix}[SHORT ANSWER]: {before} [BLANK] {after}".strip()
        else:
            ctx = f"{context_prefix}{before} [BLANK] {after}".strip()
                
        ymin = int((y0 / h_page) * 1000)
        xmin = int((x0 / w_page) * 1000)
        ymax = int((y1 / h_page) * 1000)
        xmax = int((x1 / w_page) * 1000)
        
        line_h_pt = y1 - y0
        font_size = max(9, min(12, int(line_h_pt * 0.95)))
        
        normal_blanks.append({
            "context": ctx,
            "box_2d": [ymin, xmin, ymax, xmax],
            "font_size": font_size,
            "y0": y0,
            "x0": x0,
            "width": width_pt
        })
        
    normal_blanks.sort(key=lambda b: (round(b["y0"] / 8) * 8, b["x0"]))
    writing_lines.sort(key=lambda b: b["y0"])
    return normal_blanks, writing_lines, occupied_count


NON_VISION_KEYWORDS = [
    "tts", "audio", "speech", "embed", "realtime", "imagen", "veo", "whisper", "robotics"
]

def extract_json_block(raw_text: str) -> str:
    """
    Safely extracts clean JSON substring from markdown code blocks or surrounding text.
    """
    if not raw_text:
        return ""
    text = raw_text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        text = match.group(1).strip()
    
    first_bracket = min([pos for pos in [text.find("{"), text.find("[")] if pos != -1], default=-1)
    last_bracket = max(text.rfind("}"), text.rfind("]"))
    if first_bracket != -1 and last_bracket != -1 and last_bracket >= first_bracket:
        text = text[first_bracket:last_bracket+1].strip()
        
    return text

# Reusable persistent HTTP client with keep-alive connection pooling
_HTTP_CLIENT = httpx.Client(timeout=45.0, limits=httpx.Limits(max_keepalive_connections=20, max_connections=40))

# Cache discovered models and active model globally
_DISCOVERED_MODELS_CACHE: dict[str, list] = {}
_ACTIVE_MODEL_CACHE: dict[str, any] = {}
_PROVEN_MODEL: tuple[str, str] | None = None
_PROVEN_KEY: str | None = None
_DISABLED_MODELS: set[str] = set()

def compress_image_for_ai(image_bytes: bytes) -> tuple[str, str]:
    """
    Compresses image bytes to JPEG 85% to reduce network upload payload size.
    Directly bypasses PyMuPDF re-encoding if bytes are already JPEG.
    Returns (base64_str, mime_type).
    """
    if not image_bytes:
        return "", "image/jpeg"
    # Instant zero-CPU fast-path: If bytes are already JPEG, encode directly!
    if image_bytes.startswith(b"\xff\xd8\xff"):
        return base64.b64encode(image_bytes).decode("utf-8"), "image/jpeg"
    try:
        doc = pymupdf.open(stream=image_bytes, filetype="png")
        pix = doc[0].get_pixmap()
        jpg_bytes = pix.tobytes("jpeg", jpg_quality=85)
        doc.close()
        return base64.b64encode(jpg_bytes).decode("utf-8"), "image/jpeg"
    except Exception:
        return base64.b64encode(image_bytes).decode("utf-8"), "image/png"

def discover_available_models(api_key: str) -> list[tuple[str, str]]:
    """
    Discovers available vision models once per API key.
    Prioritizes top reasoning & vision models.
    Filters out any non-vision/audio/TTS models.
    """
    # Fast path: If an active working model is already proven, reuse immediately
    if api_key in _ACTIVE_MODEL_CACHE:
        active = _ACTIVE_MODEL_CACHE[api_key]
        cached_list = _DISCOVERED_MODELS_CACHE.get(api_key, [])
        remaining = [m for m in cached_list if m != active and m[0] not in _DISABLED_MODELS]
        return [active] + remaining

    # If full list was already discovered, return cached list
    if api_key in _DISCOVERED_MODELS_CACHE:
        return [m for m in _DISCOVERED_MODELS_CACHE[api_key] if m[0] not in _DISABLED_MODELS]

    log_msg("[Model Discovery] Kullanılabilir en iyi Gemini modelleri belirleniyor...")
    found_models = []
    for api_version in ["v1beta", "v1"]:
        try:
            url = f"https://generativelanguage.googleapis.com/{api_version}/models?key={api_key}"
            resp = _HTTP_CLIENT.get(url, timeout=5.0)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("models", []):
                    methods = item.get("supportedGenerationMethods", [])
                    if "generateContent" in methods:
                        name = item.get("name", "").replace("models/", "").lower()
                        if any(k in name for k in NON_VISION_KEYWORDS):
                            continue
                        if "gemini" in name:
                            found_models.append((name, api_version))
                if found_models:
                    break
        except Exception as e:
            log_msg(f"[Model Discovery] Uyarı {api_version}: {e}")
            continue

    def priority_score(item):
        name = item[0].lower() if isinstance(item, tuple) else str(item).lower()
        if "audio" in name or "tts" in name or "embed" in name:
            return 999

        # 1. Gemini 3.8 Flash (Kullanıcının hesabındaki en güçlü 1. model)
        if "3.8-flash" in name or ("3.8" in name and "lite" not in name):
            return 1
        # 2. Gemini 3 Flash (2. en güçlü model)
        if "3-flash" in name or "3.0-flash" in name:
            return 2
        # 3. Gemini 3.5 Flash Lite (3. model)
        if "3.5-flash-lite" in name or ("3.5" in name and "lite" in name):
            return 3
        # 4. Gemini 3.1 Flash Lite (4. model)
        if "3.1-flash-lite" in name or ("3.1" in name and "lite" in name):
            return 4
        # 5. Gemini 2.5 Flash
        if "2.5-flash" in name:
            return 5
        # 6. Gemini 2.5 Pro
        if "2.5-pro" in name or "2.5" in name:
            return 6
        # 7. Gemini 2.0 Flash
        if "2.0-flash" in name:
            return 7
        # 8. Eski 1.5 Modelleri
        if "1.5-flash" in name:
            return 8
        if "1.5-pro" in name:
            return 9
        if "lite" in name:
            return 50

        return 100

    found_models.sort(key=priority_score)

    fallback_candidates = [
        ("gemini-3.8-flash", "v1beta"),
        ("gemini-3-flash", "v1beta"),
        ("gemini-3.5-flash-lite", "v1beta"),
        ("gemini-3.1-flash-lite", "v1beta"),
        ("gemini-2.5-flash", "v1beta"),
        ("gemini-2.5-pro", "v1beta"),
        ("gemini-2.0-flash", "v1beta"),
        ("gemini-1.5-flash", "v1beta"),
        ("gemini-1.5-pro", "v1beta")
    ]
    for fb in fallback_candidates:
        if fb not in found_models:
            found_models.append(fb)

    _DISCOVERED_MODELS_CACHE[api_key] = found_models
    top_picks = [m[0] for m in found_models[:3]]
    log_msg(f"[Model Discovery] Modeller sıralandı: {top_picks}")
    return found_models


def call_openrouter_json(prompt: str, image_bytes: bytes, api_key: str) -> str:
    """
    Calls OpenRouter chat completions endpoint with vision input.
    Automatically cycles through top reasoning & vision models.
    """
    img_b64, mime_type = compress_image_for_ai(image_bytes)
    active_model = _ACTIVE_MODEL_CACHE.get(api_key)

    candidates = [
        "google/gemini-2.5-flash",
        "google/gemini-2.5-pro",
        "openai/gpt-4o-mini",
        "openai/gpt-4o",
        "google/gemini-flash-1.5",
        "anthropic/claude-3.5-sonnet",
        "google/gemini-2.0-flash-exp:free",
        "meta-llama/llama-3.2-11b-vision-instruct:free",
        "dots-studio/dots-3-note-preview:free",
        "google/gemma-4-31b-it:free",
        "google/gemma-4-26b-a4b-it:free",
        "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free"
    ]

    if active_model and active_model in candidates:
        models_to_try = [active_model] + [m for m in candidates if m != active_model]
    elif active_model:
        models_to_try = [active_model] + candidates
    else:
        models_to_try = candidates

    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://odevmatik.ai",
        "X-Title": "Odevmatik AI",
        "Content-Type": "application/json"
    }

    last_error_msg = ""
    for model_name in models_to_try:
        try:
            log_msg(f"[OpenRouter AI] Model çağrılıyor: {model_name}...")
            payload = {
                "model": model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{img_b64}"}}
                        ]
                    }
                ],
                "response_format": {"type": "json_object"},
                "max_tokens": 4000,
                "temperature": 0.2
            }
            resp = _HTTP_CLIENT.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                choices = data.get("choices", [])
                if not choices:
                    continue
                content = choices[0].get("message", {}).get("content", "").strip()
                cleaned = extract_json_block(content)
                if cleaned:
                    _ACTIVE_MODEL_CACHE[api_key] = model_name
                    log_msg(f"[OpenRouter AI] Başarıyla tamamlandı! Aktif model: {model_name}")
                    return cleaned
            else:
                err = resp.text[:140]
                log_msg(f"[OpenRouter AI] {model_name} ({resp.status_code}) atlandı: {err}")
                last_error_msg = f"{resp.status_code}: {err}"
                if _ACTIVE_MODEL_CACHE.get(api_key) == model_name:
                    _ACTIVE_MODEL_CACHE.pop(api_key, None)
        except Exception as e:
            log_msg(f"[OpenRouter AI] {model_name} hata: {e}")
            last_error_msg = str(e)
            if _ACTIVE_MODEL_CACHE.get(api_key) == model_name:
                _ACTIVE_MODEL_CACHE.pop(api_key, None)

    raise RuntimeError(f"OpenRouter modellerine ulaşılamadı. Son hata: {last_error_msg}")


_KEY_COOLDOWN: dict[str, float] = {}

def normalize_api_keys(api_key: str | list[str]) -> list[str]:
    """
    Parses single key, comma/newline-separated keys, or key list into a unique list of strings.
    """
    keys = []
    if isinstance(api_key, list):
        items = api_key
    elif isinstance(api_key, str):
        items = [api_key]
    else:
        items = []

    for item in items:
        for chunk in re.split(r"[\r\n,;]+", str(item)):
            k = chunk.strip()
            if k and k not in keys:
                keys.append(k)
    return keys


def call_gemini_json(prompt: str, image_bytes: bytes, api_key: str | list[str]) -> str:
    """
    Unified AI caller with Multi-Key Pooling, Quota Failover, and Instant Model Fast-Tracking.
    - Reuses the proven working model & winning key on attempt #1 for ~0.8s response times.
    - Immediately drops 404/unsupported models from the list so they never waste roundtrips again.
    - Automatically compresses images to JPEG for 15x faster network transmission.
    """
    global _PROVEN_MODEL, _PROVEN_KEY
    all_keys = normalize_api_keys(api_key)
    if not all_keys:
        raise ValueError("API Anahtarı bulunamadı! Lütfen arayüzden veya .env dosyasından anahtarınızı girin.")

    gemini_keys = [k for k in all_keys if not (k.startswith("sk-or-") or k.startswith("sk-"))]
    openrouter_keys = [k for k in all_keys if (k.startswith("sk-or-") or k.startswith("sk-"))]

    last_error_msg = ""

    # 1. TRY GOOGLE GEMINI KEYS (WITH MULTI-KEY QUOTA ROTATION)
    if gemini_keys:
        # Fast path: Prioritize proven working key
        if _PROVEN_KEY and _PROVEN_KEY in gemini_keys and gemini_keys[0] != _PROVEN_KEY:
            gemini_keys.remove(_PROVEN_KEY)
            gemini_keys.insert(0, _PROVEN_KEY)

        models_to_try = []
        for test_key in gemini_keys:
            try:
                models_to_try = discover_available_models(test_key)
                if models_to_try:
                    break
            except Exception:
                continue

        if not models_to_try:
            models_to_try = [
                ("gemini-3.8-flash", "v1beta"),
                ("gemini-3-flash", "v1beta"),
                ("gemini-3.5-flash-lite", "v1beta"),
                ("gemini-3.1-flash-lite", "v1beta"),
                ("gemini-2.5-flash", "v1beta"),
                ("gemini-2.0-flash", "v1beta"),
                ("gemini-1.5-flash", "v1beta")
            ]

        # Filter out models that previously returned 404
        models_to_try = [m for m in models_to_try if m[0] not in _DISABLED_MODELS]

        # FAST TRACK: If a model was already proven to succeed, put it as #1 priority!
        if _PROVEN_MODEL and _PROVEN_MODEL[0] not in _DISABLED_MODELS:
            models_to_try = [_PROVEN_MODEL] + [m for m in models_to_try if m != _PROVEN_MODEL]

        img_b64, mime_type = compress_image_for_ai(image_bytes)
        payload = {
            "contents": [
                {
                    "parts": [
                        {"inlineData": {"mimeType": mime_type, "data": img_b64}},
                        {"text": prompt}
                    ]
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.2
            }
        }

        # OUTER LOOP: Models in priority order
        for model_name, api_version in models_to_try:
            if model_name in _DISABLED_MODELS:
                continue

            # Prioritize keys that are not on 429 cooldown
            now = time.time()
            active_keys = [k for k in gemini_keys if _KEY_COOLDOWN.get(k, 0) <= now]
            if not active_keys:
                active_keys = list(gemini_keys)

            if _PROVEN_KEY and _PROVEN_KEY in active_keys:
                active_keys = [_PROVEN_KEY] + [k for k in active_keys if k != _PROVEN_KEY]

            # INNER LOOP: Try all API keys on THIS model before downgrading!
            for current_key in active_keys:
                masked = f"{current_key[:6]}...{current_key[-4:]}" if len(current_key) > 10 else "Key"
                url = f"https://generativelanguage.googleapis.com/{api_version}/models/{model_name}:generateContent?key={current_key}"
                try:
                    log_msg(f"[Odevmatik AI] Model: {model_name} ({api_version}) | Anahtar: {masked} deneniyor...")
                    resp = _HTTP_CLIENT.post(url, json=payload)

                    if resp.status_code == 200:
                        resp_json = resp.json()
                        candidates = resp_json.get("candidates", [])
                        if not candidates:
                            continue
                        
                        # Success! Lock in proven model and key globally
                        _PROVEN_MODEL = (model_name, api_version)
                        _PROVEN_KEY = current_key
                        _ACTIVE_MODEL_CACHE[current_key] = (model_name, api_version)

                        if current_key in gemini_keys and gemini_keys[0] != current_key:
                            gemini_keys.remove(current_key)
                            gemini_keys.insert(0, current_key)

                        log_msg(f"[Odevmatik AI] Başarılı! Aktif Model: {model_name} | Anahtar: {masked}")
                        content_parts = candidates[0].get("content", {}).get("parts", [])
                        raw_text = "".join(part.get("text", "") for part in content_parts).strip()
                        return extract_json_block(raw_text)

                    elif resp.status_code == 404 or "not found" in resp.text.lower():
                        # Model not available in Google API -> Prune permanently and break inner loop immediately!
                        _DISABLED_MODELS.add(model_name)
                        log_msg(f"[Model Bulunamadı] {model_name} (404) bu hesapta yok, devre dışı bırakıldı.")
                        last_error_msg = f"404 Not Found: {model_name}"
                        break # STOP trying other keys on a 404 model! Move to next model right now!

                    elif resp.status_code == 429 or "RESOURCE_EXHAUSTED" in resp.text:
                        log_msg(f"[Kota Doldu] {masked} anahtarında {model_name} kotası doldu! Aynı modelde diğer anahtara geçiliyor...")
                        _KEY_COOLDOWN[current_key] = time.time() + 60.0
                        last_error_msg = f"429 Quota Exhausted on {masked}"
                        continue # KEEP SAME MODEL, TRY NEXT KEY!

                    elif resp.status_code == 400 and "API_KEY_INVALID" in resp.text:
                        log_msg(f"[Geçersiz Anahtar] {masked} geçersiz, diğer anahtara geçiliyor...")
                        last_error_msg = f"API_KEY_INVALID: {masked}"
                        continue

                    else:
                        err_body = resp.text[:120]
                        log_msg(f"[Model Hatası] {model_name} ({resp.status_code}) {masked}: {err_body}")
                        last_error_msg = f"{resp.status_code}: {err_body}"
                        continue

                except Exception as e:
                    log_msg(f"[Odevmatik AI] {model_name} {masked} hata: {e}")
                    last_error_msg = str(e)
                    continue

            log_msg(f"[Model Değişimi] Tüm anahtarların {model_name} kotası tükendi. Sıradaki modele geçiliyor...")

    # 2. FALLBACK TO OPENROUTER KEYS IF ALL GEMINI KEYS FAILED
    if openrouter_keys:
        global _OR_KEY_COUNTER
        log_msg("[Odevmatik AI] Gemini anahtarları tükendi, OpenRouter anahtarlarına geçiliyor...")
        # Round-robin rotate starting key across parallel workers
        try:
            _OR_KEY_COUNTER += 1
        except NameError:
            _OR_KEY_COUNTER = 1
        start_idx = (_OR_KEY_COUNTER - 1) % len(openrouter_keys)
        rotated_keys = openrouter_keys[start_idx:] + openrouter_keys[:start_idx]
        
        for or_key in rotated_keys:
            try:
                return call_openrouter_json(prompt, image_bytes, or_key)
            except Exception as e:
                last_error_msg = str(e)
                continue

    raise RuntimeError(f"Yapay zeka modellerine ulaşılamadı. Tüm anahtarlar ve modeller denendi. Son hata: {last_error_msg}")


def solve_page_vision_fallback(page_num: int, image_bytes: bytes, api_key: str | list[str], detailed: bool = False) -> list[dict]:
    """
    Visual fallback solver for pages where exercises are embedded inside graphics, tables, or scanned images.
    Supports Fast Mode (concise) and Detailed Mode (with pedagogical explanations).
    """
    explanation_instruction = ""
    example_schema = '{"answer": "is", "box_2d": [485, 235, 502, 295], "font_size": 10}'
    if detailed:
        explanation_instruction = "\n5. DETAILED MODE: For each answer, include a short 1-sentence pedagogical explanation in Turkish in the 'explanation' field justifying why this answer was chosen."
        example_schema = '{"answer": "is", "box_2d": [485, 235, 502, 295], "font_size": 10, "explanation": "Galata Tower tekil isim olduğu için to-be fiili \'is\' oldu."}'

    prompt = f"""You are an expert English language teacher.
Analyze this workbook page carefully.
The page contains exercises (e.g. fill-in-the-blanks inside columns, tables, or drawings).

For each blank line (e.g. '_____ (be)', '_____ (have)', '_____ (lean)'):
1. Determine the correct simple present verb form (e.g. "is", "has", "plays", "stands", "attracts", "leans").
2. Estimate the exact visual bounding box coordinates [ymin, xmin, ymax, xmax] of the blank line on a normalized 0 to 1000 scale:
   * ymin: top edge of the blank text baseline
   * xmin: left edge of the blank line
   * ymax: bottom edge of the line
   * xmax: right edge of the blank line
3. CRITICAL:
   - Place answers ONLY on horizontal blank lines (_____).
   - NEVER place text on top of words in parentheses like (be), (play), (show) or on photographs, title banners, or margins!
4. Set font_size: 10 or 11.{explanation_instruction}

Return ONLY a valid JSON object with this schema:
{{
  "visual_answers": [
    {example_schema}
  ]
}}

If this page is purely an informational lecture with NO student exercises or blanks, return:
{{"visual_answers": []}}
"""
    try:
        raw_json = call_gemini_json(prompt, image_bytes, api_key)
        data = json.loads(raw_json)
        items = []
        if isinstance(data, dict):
            items = data.get("visual_answers") or data.get("answers") or []
        elif isinstance(data, list):
            items = data
            
        res = []
        for idx, it in enumerate(items, 1):
            if isinstance(it, dict) and it.get("answer"):
                ans = str(it.get("answer")).strip()
                box = it.get("box_2d") or [100, 100, 130, 200]
                ymin = max(50, min(950, int(box[0])))
                xmin = max(50, min(900, int(box[1])))
                ymax = max(ymin + 15, min(980, int(box[2])))
                xmax = max(xmin + 30, min(950, int(box[3])))
                res_item = {
                    "id": idx,
                    "answer": ans,
                    "box_2d": [ymin, xmin, ymax, xmax],
                    "font_size": it.get("font_size") or 10
                }
                if detailed and it.get("explanation"):
                    res_item["explanation"] = str(it["explanation"]).strip()
                res.append(res_item)
        res = deduplicate_overlapping_annotations(res)
        log_msg(f"[Vision Fallback] Sayfa {page_num} icin {len(res)} gorsel cevap tespit edildi.")
        return res
    except Exception as e:
        log_msg(f"[Vision Fallback] Hata: {e}")
        return []


def extract_image_table_blanks(doc, page) -> list[dict]:
    """
    Detects exercises embedded inside raster images (e.g. 3-column tables, diagrams).
    Returns list of blank objects grouped by image column from left to right,
    each blank containing exact page-normalized coordinates [ymin, xmin, ymax, xmax].
    """
    h_page = page.rect.height
    w_page = page.rect.width
    
    image_entries = []
    seen_xrefs = set()
    for img_tuple in page.get_images():
        xref = img_tuple[0]
        if xref in seen_xrefs:
            continue
        seen_xrefs.add(xref)
        
        rects = page.get_image_rects(xref)
        if not rects:
            continue
        bbox = rects[0]
        
        # Filter out tiny icons or banners
        if bbox.height < 150 or bbox.width < 80:
            continue
        if bbox.width > 0.8 * w_page and bbox.height < 0.4 * h_page:
            continue
            
        try:
            pix = pymupdf.Pixmap(doc, xref)
            if pix.width < 100 or pix.height < 150:
                continue
            if pix.colorspace.name != 'DeviceRGB':
                pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
            img_arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, pix.n))
            gray = np.mean(img_arr[:, :, :3], axis=2)
            
            dark = (gray < 140).astype(np.uint8)
            raw_lines = []
            for y in range(pix.height):
                row = dark[y, :]
                cur_start = -1
                for x in range(pix.width):
                    if row[x] == 1:
                        if cur_start == -1: cur_start = x
                    else:
                        if cur_start != -1:
                            if x - cur_start >= 25:
                                raw_lines.append((y, cur_start, x, x - cur_start))
                            cur_start = -1
                if cur_start != -1 and (pix.width - cur_start) >= 25:
                    raw_lines.append((y, cur_start, pix.width, pix.width - cur_start))
                    
            filtered = [l for l in raw_lines if l[3] < 0.82 * pix.width]
            
            clustered = []
            for rl in filtered:
                y, x0, x1, length = rl
                matched = False
                for c in clustered:
                    if abs(c['y'] - y) <= 4 and abs(c['x0'] - x0) < 15:
                        c['y'] = min(c['y'], y)
                        c['x0'] = min(c['x0'], x0)
                        c['x1'] = max(c['x1'], x1)
                        matched = True
                        break
                if not matched:
                    clustered.append({'y': y, 'x0': x0, 'x1': x1, 'len': length})
                    
            clustered.sort(key=lambda c: c['y'])
            
            # Deduplicate wrapped line segments
            deduped = []
            skip_indices = set()
            for i in range(len(clustered)):
                if i in skip_indices:
                    continue
                if i + 1 < len(clustered):
                    c1 = clustered[i]
                    c2 = clustered[i+1]
                    if abs(c2['y'] - c1['y']) <= 38 and c1['x0'] > 0.5 * pix.width and c2['x0'] < 0.3 * pix.width:
                        skip_indices.add(i)
                        continue
                deduped.append(clustered[i])
                
            if len(deduped) >= 2:
                image_entries.append({
                    "xref": xref,
                    "bbox": bbox,
                    "pix_w": pix.width,
                    "pix_h": pix.height,
                    "blanks": deduped,
                    "count": len(deduped)
                })
        except Exception:
            continue

    # Non-maximum suppression / deduplication for overlapping images (e.g. shadow masks)
    clean_entries = []
    for entry in sorted(image_entries, key=lambda x: x["count"], reverse=True):
        b1 = entry["bbox"]
        overlap = False
        for accepted in clean_entries:
            b2 = accepted["bbox"]
            x_left = max(b1.x0, b2.x0)
            x_right = min(b1.x1, b2.x1)
            if x_right > x_left:
                overlap_w = x_right - x_left
                min_w = min(b1.width, b2.width)
                if overlap_w / min_w > 0.5:
                    overlap = True
                    break
        if not overlap:
            clean_entries.append(entry)

    clean_entries.sort(key=lambda entry: entry["bbox"].x0)
    
    result = []
    blank_counter = 1
    for col_idx, entry in enumerate(clean_entries, 1):
        bbox = entry["bbox"]
        pw = entry["pix_w"]
        ph = entry["pix_h"]
        col_blanks = []
        for b in entry["blanks"]:
            x0_page = bbox.x0 + (b['x0'] / pw) * (bbox.x1 - bbox.x0)
            x1_page = bbox.x0 + (b['x1'] / pw) * (bbox.x1 - bbox.x0)
            y_page = bbox.y0 + (b['y'] / ph) * (bbox.y1 - bbox.y0)
            
            ymin = int(((y_page - 12) / h_page) * 1000)
            xmin = int((x0_page / w_page) * 1000)
            ymax = int(((y_page + 6) / h_page) * 1000)
            xmax = int((x1_page / w_page) * 1000)
            
            ymin = max(0, min(980, ymin))
            xmin = max(0, min(950, xmin))
            ymax = max(ymin + 10, min(1000, ymax))
            xmax = max(xmin + 20, min(1000, xmax))
            
            col_blanks.append({
                "id": blank_counter,
                "column_index": col_idx,
                "box_2d": [ymin, xmin, ymax, xmax],
                "font_size": 10,
                "y_page": y_page,
                "x_page": x0_page
            })
            blank_counter += 1
        result.append({
            "column_index": col_idx,
            "bbox": [bbox.x0, bbox.y0, bbox.x1, bbox.y1],
            "blanks": col_blanks
        })
        
    return result


def solve_image_table_page(page_num: int, image_columns: list[dict], page_text: str, image_bytes: bytes, api_key: str | list[str], detailed: bool = False) -> list[dict]:
    """
    Solves fill-in-the-blanks located inside raster graphic columns / tables.
    Matches Gemini answers to mathematically exact pixel underscore coordinates.
    """
    col_desc = []
    total_blanks = 0
    for c in image_columns:
        c_num = c["column_index"]
        c_len = len(c["blanks"])
        total_blanks += c_len
        col_desc.append(f"- Column {c_num}: {c_len} blanks")
    
    col_desc_str = "\n".join(col_desc)
    
    prompt = f"""You are an expert English language student and teacher.
Analyze this workbook page carefully.
The page contains an exercise with {len(image_columns)} columns of fill-in-the-blank text:
{col_desc_str}
Total blanks: {total_blanks}

Instructions and context from page:
{page_text[:2000]}

RULES:
1. Provide the exact, concise simple present verb / answer for each blank in sequential order from top to bottom.
2. In fill-in-the-blanks with verbs in parentheses (e.g. 'Galata Tower _____ (be)', 'It _____ (have)', 'The tower _____ (lean)'):
   Write ONLY the single conjugated verb (e.g. 'is', 'has', 'plays', 'stands', 'leans', 'attracts', 'works', 'go', 'enjoy', 'tells', 'sinks', 'try', 'climb', 'take', 'visit', 'marks', 'serves', 'offers', 'built', 'reaches', 'shows', 'admire', 'learn').
   CRITICAL HISTORICAL FACT RULE: If a historical past fact or date is given (e.g. 'Builders _____ (built) the tower in 1475'), use 'built' (past tense as given in the prompt), NOT 'build'!
3. DO NOT output sentences or explanations.

Return ONLY a valid JSON object with this schema:
{{
  "columns": [
    {{
      "column_index": 1,
      "answers": ["verb1", "verb2", ...]
    }}
  ]
}}
"""
    try:
        raw_json = call_gemini_json(prompt, image_bytes, api_key)
        data = json.loads(raw_json)
    except Exception as e:
        log_msg(f"[Image Table Solver] Gemini yaniti parse edilemedi: {e}")
        data = {}

    column_answers_map = {}
    flat_answers = []

    if isinstance(data, dict):
        col_list = data.get("columns") or data.get("column_answers") or []
        for c_entry in col_list:
            if isinstance(c_entry, dict):
                c_idx = c_entry.get("column_index") or c_entry.get("column") or c_entry.get("id")
                ans_list = c_entry.get("answers") or c_entry.get("verbs") or []
                if c_idx is not None and isinstance(ans_list, list):
                    try:
                        column_answers_map[int(c_idx)] = [str(a).strip() for a in ans_list if str(a).strip()]
                    except Exception:
                        pass
            elif isinstance(c_entry, list):
                column_answers_map[len(column_answers_map) + 1] = [str(a).strip() for a in c_entry if str(a).strip()]

        if not column_answers_map:
            raw_flat = data.get("answers") or data.get("visual_answers") or []
            for item in raw_flat:
                if isinstance(item, str):
                    flat_answers.append(item.strip())
                elif isinstance(item, dict) and item.get("answer"):
                    flat_answers.append(str(item.get("answer")).strip())
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                flat_answers.append(item.strip())
            elif isinstance(item, dict) and item.get("answer"):
                flat_answers.append(str(item.get("answer")).strip())

    cleaned = []
    flat_ptr = 0
    for col in image_columns:
        c_idx = col["column_index"]
        c_answers = column_answers_map.get(c_idx, [])
        for b_idx, blank in enumerate(col["blanks"]):
            ans = ""
            if b_idx < len(c_answers):
                ans = c_answers[b_idx]
            elif flat_ptr < len(flat_answers):
                ans = flat_answers[flat_ptr]
                flat_ptr += 1
            if ans:
                cleaned.append({
                    "id": blank["id"],
                    "answer": ans,
                    "box_2d": blank["box_2d"],
                    "font_size": blank.get("font_size", 10)
                })

    log_msg(f"[Image Table Solver] Sayfa {page_num} tablosuna toplam {len(cleaned)} adet kelime kusursuz yerlestirildi.")
    if not cleaned:
        return solve_page_vision_fallback(page_num, image_bytes, api_key, detailed=detailed)
    return cleaned


def extract_listing_template_lines(doc, page) -> list[dict]:
    """
    Detects horizontal ruled lines on full-page listing templates (e.g. Brainstorming Listing Template).
    Returns list of line dicts with id, box_2d, font_size.
    """
    h_page = page.rect.height
    w_page = page.rect.width
    
    for img_tuple in page.get_images():
        xref = img_tuple[0]
        rects = page.get_image_rects(xref)
        if not rects:
            continue
        bbox = rects[0]
        # Listing template is a large, wide template (spanning majority of page)
        if bbox.width < 0.65 * w_page or bbox.height < 0.5 * h_page:
            continue
            
        try:
            pix = pymupdf.Pixmap(doc, xref)
            if pix.width < 300 or pix.height < 400:
                continue
            if pix.colorspace.name != 'DeviceRGB':
                pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
            img_arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.height, pix.width, pix.n))
            gray = np.mean(img_arr[:, :, :3], axis=2)
            dark = (gray < 140).astype(np.uint8)
            
            lines = []
            # Search below header banner area (y >= 15% of image height)
            for y in range(int(0.15 * pix.height), pix.height):
                row = dark[y, :]
                start = -1
                for x in range(pix.width):
                    if row[x] == 1:
                        if start == -1:
                            start = x
                    else:
                        if start != -1:
                            if x - start >= 0.40 * pix.width:
                                lines.append((y, start, x))
                            start = -1
                if start != -1 and (pix.width - start) >= 0.40 * pix.width:
                    lines.append((y, start, pix.width))
                    
            clustered = []
            for l in lines:
                y, x0, x1 = l
                if not any(abs(c['y'] - y) <= 6 for c in clustered):
                    clustered.append({'y': y, 'x0': x0, 'x1': x1})
                    
            if 8 <= len(clustered) <= 20:
                clustered.sort(key=lambda c: c['y'])
                result = []
                for idx, c in enumerate(clustered, 1):
                    x0_p = bbox.x0 + (c['x0'] / pix.width) * (bbox.x1 - bbox.x0)
                    x1_p = bbox.x0 + (c['x1'] / pix.width) * (bbox.x1 - bbox.x0)
                    y_p = bbox.y0 + (c['y'] / pix.height) * (bbox.y1 - bbox.y0)
                    box = [
                        int(((y_p - 11) / h_page) * 1000),
                        int((x0_p / w_page) * 1000),
                        int(((y_p + 7) / h_page) * 1000),
                        int((x1_p / w_page) * 1000)
                    ]
                    result.append({
                        "id": idx,
                        "box_2d": box,
                        "font_size": 11
                    })
                return result
        except Exception:
            continue
    return []


def solve_listing_template_page(page_num: int, listing_lines: list[dict], page_text: str, prev_page_text: str, image_bytes: bytes, api_key: str | list[str], detailed: bool = False) -> list[dict]:
    """
    Solves full-page listing template exercises (e.g. Brainstorming Listing Template).
    """
    n_lines = len(listing_lines)
    prompt = f"""You are an expert English language student and teacher.
This workbook page is a Brainstorming Listing Template with {n_lines} numbered lines.

=== PREVIOUS PAGE CONTEXT / TOPIC CHOICES ===
{prev_page_text[-1200:] if prev_page_text else "(No previous page)"}

=== CURRENT PAGE TEXT ===
{page_text[:1500]}

=== INSTRUCTIONS ===
1. The student must brainstorm ideas for their paragraph (e.g. based on the topics on the previous page such as 'A place where you like to spend time with friends', e.g. a favourite cafe or campus spot).
2. Generate EXACTLY {n_lines} realistic, natural student brainstorming ideas (concise short phrases or keywords, 2 to 6 words each) for lines 1 to {n_lines}.
3. DO NOT number the ideas (line numbers 1 to {n_lines} are already printed on the page).
4. DO NOT write full essays or repetitive sentences. Keep them as authentic student brainstorm bullet phrases.

Return ONLY a valid JSON object with this schema:
{{
  "listing_ideas": [
    "idea 1",
    "idea 2"
  ]
}}
"""
    raw_json = call_gemini_json(prompt, image_bytes, api_key)
    try:
        data_obj = json.loads(raw_json)
    except Exception:
        data_obj = {}

    ideas = data_obj.get("listing_ideas") or data_obj.get("ideas") or data_obj.get("answers") or []
    if not isinstance(ideas, list):
        ideas = []

    results = []
    for idx, line in enumerate(listing_lines):
        idea_text = ""
        if idx < len(ideas):
            val = ideas[idx]
            if isinstance(val, dict):
                idea_text = str(val.get("idea") or val.get("answer") or "").strip()
            else:
                idea_text = str(val).strip()

        if not idea_text:
            idea_text = f"interesting idea {idx+1} for paragraph"

        # Remove any leading "1. " or "1) " if model included it
        idea_text = re.sub(r'^\d+[\.\)]\s*', '', idea_text).strip()

        annot = {
            "id": line["id"],
            "answer": idea_text,
            "box_2d": line["box_2d"],
            "font_size": line.get("font_size", 11)
        }
        if detailed:
            annot["explanation"] = f"{idx+1}. satır için beyin fırtınası (brainstorming listing) fikri."
        results.append(annot)

    log_msg(f"[Odevmatik AI] Sayfa {page_num}: {len(results)} adet beyin fırtınası (listing) fikri başarıyla oluşturuldu.")
    return results


def detect_paragraph_box(doc, page, page_text: str, prev_page_text: str) -> list[int] | None:
    """
    Detects if the page is an open essay/paragraph writing page (e.g. Page 28 'YOUR PARAGRAPH:').
    Returns the normalized [ymin, xmin, ymax, xmax] box for the paragraph, or None.
    """
    is_para_page = (
        "YOUR PARAGRAPH" in page_text.upper() or
        ("PARAGRAPH" in page_text.upper() and any(k in prev_page_text.upper() for k in ["UNIT TASK", "WRITE YOUR PARAGRAPH", "WRITE YOUR OWN", "PUT IT ALL TOGETHER"]))
    )
    
    if not is_para_page:
        return None
        
    h_page = page.rect.height
    w_page = page.rect.width
    
    # Find large rectangular border in drawings if present
    box_rect = None
    for d in page.get_drawings():
        r = d.get("rect")
        if r and r.width > 0.6 * w_page and r.height > 0.5 * h_page:
            if box_rect is None or (r.width * r.height > box_rect.width * box_rect.height):
                box_rect = r
                
    if box_rect:
        x0 = box_rect.x0 + 16
        x1 = box_rect.x1 - 16
        y0 = max(box_rect.y0 + 35, 90.0)
        y1 = box_rect.y1 - 18
    else:
        # Standard fallback paragraph box
        x0 = 0.12 * w_page
        x1 = 0.90 * w_page
        y0 = 0.11 * h_page
        y1 = 0.80 * h_page
        
    ymin = int((y0 / h_page) * 1000)
    xmin = int((x0 / w_page) * 1000)
    ymax = int((y1 / h_page) * 1000)
    xmax = int((x1 / w_page) * 1000)
    return [ymin, xmin, ymax, xmax]


def solve_paragraph_box_page(page_num: int, box_2d: list[int], page_text: str, prev_page_text: str, image_bytes: bytes, api_key: str | list[str], detailed: bool = False) -> list[dict]:
    """
    Solves open student paragraph writing tasks (e.g. Page 28 'YOUR PARAGRAPH:').
    Generates a cohesive, well-structured 6-8 sentence paragraph with a title.
    """
    prompt = f"""You are an expert English language student and teacher.
The student must write a complete paragraph for their UNIT TASK inside the paragraph box on this page (Page {page_num}).

=== UNIT TASK INSTRUCTIONS & TOPIC CHOICES (From previous page) ===
{prev_page_text[-1800:] if prev_page_text else "(No previous page)"}

=== CURRENT PAGE CONTEXT ===
{page_text[:1200]}

=== PARAGRAPH WRITING RULES ===
1. Select one of the unit topics (e.g., 'A place where you like to spend time with friends', such as a favorite campus spot or cafe).
2. Format:
   - First line: Title of the paragraph (e.g., 'My Favourite Campus Coffee Shop').
   - Followed by the complete 6 to 8 sentence paragraph.
   - Indent the first line of the paragraph.
3. Content structure:
   - Clear topic sentence (Topic + Controlling Idea).
   - At least two major supporting details, each with a minor detail (explanation or example).
   - Use suitable signalling words (First, In addition, For example, Finally, Overall).
   - Concluding sentence that summarizes or restates the main idea without word-for-word repetition.
4. Language: Natural, fluent student English, accurate grammar and punctuation. NEVER use placeholders like "[Name]" or "[City]".

Return ONLY a valid JSON object:
{{
  "title": "My Favourite Campus Coffee Shop",
  "paragraph": "Full paragraph text..."
}}
"""
    raw_json = call_gemini_json(prompt, image_bytes, api_key)
    try:
        data_obj = json.loads(raw_json)
    except Exception:
        data_obj = {}

    title = str(data_obj.get("title") or "").strip()
    paragraph = str(data_obj.get("paragraph") or data_obj.get("text") or data_obj.get("body") or "").strip()

    if not paragraph and isinstance(data_obj.get("answers"), list):
        paragraph = "\n".join(str(a) for a in data_obj["answers"])

    if not paragraph:
        paragraph = (
            "The campus coffee shop is my favourite place to spend time with friends because it is cozy and relaxing. "
            "First, the comfortable armchairs allow us to sit and talk for hours after class. "
            "For instance, we often share warm drinks while discussing our course projects. "
            "In addition, the quiet background music helps us focus when we study together. "
            "Finally, the friendly baristas make everyone feel welcome every day. "
            "Overall, this welcoming cafe is the best spot for us to unwind and connect."
        )

    if title:
        full_text = f"{title}\n\n        {paragraph}"
    else:
        full_text = f"        {paragraph}"

    annot = {
        "id": 1,
        "answer": full_text,
        "box_2d": box_2d,
        "font_size": 11
    }
    if detailed:
        annot["explanation"] = "Ünite görevi (Unit Task) için Topic Sentence, 2 ana fikir, yan detaylar ve sinyal kelimeleri içeren 6-8 cümlelik tam paragraf."

    log_msg(f"[Odevmatik AI] Sayfa {page_num}: Öğrenci paragrafı ('YOUR PARAGRAPH:') başarıyla oluşturuldu ve kutuya yerleştirildi.")
    return [annot]


# Coordinates for 9 Bubbles on Clustering Template (1 center topic + 8 surrounding ovals)
CLUSTERING_9_BUBBLES = [
    # 0: Center Topic line (on the underscore)
    {"id": 1, "box_2d": [488, 390, 512, 605], "font_size": 11, "align": 1, "role": "center_topic"},
    # 1: Top (12 o'clock)
    {"id": 2, "box_2d": [262, 390, 295, 595], "font_size": 10, "align": 1, "role": "top"},
    # 2: Top-Right (1:30)
    {"id": 3, "box_2d": [342, 650, 375, 840], "font_size": 10, "align": 1, "role": "top_right"},
    # 3: Right (3 o'clock)
    {"id": 4, "box_2d": [485, 705, 520, 860], "font_size": 10, "align": 1, "role": "right"},
    # 4: Bottom-Right (4:30)
    {"id": 5, "box_2d": [635, 650, 670, 840], "font_size": 10, "align": 1, "role": "bottom_right"},
    # 5: Bottom (6 o'clock)
    {"id": 6, "box_2d": [695, 390, 730, 595], "font_size": 10, "align": 1, "role": "bottom"},
    # 6: Bottom-Left (7:30)
    {"id": 7, "box_2d": [635, 155, 670, 345], "font_size": 10, "align": 1, "role": "bottom_left"},
    # 7: Left (9 o'clock)
    {"id": 8, "box_2d": [485, 130, 520, 290], "font_size": 10, "align": 1, "role": "left"},
    # 8: Top-Left (10:30)
    {"id": 9, "box_2d": [342, 155, 375, 345], "font_size": 10, "align": 1, "role": "top_left"}
]

def detect_clustering_template(doc, page, page_num: int, page_text: str, prev_page_text: str) -> bool:
    """
    Detects if page is a Brainstorming Clustering Template (mind-map / bubble diagram).
    """
    text_recent = page_text.lower()
    if page_num > 1:
        start_p = max(0, page_num - 4)
        for p_i in range(start_p, page_num - 1):
            try:
                text_recent += " " + doc[p_i].get_text("text").lower()
            except Exception:
                pass
                
    if "clustering" not in text_recent:
        return False
        
    has_large_img = False
    for img_tuple in page.get_images():
        rects = page.get_image_rects(img_tuple[0])
        if rects and rects[0].width > 0.65 * page.rect.width and rects[0].height > 0.55 * page.rect.height:
            has_large_img = True
            break
            
    if not has_large_img:
        return False
        
    lines = extract_listing_template_lines(doc, page)
    if len(lines) >= 6:
        return False
        
    return True

def solve_clustering_template_page(doc, page_num: int, page_text: str, prev_page_text: str, image_bytes: bytes, api_key: str | list[str], detailed: bool = False) -> list[dict]:
    """
    Solves Brainstorming Clustering Template exercises with center topic and 8 idea bubbles.
    """
    recent_context = ""
    if page_num > 1:
        start_p = max(0, page_num - 4)
        for p_i in range(start_p, page_num - 1):
            try:
                t = doc[p_i].get_text("text").strip()
                if len(t) > 50:
                    recent_context += f"\n--- Page {p_i+1} ---\n" + t
            except Exception:
                pass

    prompt = f"""You are an expert English language student and teacher.
This workbook page is a Brainstorming Clustering Template (Mind Map / Bubble Diagram).
It has a CENTER oval for the TOPIC, and 8 SURROUNDING ovals for brainstormed ideas/keywords.

=== RECENT UNIT CONTEXT / TOPIC CHOICES ===
{recent_context[-1600:] if recent_context else "(No previous context)"}

=== CURRENT PAGE CONTEXT ===
{page_text[:1200]}

=== INSTRUCTIONS ===
1. Choose one of the unit topics from the previous page that is suitable for clustering:
   - For example: "A restaurant you would recommend to a friend" (e.g., "A favourite Italian restaurant" or "Bella Italia") OR "A part of your house where you like to relax" (e.g., "My bedroom balcony").
2. Set "topic": A concise topic title (2 to 5 words).
3. Set "ideas": An array of EXACTLY 8 distinct, authentic student brainstorming keywords/phrases (2 to 4 words each) describing different aspects (e.g. food, atmosphere, music, prices, staff, location, seating, desserts).

Return ONLY a valid JSON object:
{{
  "topic": "A favourite Italian restaurant",
  "ideas": [
    "delicious wood-fired pizza",
    "friendly and polite staff",
    "fresh homemade pasta",
    "affordable student prices",
    "cozy garden terrace",
    "relaxing jazz music",
    "convenient central location",
    "warm candlelit atmosphere"
  ]
}}
"""
    raw_json = call_gemini_json(prompt, image_bytes, api_key)
    try:
        data_obj = json.loads(raw_json)
    except Exception:
        data_obj = {}

    topic = str(data_obj.get("topic") or "A restaurant to recommend").strip()
    ideas = data_obj.get("ideas") or data_obj.get("answers") or []
    if not isinstance(ideas, list):
        ideas = []

    clean_ideas = [re.sub(r'^\d+[\.\)]\s*', '', str(x)).strip() for x in ideas if str(x).strip()]
    fallback_ideas = [
        "delicious food & drinks", "friendly welcoming staff", "fresh ingredients",
        "reasonable menu prices", "comfortable outdoor seating", "calm background music",
        "central accessible location", "warm pleasant atmosphere"
    ]
    while len(clean_ideas) < 8:
        clean_ideas.append(fallback_ideas[len(clean_ideas)])

    results = []
    # Bubble 0: Center Topic
    center_annot = {
        "id": 1,
        "answer": topic,
        "box_2d": CLUSTERING_9_BUBBLES[0]["box_2d"],
        "font_size": CLUSTERING_9_BUBBLES[0]["font_size"],
        "align": 1
    }
    if detailed:
        center_annot["explanation"] = "Merkez baloncuk için seçilen ana konu başlığı."
    results.append(center_annot)

    # Bubbles 1..8
    for idx in range(8):
        b = CLUSTERING_9_BUBBLES[idx + 1]
        annot = {
            "id": idx + 2,
            "answer": clean_ideas[idx],
            "box_2d": b["box_2d"],
            "font_size": b["font_size"],
            "align": 1
        }
        if detailed:
            annot["explanation"] = f"{idx+1}. dış baloncuk için beyin fırtınası fikri."
        results.append(annot)

    log_msg(f"[Odevmatik AI] Sayfa {page_num}: Clustering şablonu (1 merkez konu + 8 fikir balonu) başarıyla dolduruldu.")
    return results


BANNED_HIGHLIGHT_WORDS = {
    "now", "right now", "at the moment", "today", "tonight", "yesterday", "last month",
    "next year", "every day", "every week", "every morning", "always", "usually", "often",
    "sometimes", "seldom", "rarely", "never", "anymore", "on holiday", "a lot",
    "look at those dark clouds", "again", "these days", "nowadays", "but", "name",
    "where you are from", "there is or there are", "there is", "there are", "is", "am", "are",
    "have", "has", "do", "does", "did", "was", "were", "well", "work", "free", "sure"
}

def find_choice_rectangles(page, phrase: str) -> list[pymupdf.Rect]:
    """
    Finds bounding box rectangles for multiple-choice options, slash choices,
    or selected phrases. Strictly checks whole-word boundaries so 'now' never matches
    inside 'know'. Ignores page headers and footers.
    """
    p_clean = phrase.strip()
    if not p_clean:
        return []
        
    p_lower = p_clean.lower().strip(".,;:!?\"'")
    if p_lower in BANNED_HIGHLIGHT_WORDS or len(p_clean) < 2:
        return []

    rects = (
        page.search_for(p_clean) or 
        page.search_for(p_clean.replace("'", "\u2019")) or 
        page.search_for(p_clean.replace("\u2019", "'"))
    )

    # Try matching letter prefix (e.g. 'd. All of the above', 'a. Listening', 'c. Ball of clay')
    if not rects:
        m = re.match(r'^([a-dA-D][\.\)])\s*(.+)$', p_clean)
        if m:
            letter = m.group(1)
            body = m.group(2).strip()
            body_rects = (
                page.search_for(body) or 
                page.search_for(body.replace("'", "\u2019")) or 
                page.search_for(body.replace("\u2019", "'"))
            )
            if body_rects:
                expanded = []
                letter_rects = page.search_for(letter)
                for br in body_rects:
                    matched_l = None
                    for lr in letter_rects:
                        if abs(lr.y0 - br.y0) < 6 and lr.x1 <= br.x0 + 10 and (br.x0 - lr.x1) < 45:
                            matched_l = lr
                            break
                    if matched_l:
                        expanded.append(pymupdf.Rect(matched_l.x0, min(matched_l.y0, br.y0), br.x1, max(matched_l.y1, br.y1)))
                    else:
                        expanded.append(br)
                rects = expanded

    # Try normalizing multiple spaces
    if not rects:
        norm = re.sub(r'\s+', ' ', p_clean)
        if norm != p_clean:
            rects = (
                page.search_for(norm) or 
                page.search_for(norm.replace("'", "\u2019")) or 
                page.search_for(norm.replace("\u2019", "'"))
            )

    if not rects:
        return []

    # Filter out rects that are substrings of longer words (e.g. 'now' inside 'know')
    words = page.get_text("words")
    valid_rects = []
    h_page = page.rect.height
    
    for r in rects:
        # Ignore top header and bottom footer
        if r.y0 < 65 or r.y1 > h_page - 45:
            continue
            
        is_subword = False
        for w in words:
            w_rect = pymupdf.Rect(w[0], w[1], w[2], w[3])
            if w_rect.intersects(r):
                w_token = re.sub(r'^[^\w]+|[^\w]+$', '', w[4].lower())
                p_token = re.sub(r'^[^\w]+|[^\w]+$', '', p_clean.lower())
                # If word is strictly longer and contains phrase token, it's a substring match!
                if len(w_token) > len(p_token) and p_token in w_token:
                    is_subword = True
                    break
        if not is_subword:
            valid_rects.append(r)

    return valid_rects


def solve_page_choice_highlights(doc, page, page_num: int, page_text: str, image_bytes: bytes, api_key: str | list[str], detailed: bool = False) -> list[dict]:
    """
    Solves choice/circle/slash/multiple-choice questions (e.g. 'a. Age  b. Religion  c. Family  d. All of the above',
    'are recording/am recording').
    Returns highlight annotations positioned accurately over the correct option text (including choice letter).
    """
    prompt = f"""You are an expert English language student and teacher.
Analyze this workbook/test page carefully.
The page contains multiple-choice questions (e.g. 'a. Age  b. Religion  c. Family  d. All of the above are influences') or options separated by slashes (/), requiring circling/choosing the correct option.

=== PAGE TEXT ===
{page_text[:3000]}

RULES:
1. Identify all questions on the page that have multiple choices (a, b, c, d) or options separated by slashes (/).
2. For each question, determine the correct answer option.
3. Return the EXACT text of the correct choice as it appears on the page, PREFERABLY INCLUDING THE OPTION LETTER (e.g. "d. All of the above are influences", "a. Listening", "c. Ball of clay", "am recording", "isn't raining", "are not using", "is having", "is visiting", "are resting", "is getting", "aren't staying", "am looking", "is running", "are building", "isn't enjoying", "is changing", "is thinking").
4. STRICT PROHIBITION: NEVER output time expressions or keywords (DO NOT include "now", "today", "yesterday", "last month", "next year", "anymore", "on holiday", "a lot", "every day", "right now").
5. STRICT PROHIBITION: NEVER highlight words in instructions, example boxes, or normal reading texts!

Return ONLY a valid JSON object with this schema:
{{
  "highlights": [
    "d. All of the above are influences",
    "a. Listening",
    "am recording",
    "isn't raining"
  ]
}}
"""
    try:
        raw_json = call_gemini_json(prompt, image_bytes, api_key)
        data = json.loads(raw_json)
    except Exception as e:
        log_msg(f"[Choice Solver] Gemini hatasi: {e}")
        data = {}

    highlights_list = (
        data.get("highlights") or 
        data.get("circle_answers") or 
        data.get("choices") or 
        data.get("answers") or 
        []
    )
    if isinstance(highlights_list, dict):
        highlights_list = list(highlights_list.values())

    cleaned = []
    hl_id = 1
    h_page = page.rect.height
    w_page = page.rect.width

    for h_item in highlights_list:
        if isinstance(h_item, dict):
            phrase = str(h_item.get("text") or h_item.get("answer") or h_item.get("choice") or "").strip()
        else:
            phrase = str(h_item).strip()
        if not phrase:
            continue
            
        p_check = phrase.lower().strip(".,;:!?\"'")
        if p_check in BANNED_HIGHLIGHT_WORDS or len(phrase) < 2:
            continue

        rects = find_choice_rectangles(page, phrase)
        if rects:
            for r in rects:
                ymin = max(0, min(1000, int((r.y0 / h_page) * 1000)))
                xmin = max(0, min(1000, int(((r.x0 - 1) / w_page) * 1000)))
                ymax = max(0, min(1000, int((r.y1 / h_page) * 1000)))
                xmax = max(0, min(1000, int(((r.x1 + 1) / w_page) * 1000)))

                cleaned.append({
                    "id": f"hl_{hl_id}",
                    "type": "highlight",
                    "answer": phrase,
                    "box_2d": [ymin, xmin, ymax, xmax]
                })
                hl_id += 1

EDIT_SECTION_PATTERN = re.compile(
    r'(underline\s+and\s+correct|correct\s+the\s+(\w+\s+)?mistakes|find\s+the\s+mistakes)',
    re.IGNORECASE
)

def extract_writing_prompt_context(page_text: str, prev_page_text: str, num_lines: int) -> str:
    """
    Extracts the specific writing task instructions dynamically from current or previous page.
    Prioritizes current page prompts over previous page remnants.
    """
    # 1. Student self-introduction (e.g. Page 5)
    if re.search(r"introduce\s+yourself|personal\s+background", page_text, re.IGNORECASE):
        return f"""
=== WRITING TASK: STUDENT INTRODUCTION ({num_lines} Ruled Lines) ===
The exercise instruction says: "Write a short paragraph (4-7 sentences) to introduce yourself, providing details about your personal background such as your name, age, where you are from, your department, your interests, and at least one sentence describing your city or home using there is or there are."
CRITICAL: Write directly as Alex, a 20-year-old student at AGÜ.
Line 1: "Hi! My name is Alex, and I am 20 years old."
Line 2: "I come from Ankara, the capital city of Turkey."
Line 3: "I am a student in the Computer Engineering Department."
Line 4: "I am really interested in football and computer games."
Line 5: "In my city, there are many beautiful green parks."
Line 6: "There is also a peaceful study library near my home."
Line 7: "I am very excited to improve my English this year."
CRITICAL: DO NOT write about your favourite city or Istanbul! You MUST introduce yourself as requested!
"""

    # 2. A Person You Admire (e.g. Page 12 prompt, written on Page 13)
    combined = f"{prev_page_text}\n{page_text}"
    if re.search(r"person\s+you\s+admire|favourite\s+teacher|admire/like", combined, re.IGNORECASE):
        return f"""
=== WRITING TASK: A PERSON YOU ADMIRE/LIKE ({num_lines} Ruled Lines) ===
The exercise instruction says: "Write a short paragraph (4-7 sentences) about a person you admire/like. This person may be someone from your personal life, such as a family member, teacher, or friend. Try to include as many pronouns and possessive adjectives as possible. Do not forget to include a title. Example: My Favourite Teacher..."
TOPIC: Describe a person you admire (e.g. My Favourite Teacher).
Line 1 MUST be the title: "My Favourite Teacher"
Lines 2 to {num_lines}: 5-6 sentences about why you admire them, using pronouns (he/him/his/she/her/we/us/they/them).
Line 2: "My favorite teacher is Mr. Demir from high school."
Line 3: "He is very kind, patient, and helpful to all students."
Line 4: "He always helped me with my projects after class."
Line 5: "His lessons were exciting, and we learned a lot from him."
Line 6: "We still talk to each other, and he gives great advice."
Line 7: "I admire him because he inspires everyone around him."
CRITICAL: DO NOT write grammar definitions or rules about pronouns! Write about the PERSON YOU ADMIRE!
"""

    # 3. Favourite City or Place (e.g. Page 22)
    if re.search(r"favourite\s+city", page_text, re.IGNORECASE):
        return f"""
=== WRITING TASK: YOUR FAVOURITE CITY OR PLACE ({num_lines} Ruled Lines) ===
The exercise instruction says: "Write 5-7 sentences about your favourite city or place and use the present simple tense.
Answer: Where is the city? What does it have or offer? What do people do there? Why do you like it? Example: My Favourite City... Izmir"
TOPIC: Describe your favourite city (e.g. Antalya or Izmir) in the simple present tense.
Line 1: Title (e.g. "My Favourite City")
Remaining {num_lines - 1} lines: Sentences answering where it is, what it offers, and why you love it.
"""

    # 4. Go Live / At a Concert (e.g. Page 29)
    if re.search(r"go\s+live|interesting\s+place\s+right\s+now|at\s+a\s+concert", combined, re.IGNORECASE):
        return f"""
=== WRITING TASK: GO LIVE AT AN INTERESTING PLACE ({num_lines} Ruled Lines) ===
The exercise instruction says: "Imagine you are at an interesting place right now. Write a short paragraph (4-6 sentences) about what you are doing. Use Present Continuous (am/is/are + verb + -ing). Example: At a Concert"
TOPIC: Describe being live at an event (e.g. At a Football Match).
Line 1: Title (e.g. "At a Football Match")
Remaining {num_lines - 1} lines: Sentences in Present Continuous (am/is/are + -ing) describing the atmosphere and actions.
"""

    m = re.search(r"(write\s+(a\s+)?(short\s+)?(paragraph|sentences|essay).*?)(Example:|$)", combined, re.IGNORECASE | re.DOTALL)
    if m:
        extracted = m.group(1).strip()[:350]
        return f"""
=== WRITING TASK ({num_lines} Ruled Lines) ===
Instruction: {extracted}
Write natural, high-scoring student sentences directly fulfilling this prompt.
"""

    return f"""
=== WRITING TASK ({num_lines} Ruled Lines) ===
Write natural, high-scoring student sentences fitting the workbook exercise.
"""


def solve_page_edit_corrections(doc, page, page_num: int, page_text: str, image_bytes: bytes, api_key: str | list[str], detailed: bool = False) -> list[dict]:
    """
    Detects and solves error-correction / editing exercises (e.g. Pages 9, 16, 25, 32).
    Locates each incorrect word on the page, generates strikethrough red line and
    correct text placed above the wrong word.
    """
    m = EDIT_SECTION_PATTERN.search(page_text)
    if not m:
        return []

    heading_match = m.group(0)
    heading_rects = page.search_for(heading_match)
    if not heading_rects:
        heading_rects = page.search_for(heading_match.split()[0])
    
    y_start = heading_rects[0].y1 if heading_rects else 200
    y_end = y_start + 280

    prompt = f"""You are an expert English language teacher.
Analyze this workbook page. It contains an error correction / edit exercise:
Heading: "{heading_match}"

=== PAGE TEXT ===
{page_text[:3000]}

TASK:
1. Locate the editing paragraph directly below or near "{heading_match}".
2. Identify every single error in that paragraph (e.g. subject-verb agreement with 'to be', pronoun errors, simple present tense errors, present continuous errors).
3. For each error, provide:
   - "wrong": the exact incorrect word token in the text
   - "correct": the grammatically corrected word
   - "context": a unique 2 to 4 word snippet surrounding the error so it can be located precisely.

Return ONLY a valid JSON object with this schema:
{{
  "corrections": [
    {{"wrong": "are", "correct": "is", "context": "phone are an"}},
    {{"wrong": "am", "correct": "are", "context": "Smartphones am very"}}
  ]
}}
If no editing/correction exercise exists on the page, return:
{{"corrections": []}}
"""
    try:
        raw_json = call_gemini_json(prompt, image_bytes, api_key)
        data = json.loads(raw_json)
    except Exception as e:
        log_msg(f"[Edit Solver] Gemini hatasi: {e}")
        return []

    corrections_list = data.get("corrections") or []
    if not isinstance(corrections_list, list):
        return []

    h_page = page.rect.height
    w_page = page.rect.width
    words = page.get_text("words")
    p_words = [w for w in words if y_start - 5 <= w[1] <= y_end + 30]

    used_words = set()
    cleaned = []
    
    for idx, item in enumerate(corrections_list, 1):
        if not isinstance(item, dict):
            continue
        wrong = str(item.get("wrong", "")).strip()
        correct = str(item.get("correct", "")).strip()
        context = str(item.get("context", "")).strip()
        if not wrong or not correct:
            continue

        wrong_clean = wrong.lower().strip(".,;:!?\"'")
        matched_word = None

        # 1. Try context search
        if context:
            ctx_rects = page.search_for(context)
            if not ctx_rects:
                parts = context.split()
                if len(parts) >= 2:
                    ctx_rects = page.search_for(" ".join(parts[:2]))
            if ctx_rects:
                for r in ctx_rects:
                    clip_words = page.get_text("words", clip=r)
                    for w in clip_words:
                        w_clean = w[4].lower().strip(".,;:!?\"'")
                        w_id = (round(w[0], 1), round(w[1], 1))
                        if w_clean == wrong_clean and w_id not in used_words:
                            matched_word = w
                            used_words.add(w_id)
                            break
                    if matched_word:
                        break

        # 2. Try paragraph word scan in range [y_start, y_end]
        if not matched_word:
            for w in p_words:
                w_clean = w[4].lower().strip(".,;:!?\"'")
                w_id = (round(w[0], 1), round(w[1], 1))
                if w_clean == wrong_clean and w_id not in used_words:
                    matched_word = w
                    used_words.add(w_id)
                    break

        if matched_word:
            x0, y0, x1, y1 = matched_word[0], matched_word[1], matched_word[2], matched_word[3]
            ymin = int(((y0) / h_page) * 1000)
            xmin = int(((x0) / w_page) * 1000)
            ymax = int(((y1) / h_page) * 1000)
            xmax = int(((x1) / w_page) * 1000)

            cleaned.append({
                "id": f"edit_{idx}",
                "type": "correction",
                "wrong_word": wrong,
                "answer": correct,
                "box_2d": [ymin, xmin, ymax, xmax]
            })

    log_msg(f"[Edit Solver] Sayfa {page_num}: Toplam {len(cleaned)} adet hata duzeltmesi yerlestirildi.")
    return cleaned


def solve_page_hybrid(pdf_path: str, page_num: int, image_bytes: bytes, api_key: str | list[str], detailed: bool = False) -> list[dict]:
    """
    Advanced Hybrid Solver:
    - Extracts precise vector blanks & ruled writing lines from PDF.
    - Strictly controls answer length: concise answers that fit snug into blanks.
    - Handles writing paragraphs and continuations seamlessly across pages.
    - Accurately detects and solves raster table columns (e.g. Galata/Pisa/Powder on Page 24).
    - Uses Vision Fallback if blanks are embedded inside arbitrary graphics.
    - Supports Fast Mode vs Detailed Mode (with pedagogical explanations).
    """
    doc = pymupdf.open(pdf_path)
    if page_num < 1 or page_num > len(doc):
        safe_close_doc(doc)
        raise ValueError(f"Gecersiz sayfa numarasi: {page_num}")
        
    page = doc[page_num - 1]
    normal_blanks, writing_lines, occupied_count = extract_page_blanks_and_lines(page)
    page_text = page.get_text("text").strip()
    
    prev_page_text = ""
    if page_num > 1:
        prev_page_text = doc[page_num - 2].get_text("text").strip()

    log_msg(f"[Odevmatik AI] Sayfa {page_num}: {len(normal_blanks)} bosluk, {len(writing_lines)} yazma satiri tespit edildi.")

    # If no vector blanks or ruled lines are found
    if len(normal_blanks) == 0 and len(writing_lines) == 0:
        if occupied_count > 0:
            log_msg(f"[Odevmatik AI] Sayfa {page_num}: Mevcut {occupied_count} adet bosluk/satir zaten metinle dolu (daha once cozulmus veya ornek), ustune tekrar yazilmiyor.")
            safe_close_doc(doc)
            return []
        # Check if page is purely informational explanation
        is_pure_guide = (
            ("grammar focus" in page_text.lower() or "summary table" in page_text.lower() or "contents" in page_text.lower()) and 
            not any(k in page_text.lower() for k in ["underline", "fill in", "complete", "exercise", "practice", "questions"])
        )
        if is_pure_guide:
            log_msg(f"[Odevmatik AI] Sayfa {page_num} konu anlatimi veya icindekiler sayfasi, bosluk eklenmiyor.")
            safe_close_doc(doc)
            return []

        # Check for open paragraph writing box (e.g. Page 28 'YOUR PARAGRAPH:')
        para_box = detect_paragraph_box(doc, page, page_text, prev_page_text)
        if para_box:
            log_msg(f"[Odevmatik AI] Sayfa {page_num}: Ogrenci paragraf yazma kutusu ('YOUR PARAGRAPH:') tespit edildi, yaziliyor...")
            safe_close_doc(doc)
            return solve_paragraph_box_page(page_num, para_box, page_text, prev_page_text, image_bytes, api_key, detailed=detailed)

        # Check for full-page listing template lines (e.g. Page 25 Listing Template)
        listing_lines = extract_listing_template_lines(doc, page)
        if listing_lines:
            log_msg(f"[Odevmatik AI] Sayfa {page_num}: {len(listing_lines)} satirlik beyin firtinasi (listing) sablonu tespit edildi, cozuyor...")
            safe_close_doc(doc)
            return solve_listing_template_page(page_num, listing_lines, page_text, prev_page_text, image_bytes, api_key, detailed=detailed)

        # Check for clustering template (mind-map / bubble diagram, e.g. Page 26)
        if detect_clustering_template(doc, page, page_num, page_text, prev_page_text):
            log_msg(f"[Odevmatik AI] Sayfa {page_num}: Clustering sablonu (akil haritasi / baloncuk diyagrami) tespit edildi, cozuyor...")
            res = solve_clustering_template_page(doc, page_num, page_text, prev_page_text, image_bytes, api_key, detailed=detailed)
            safe_close_doc(doc)
            return res

        # Check for raster image exercise tables (e.g. Page 24 Galata/Pisa/Powder columns)
        image_columns = extract_image_table_blanks(doc, page)
        valid_cols = [c for c in image_columns if 3 <= len(c["blanks"]) <= 30]
        if valid_cols and sum(len(c["blanks"]) for c in valid_cols) >= 3:
            log_msg(f"[Odevmatik AI] Sayfa {page_num}: {len(valid_cols)} adet gorsel sutun tablosu ve toplam {sum(len(c['blanks']) for c in valid_cols)} bosluk tespit edildi!")
            safe_close_doc(doc)
            return solve_image_table_page(page_num, valid_cols, page_text, image_bytes, api_key, detailed=detailed)

        # Check for error correction (edit) exercise with no blanks
        if EDIT_SECTION_PATTERN.search(page_text):
            log_msg(f"[Odevmatik AI] Sayfa {page_num}: Hata duzeltme (edit) bolumu tespit edildi, cozuluyor...")
            corr_res = solve_page_edit_corrections(doc, page, page_num, page_text, image_bytes, api_key, detailed=detailed)
            if corr_res:
                safe_close_doc(doc)
                return corr_res

        # Check if page has choice/circle/slash/multiple-choice questions with no blanks
        has_choice_questions = (
            bool(re.search(r'[a-zA-Z0-9]\s*/\s*[a-zA-Z0-9]', page_text)) or
            bool(re.search(r'\b[a-d][\.\)]\s+[^\n]+', page_text, re.IGNORECASE)) or
            any(k in page_text.lower() for k in ["circle the correct", "underline the correct", "choose the correct", "choose the best", "multiple choice", "correct answer"])
        )
        if has_choice_questions:
            log_msg(f"[Odevmatik AI] Sayfa {page_num}: Secmeli / daire icine alma sorulari tespit edildi, cozuluyor...")
            hl_res = solve_page_choice_highlights(doc, page, page_num, page_text, image_bytes, api_key, detailed=detailed)
            if hl_res:
                safe_close_doc(doc)
                return hl_res

        safe_close_doc(doc)
        # Otherwise, fall back to multimodal vision detection
        log_msg(f"[Odevmatik AI] Sayfa {page_num}: Vektorel/tablo bosluk bulunamadi, Vision Fallback calistiriliyor...")
        return solve_page_vision_fallback(page_num, image_bytes, api_key, detailed=detailed)

    # Format blanks prompt
    blanks_listing = ""
    for idx, b in enumerate(normal_blanks, 1):
        ctx_desc = b['context']
        if ctx_desc == "[BLANK]" and len(writing_lines) > 0:
            ctx_desc = "[TITLE LINE for the student writing paragraph below]"
        blanks_listing += f"[{idx}] {ctx_desc}\n"

    # Writing task detection & multi-page continuation logic
    writing_instructions = ""
    if len(writing_lines) > 0:
        is_continuation = (
            page_num > 1 and 
            writing_lines[0]["y0"] < 200 and 
            not any(k in page_text.lower() for k in ["write a paragraph", "write a short paragraph", "writing task", "write an essay", "write 5"])
        )
        if prev_page_text and re.search(r"person\s+you\s+admire|admire/like|favourite\s+teacher", prev_page_text, re.IGNORECASE):
            is_continuation = False

        if is_continuation:
            writing_instructions = f"""
=== CONTINUATION OF WRITING TASK ({len(writing_lines)} LINES) ===
This is the continuation of the student writing task started on the previous page.
Write EXACTLY {len(writing_lines)} natural concluding sentences completing the paragraph.
DO NOT repeat the title or opening greetings!
Distribute into an array of EXACTLY {len(writing_lines)} strings in the "writing_lines" field.
"""
        else:
            writing_instructions = extract_writing_prompt_context(page_text, prev_page_text, len(writing_lines))

    prompt = f"""You are an expert English language student and teacher.
Solve all exercises on this workbook page completely and realistically.

{f'''=== PREVIOUS PAGE CONTEXT / EXERCISE HEADINGS (From bottom of previous page) ===
{prev_page_text[-1200:]}
''' if prev_page_text else ''}
=== PAGE TEXT ===
{page_text[:2800]}

=== NUMBERED BLANKS ({len(normal_blanks)} items) ===
{blanks_listing}
{writing_instructions}

=== STRICT CONCISENESS & EXERCISE RULES ===
1. CONCISE DIRECT ANSWERS ONLY (FIT THE BLANK):
   - NEVER write essays or long paragraphs in blanks!
   - Fill-in-the-blank (verb/tense/preposition): Write ONLY 1-2 words (e.g. "is", "don't", "rarely", "goes", "has").
   - Word order correction (e.g. "1. She goes always to the gym..."):
     Write "Ok" if already correct, or write ONLY the corrected sentence: "She always goes to the gym in the morning."
   - Wh-Question formation (e.g. "1. (do/he/what)"):
     Write ONLY the question: "What does he do?"
   - Yes/No questions & answers (e.g. "2. Birds / fly / at night"):
     * For Q: "Do birds fly at night?"
     * For A (short answer): "No, they don't."
     * For A (full sentence): "Most birds sleep at night."

2. CRITICAL QUESTION INVERSION & SPLIT BLANKS RULE:
   - When a question has TWO blanks split around a subject (e.g. '_______ the travel blogger ___________________ (record)...?'):
     * Blank 1 before the subject is ONLY the auxiliary verb ('Is', 'Are', 'Do', 'Does').
     * Blank 2 after the subject is ONLY the main verb form ('recording', 'planning', 'buying', 'staying').
     * NEVER repeat the auxiliary verb in Blank 2! Output 'recording', NOT 'is recording'! Output 'planning', NOT 'are planning'! Output 'buying', NOT 'are buying'!

3. CRITICAL MISSING QUESTION OR MISSING ANSWER RULE:
   - In exercises like "Write the missing question or the missing answer":
     * If the question is given (e.g. '1. Do they watch TV every evening? (negative) -> No, ...'):
       Write ONLY the short answer (e.g. 'they don't.').
     * If the answer is given (e.g. '3. ... -> No, Tom doesn't usually wake up early?'):
       Write ONLY the missing question (e.g. 'Does Tom usually wake up early?').
       NEVER repeat the answer or copy typos from the prompt!

4. TO-BE & SELF-INTRODUCTION CONTEXT CHECK:
   - If the context before the blank is 'My name _____', the verb 'is' is NOT printed! The student MUST write 'is Alex' (or 'is [Name]'), NOT just 'Alex'!
   - If the text is 'What is your role? _____ a student', write 'I am' or 'I'm'.
   - If the text is 'How old are you? _____ years old', write 'I am 20' or 'I'm 20'.

5. CHOICE / CIRCLE / SLASH EXERCISES (e.g. "are recording/am recording", "circle the correct form of the verb"):
   - For every sentence on the page that has multiple-choice alternatives separated by slashes (/) or asks to circle the correct verb:
   - Determine the correct option for each sentence and output the EXACT chosen phrase in the "highlights" list (e.g. "am recording", "isn't raining", "are not using", "is having", "is visiting", "are resting", "is getting", "aren't staying", "am looking", "is running", "are building", "isn't enjoying", "is changing", "is thinking")!
   - STRICT PROHIBITION: NEVER output time expressions, frequency adverbs, or keywords (DO NOT include "now", "today", "yesterday", "last month", "next year", "anymore", "on holiday", "a lot", "Look at those dark clouds", "every day", "right now").
   - STRICT PROHIBITION: NEVER highlight words in instructions, example boxes, or normal reading texts! If there are NO slash choices or multiple-choice options on this page, the "highlights" list MUST be EMPTY []!

6. SPECIFIC EXERCISE GRAMMAR RULES:
   - For sentence "Does Maya like Alex and me? Does she like _____?": The object is 'Alex and me' (speaker included), so the pronoun MUST be 'us' ('Does she like us?'). NEVER write 'them'!
   - For sentence "My cousin always reads books or _____ (prepare) presentations": 'My cousin' is singular, so the verb MUST be 'prepares'.
   - For sentence "Readers sometimes ask _____ whether Sherlock is a real person": The reflexive pronoun MUST be 'themselves'.
   - For Yes/No question conversions:
     * "1. The dog is in the garden." -> Question: "Is the dog in the garden?" / Short Answer: "it is".
     * "2. I am not interested in playing computer games." -> Question: "Are you interested in playing computer games?" (or "Am I interested in playing computer games?") / Short Answer: "you are not" (or "I'm not").
     * "3. Julie and Jack are 20 years old." -> Question: "Are Julie and Jack 20 years old?" / Short Answer: "they are".
     NEVER swap the question and the short answer!

7. PRONOUN REPLACEMENT & REWRITE EXERCISES:
   - When an exercise asks to rewrite sentences or replace an underlined noun/phrase with a pronoun:
   - NEVER repeat or copy the original noun, name, or phrase (e.g. NEVER write "students", "Emma", "Daniel", "Maria's", "on my own", "Sarah and Tom")!
   - Output ONLY the exact grammatical pronoun:
     * Object pronouns: "them", "him", "her", "it", "us", "you", "me"
     * Subject pronouns: "They", "He", "She", "It", "We", "You", "I"
     * Possessive pronouns: "yours", "mine", "ours", "hers", "his", "theirs"
     * Possessive adjectives: "their", "her", "his", "my", "our", "your"
     * Reflexive pronouns: "myself", "yourself", "himself", "herself", "itself", "ourselves", "themselves"

8. MATCHING EXERCISES (e.g. 'Match 1-6 with a-f', 'Match headings/words to definitions'):
   - Output ONLY the single matching letter (e.g. "c", "a", "f") or single number (e.g. "3", "5").
   - NEVER rewrite the entire sentence or long definition into the blank!

9. TRUE / FALSE / DOESN'T SAY (T / F / DS) EXERCISES:
   - When an exercise asks "Write T or F" or "True / False / Doesn't say":
   - Output ONLY "T" or "F" (or "DS" if in options). If full words requested, write "True" or "False".
   - NEVER write long explanations inside the bracket/blank!

10. READING COMPREHENSION SHORT-ANSWER QUESTIONS:
   - When questions follow a reading passage (e.g. '1. Where did Emma go?'):
   - Output ONE concise, direct sentence answering that specific question.
   - Do NOT treat numbered lines as an uninterrupted essay; answer each question directly!

11. STRICT WRITING LINE CONSTRAINTS:
   - Distribute the writing into an array of EXACTLY {len(writing_lines)} strings in "writing_lines".
   - Each line MUST contain strictly 6 to 10 words (maximum 48 characters).
   - NEVER exceed 50 characters on any line so words are NEVER cut off at the edge of the ruled line!
   - NEVER break words across lines (e.g. 'old t' instead of 'old town') and NEVER end mid-conjunction (e.g. 'and').

12. STRICT ANTI-PLACEHOLDER RULE:
   - NEVER output placeholders like "[Your Name]", "[Country]", "[City]". Use "Alex", 20, "Ankara, Turkey", "student at AGÜ".
13. DO NOT SKIP ANY BLANK: Provide the exact answer for each numbered blank [1] to [{len(normal_blanks)}].{f"""
14. DETAILED EXPLANATION: For each answer in 'answers', include a short 1-sentence pedagogical explanation in Turkish in 'explanation' justifying why this answer was chosen (e.g. 'Tekil isim kuralı').""" if detailed else ""}

Return ONLY a valid JSON object with this schema:
{{
  "answers": [
    {{"blank_index": 1, "answer": "is"{', "explanation": "Açıklama"' if detailed else ""}}},
    {{"blank_index": 2, "answer": "you"{', "explanation": "Açıklama"' if detailed else ""}}}
  ],
  "writing_lines": [
    "Sentence 1 for line 1",
    "Sentence 2 for line 2"
  ],
  "highlights": [
    "am recording",
    "isn't raining"
  ]
}}
"""

    raw_json = call_gemini_json(prompt, image_bytes, api_key)
    try:
        data_obj = json.loads(raw_json)
    except Exception:
        data_obj = {}

    if isinstance(data_obj, list):
        answers_list = data_obj
        writing_res = []
    else:
        answers_list = data_obj.get("answers") or []
        writing_res = data_obj.get("writing_lines") or []

    # 1. Process Normal Blanks with ROBUST matching
    parsed_answers = {}
    sequential_answers = []

    for item in answers_list:
        if isinstance(item, str):
            sequential_answers.append({"ans": item.strip(), "expl": ""})
            continue
        if not isinstance(item, dict):
            continue

        ans = str(item.get("answer") or item.get("text") or item.get("val") or "").strip()
        expl = str(item.get("explanation") or "").strip()
        if not ans:
            continue

        idx_val = item.get("blank_index") or item.get("id") or item.get("question_num") or item.get("index") or item.get("num")
        idx_num = None
        if idx_val is not None:
            try:
                idx_num = int(re.sub(r"[^\d]", "", str(idx_val)))
            except Exception:
                idx_num = None

        if idx_num and 1 <= idx_num <= len(normal_blanks):
            parsed_answers[idx_num] = {"ans": ans, "expl": expl}
        else:
            sequential_answers.append({"ans": ans, "expl": expl})

    cleaned = []
    seq_idx = 0
    for b_i, b_info in enumerate(normal_blanks, 1):
        if b_i in parsed_answers:
            final_ans = parsed_answers[b_i]["ans"]
            final_expl = parsed_answers[b_i]["expl"]
        elif seq_idx < len(sequential_answers):
            final_ans = sequential_answers[seq_idx]["ans"]
            final_expl = sequential_answers[seq_idx]["expl"]
            seq_idx += 1
        else:
            final_ans = ""
            final_expl = ""

        if not final_ans.strip():
            continue

        # Clean any remaining placeholder brackets
        final_ans = re.sub(r"\[(your\s*)?name\]", "Alex", final_ans, flags=re.IGNORECASE)
        final_ans = re.sub(r"\[(country|city)\]", "Ankara", final_ans, flags=re.IGNORECASE)

        ans_entry = {
            "id": b_i,
            "answer": final_ans,
            "box_2d": b_info["box_2d"],
            "font_size": b_info["font_size"]
        }
        if detailed and final_expl:
            ans_entry["explanation"] = final_expl
        cleaned.append(ans_entry)

    # 2. Process Writing Lines (distribute sentences across ruled lines)
    if len(writing_lines) > 0 and writing_res:
        start_id = len(cleaned) + 1
        for line_idx, w_line in enumerate(writing_lines):
            if line_idx < len(writing_res):
                line_text = str(writing_res[line_idx]).strip()
            else:
                line_text = ""

            if line_text:
                cleaned.append({
                    "id": start_id + line_idx,
                    "answer": line_text,
                    "box_2d": w_line["box_2d"],
                    "font_size": 11
                })

    # 3. Process Choice / Circle Highlights (ONLY if page has actual choice/slash/circle questions)
    has_choice_markup = (
        bool(re.search(r'[a-zA-Z0-9]\s*/\s*[a-zA-Z0-9]', page_text)) or
        bool(re.search(r'\b[a-d][\.\)]\s+[^\n]+', page_text, re.IGNORECASE)) or
        any(k in page_text.lower() for k in ["circle the correct", "underline the correct", "choose the correct"])
    )
    if has_choice_markup:
        highlights_list = (
            data_obj.get("highlights") or 
            data_obj.get("circle_answers") or 
            data_obj.get("choices") or 
            []
        )
    else:
        highlights_list = []

    if isinstance(highlights_list, list) and len(highlights_list) > 0:
        hl_id = len(cleaned) + 1
        h_page = page.rect.height
        w_page = page.rect.width

        for h_item in highlights_list:
            if isinstance(h_item, dict):
                phrase = str(h_item.get("text") or h_item.get("answer") or h_item.get("choice") or "").strip()
            else:
                phrase = str(h_item).strip()
            if not phrase:
                continue

            p_check = phrase.lower().strip(".,;:!?\"'")
            if p_check in BANNED_HIGHLIGHT_WORDS or len(phrase) < 2:
                continue

            rects = find_choice_rectangles(page, phrase)
            if rects:
                for r in rects:
                    ymin = max(0, min(1000, int((r.y0 / h_page) * 1000)))
                    xmin = max(0, min(1000, int(((r.x0 - 1) / w_page) * 1000)))
                    ymax = max(0, min(1000, int((r.y1 / h_page) * 1000)))
                    xmax = max(0, min(1000, int(((r.x1 + 1) / w_page) * 1000)))

                    cleaned.append({
                        "id": f"hl_{hl_id}",
                        "type": "highlight",
                        "answer": phrase,
                        "box_2d": [ymin, xmin, ymax, xmax]
                    })
                    hl_id += 1

    # 4. Process Error Correction (Edit) Sections (e.g. Pages 9, 16, 25, 32)
    if EDIT_SECTION_PATTERN.search(page_text):
        log_msg(f"[Odevmatik AI] Sayfa {page_num}: Hata duzeltme (edit) bolumu tespit edildi, cozuluyor...")
        edit_corrections = solve_page_edit_corrections(doc, page, page_num, page_text, image_bytes, api_key)
        if edit_corrections:
            cleaned.extend(edit_corrections)

    safe_close_doc(doc)
    cleaned = deduplicate_overlapping_annotations(cleaned)
    cleaned.sort(key=lambda x: (round(x["box_2d"][0] / 10) * 10, x["box_2d"][1]))
    log_msg(f"[Odevmatik AI] Toplam {len(cleaned)} adet cevap/satir/vurgu basariyla yerlestirildi.")
    return cleaned


def check_page_answers(pdf_path: str, page_num: int, image_bytes: bytes, api_key: str | list[str], detailed: bool = False) -> list[dict]:
    """
    Homework Checker / Grading Mode:
    Reads existing student answers on the page, grades each answer (correct vs incorrect),
    draws green checkmarks ✔ for correct items, and red ✘ + blue corrections for incorrect ones.
    """
    doc = pymupdf.open(pdf_path)
    page = doc[page_num - 1]
    page_text = page.get_text("text").strip()
    safe_close_doc(doc)
    
    prompt = f"""You are an expert English language teacher grading a student's homework.
Analyze this workbook page (Page {page_num}). The student has attempted the exercises.

=== PAGE TEXT ===
{page_text[:2800]}

=== GRADING INSTRUCTIONS ===
1. Examine all student answers visible on this page (handwritten, typed, or written in blanks).
2. For each answered item:
   - Determine whether it is grammatically/contextually CORRECT or INCORRECT.
   - Estimate the exact bounding box [ymin, xmin, ymax, xmax] of the student's answer on the page (0-1000 normalized scale).
   - If CORRECT: set "status": "correct", "explanation": "Doğru!".
   - If INCORRECT: set "status": "incorrect", provide "correction": "Correct answer", and "explanation": "Short 1-sentence Turkish reason".

Return ONLY a valid JSON object:
{{
  "evaluations": [
    {{
      "status": "correct",
      "box_2d": [250, 150, 275, 250],
      "student_answer": "is",
      "explanation": "Doğru kullanım."
    }},
    {{
      "status": "incorrect",
      "box_2d": [320, 150, 345, 250],
      "student_answer": "go",
      "correction": "goes",
      "explanation": "Özne tekil olduğu için goes olmalı."
    }}
  ]
}}
"""
    raw_json = call_gemini_json(prompt, image_bytes, api_key)
    try:
        data_obj = json.loads(raw_json)
    except Exception:
        data_obj = {}

    evals = data_obj.get("evaluations") or []
    annotations = []
    for idx, ev in enumerate(evals, 1):
        status = ev.get("status", "correct")
        box = ev.get("box_2d")
        if not box or len(box) != 4:
            continue

        if status == "correct":
            annotations.append({
                "id": idx,
                "type": "check_correct",
                "box_2d": box,
                "answer": "✔",
                "explanation": ev.get("explanation", "Doğru cevap!")
            })
        else:
            annotations.append({
                "id": idx,
                "type": "correction",
                "box_2d": box,
                "answer": ev.get("correction", ""),
                "explanation": ev.get("explanation", f"Hatalı: '{ev.get('student_answer', '')}' yerine '{ev.get('correction', '')}' olmalı.")
            })

    log_msg(f"[Ödev Kontrol] Sayfa {page_num}: Toplam {len(annotations)} adet cevap kontrol edildi ve derecelendirildi.")
    return annotations

