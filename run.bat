@echo off
echo === Khoi dong Bot Dich Thuat Telegram ===

REM Kiem tra moi truong ao
if exist venv (
    echo Kich hoat moi truong ao...
    call venv\Scripts\activate.bat
    if %ERRORLEVEL% neq 0 (
        echo Khong the kich hoat moi truong ao. Tiep tuc voi Python he thong.
    ) else (
        echo Da kich hoat moi truong ao.
    )
) else (
    echo Khong tim thay moi truong ao. Tao moi truong ao moi...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo Khong the tao moi truong ao. Tiep tuc voi Python he thong.
    ) else (
        echo Da tao moi truong ao.
        call venv\Scripts\activate.bat
        echo Cai dat cac thu vien can thiet...
        pip install -r requirements.txt
        if %ERRORLEVEL% neq 0 (
            echo Khong the cai dat cac thu vien can thiet.
            pause
            exit /b 1
        )
        echo Da cai dat cac thu vien can thiet.
    )
)

REM Kiem tra Tesseract OCR
where tesseract >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Canh bao: Tesseract OCR chua duoc cai dat hoac khong co trong PATH.
    echo Tinh nang OCR se khong hoat dong.
    echo Ban co the cai dat Tesseract OCR tu: https://github.com/UB-Mannheim/tesseract/wiki
    echo Sau khi cai dat, them duong dan vao bien moi truong PATH.
    echo Nhan phim bat ky de tiep tuc...
    pause > nul
)

REM Kiem tra file .env
if not exist .env (
    echo Khong tim thay file .env. Tao tu .env.example...
    if exist .env.example (
        copy .env.example .env
        echo Da tao file .env. Vui long cap nhat thong tin trong file .env truoc khi chay bot.
        echo Ban can cap nhat TELEGRAM_BOT_TOKEN trong file .env truoc khi tiep tuc.
        pause
        exit /b 1
    ) else (
        echo Khong tim thay file .env.example. Vui long tao file .env thu cong.
        pause
        exit /b 1
    )
)

REM Chay bot
echo Dang chay bot...
python run.py

REM Kiem tra ket qua
if %ERRORLEVEL% neq 0 (
    echo Bot da dung voi loi.
    pause
    exit /b 1
)

pause 