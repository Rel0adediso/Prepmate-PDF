"""
PrepMate PDF - Native Desktop Application (Electron-like Experience)
Uses Windows native Microsoft Edge WebView2 for a sleek, standalone desktop app without browser tabs or address bars.
"""
import sys
import os
import threading
import time
import socket
import uvicorn
import webview
from app import app

# Ensure working directory is set to script's directory (essential when running as .exe)
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
    os.chdir(BASE_DIR)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    os.chdir(BASE_DIR)

def find_free_port(start_port=8000):
    for port in range(start_port, start_port + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
    return start_port

def run_server(port):
    # Run uvicorn quietly in background thread
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")

def main():
    port = find_free_port(8000)
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()

    # Wait for server to bind
    time.sleep(0.8)

    # Use fresh versioned webview profile directory to strictly prevent stale asset caching
    user_data_dir = os.path.join(os.path.expanduser("~"), ".prepmate_pdf", "webview_v2")
    os.makedirs(user_data_dir, exist_ok=True)

    # Launch Electron-style dedicated desktop window with cache-busting timestamp
    cache_buster = int(time.time())
    window = webview.create_window(
        title="PrepMate 2.0 Alpha 1 — AI Workbook & Co-Worker Agent",
        url=f"http://127.0.0.1:{port}/?v={cache_buster}",
        width=1440,
        height=900,
        min_size=(980, 660),
        text_select=True,
        zoomable=True
    )

    # Start webview event loop with private_mode disabled but fresh profile
    webview.start(storage_path=user_data_dir, private_mode=False, debug=False)
    sys.exit(0)

if __name__ == "__main__":
    main()
