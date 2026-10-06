@echo off
title PrepMate PDF - Otomatik Kurulum Sihirbazi
color 0A
echo ================================================================
echo           PREPMATE PDF - Otomatik Kurulum Sihirbazi
echo ================================================================
echo.
echo Gerekli Python kutuphaneleri yukleniyor...
echo Lutfen birkac saniye bekleyin...
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
        echo PrepMate PDF'i calistirmak icin Python 3.10+ yuklu olmalidir.
        echo Simdi tarayicinizda resmi Python indirme sayfasi aciliyor...
        echo.
        echo >> ONEMLI: Kurulumu yaparken 'Add python.exe to PATH' kutucugunu
        echo            MUTLAKA isaretleyin!
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

%PYCMD% -m pip install --upgrade pip >nul 2>&1
%PYCMD% -m pip install -r requirements.txt

if not exist .env (
    if exist .env.example (
        echo.
        echo [.env] yapilandirma dosyasi olusturuluyor...
        copy .env.example .env >nul
    )
)

echo.
echo ================================================================
echo [BASARILI] Kurulum tamamlandi!
echo.
echo Simdi 'baslat.bat' dosyasina cift tiklayarak PrepMate PDF'i acabilirsin.
echo ================================================================
echo.
pause
