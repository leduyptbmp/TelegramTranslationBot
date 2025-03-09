@echo off
echo === Cai dat Bot Dich Thuat Telegram ===

REM Kiem tra Python
echo Kiem tra cai dat Python...
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Khong tim thay Python. Vui long cai dat Python truoc khi tiep tuc.
    exit /b 1
)
python --version
echo Da tim thay Python.

REM Kiem tra pip
echo Kiem tra cai dat pip...
where pip >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Khong tim thay pip. Vui long cai dat pip truoc khi tiep tuc.
    exit /b 1
)
pip --version
echo Da tim thay pip.

REM Kiem tra va tao moi truong ao
echo Kiem tra va tao moi truong ao...
if not exist venv (
    echo Tao moi truong ao moi...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo Khong the tao moi truong ao. Vui long cai dat venv: pip install virtualenv
        exit /b 1
    )
    echo Da tao moi truong ao.
) else (
    echo Moi truong ao da ton tai.
)

REM Kich hoat moi truong ao
echo Kich hoat moi truong ao...
call venv\Scripts\activate.bat
if %ERRORLEVEL% neq 0 (
    echo Khong the kich hoat moi truong ao.
    exit /b 1
)
echo Da kich hoat moi truong ao.

REM Cai dat cac thu vien
echo Cai dat cac thu vien can thiet...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Khong the cai dat cac thu vien can thiet.
    exit /b 1
)
echo Da cai dat cac thu vien can thiet.

REM Kiem tra file .env
echo Kiem tra file .env...
if not exist .env (
    echo Tao file .env tu .env.example...
    copy .env.example .env
    echo Da tao file .env. Vui long cap nhat thong tin trong file .env truoc khi chay bot.
) else (
    echo File .env da ton tai.
)

echo === Cai dat hoan tat ===
echo De chay bot, hay thuc hien cac buoc sau:
echo 1. Cap nhat thong tin trong file .env
echo 2. Kich hoat moi truong ao: venv\Scripts\activate.bat
echo 3. Chay bot: python run.py

pause 