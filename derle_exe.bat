@echo off
title PrepMate PDF - EXE Paketleyici
color 0B
echo ================================================================
echo           PREPMATE PDF - Masaustu EXE Paketleyici
echo ================================================================
echo.
echo PyInstaller ile tek dosyali PrepMate-PDF.exe olusturuluyor...
echo Lutfen bekleyin (bu islem 1-2 dakika surebilir)...
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    set PYCMD=py
) else (
    set PYCMD=python
)

%PYCMD% -m PyInstaller --noconfirm --onefile --windowed --name "PrepMate-PDF" ^
    --add-data "static;static" ^
    --add-data "assets;assets" ^
    --add-data "ornek_ingilizce_odev.pdf;." ^
    --hidden-import uvicorn.logging ^
    --hidden-import uvicorn.loops ^
    --hidden-import uvicorn.loops.auto ^
    --hidden-import uvicorn.protocols ^
    --hidden-import uvicorn.protocols.http ^
    --hidden-import uvicorn.protocols.http.auto ^
    --hidden-import uvicorn.lifespan ^
    --hidden-import uvicorn.lifespan.on ^
    desktop.py

if %errorlevel% neq 0 (
    color 0C
    echo.
    echo ================================================================
    echo [HATA] Derleme sirasinda bir hata olustu!
    echo ================================================================
    pause
    exit /b 1
)

echo.
echo ================================================================
echo [BASARILI] PrepMate-PDF.exe basariyla olusturuldu!
echo Konum: dist\PrepMate-PDF.exe
echo ================================================================
echo.
pause
