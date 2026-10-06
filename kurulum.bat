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

python -m pip install --upgrade pip
pip install -r requirements.txt

if not exist .env (
    echo.
    echo [.env] yapilandirma dosyasi olusturuluyor...
    copy .env.example .env >nul
)

echo.
echo ================================================================
echo [BASARILI] Kurulum tamamlandi!
echo.
echo Simdi 'baslat.bat' dosyasina cift tiklayarak PrepMate PDF'i acabilirsin.
echo ================================================================
echo.
pause
