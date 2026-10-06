@echo off
title PrepMate PDF - AI Workbook & Homework Solver
color 0B
echo ================================================================
echo           PREPMATE PDF - AI Workbook & Homework Solver
echo ================================================================
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    where py >nul 2>&1
    if %errorlevel% neq 0 (
        color 0C
        echo ================================================================
        echo [HATA] Bilgisayarinizda Python bulunamadi!
        echo ================================================================
        echo.
        echo PrepMate PDF'i calistirmak icin once 'kurulum.bat' dosyasini calistirin
        echo veya Python'i kurun: https://www.python.org/downloads/
        echo.
        start https://www.python.org/downloads/
        pause
        exit /b 1
    ) else (
        set PYCMD=py
    )
) else (
    set PYCMD=python
)

%PYCMD% -c "import fastapi, pymupdf, httpx" >nul 2>&1
if %errorlevel% neq 0 (
    echo Gerekli kutuphaneler eksik, otomatik kuruluyor...
    %PYCMD% -m pip install -r requirements.txt
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
%PYCMD% -m uvicorn app:app --host 127.0.0.1 --port 8000

pause
