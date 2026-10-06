@echo off
title PrepMate PDF - AI Workbook & Homework Solver
color 0B
echo ================================================================
echo           PREPMATE PDF - AI Workbook & Homework Solver
echo ================================================================
echo.

python -c "import fastapi, pymupdf, httpx" >nul 2>&1
if %errorlevel% neq 0 (
    echo Gerekli kutuphaneler eksik, otomatik kurulum yapiliyor...
    pip install -r requirements.txt
    echo.
)

if not exist .env (
    if exist .env.example (
        copy .env.example .env >nul
    )
)

echo Sunucu calistiriliyor ve tarayiciniz aciliyor...
echo Adres: http://localhost:8000
echo.

start "" "http://localhost:8000"
python -m uvicorn app:app --host 127.0.0.1 --port 8000

pause
