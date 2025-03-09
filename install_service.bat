@echo off
echo === Cai dat Bot Dich Thuat Telegram nhu mot Service ===

REM Kiem tra quyen admin
net session >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Ban can chay script nay voi quyen Administrator.
    echo Vui long click chuot phai va chon "Run as administrator".
    pause
    exit /b 1
)

REM Lay duong dan tuyet doi cua thu muc hien tai
set "CURRENT_DIR=%cd%"

REM Kiem tra NSSM
where nssm >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo NSSM (Non-Sucking Service Manager) chua duoc cai dat.
    echo Ban co muon tai NSSM khong? (Y/N)
    set /p download_nssm=
    if /i "%download_nssm%"=="Y" (
        echo Dang tai NSSM...
        powershell -Command "Invoke-WebRequest -Uri 'https://nssm.cc/release/nssm-2.24.zip' -OutFile '%TEMP%\nssm.zip'"
        echo Dang giai nen NSSM...
        powershell -Command "Expand-Archive -Path '%TEMP%\nssm.zip' -DestinationPath '%TEMP%\nssm'"
        
        REM Xac dinh kien truc he thong
        if exist "%ProgramFiles(x86)%" (
            set "NSSM_PATH=%TEMP%\nssm\nssm-2.24\win64\nssm.exe"
        ) else (
            set "NSSM_PATH=%TEMP%\nssm\nssm-2.24\win32\nssm.exe"
        )
        
        REM Tao thu muc cho NSSM
        if not exist "%ProgramFiles%\nssm" mkdir "%ProgramFiles%\nssm"
        copy "%NSSM_PATH%" "%ProgramFiles%\nssm\nssm.exe"
        
        REM Them NSSM vao PATH
        setx PATH "%PATH%;%ProgramFiles%\nssm" /M
        set "PATH=%PATH%;%ProgramFiles%\nssm"
        
        echo NSSM da duoc cai dat.
    ) else (
        echo Vui long cai dat NSSM tu https://nssm.cc/download
        echo Sau do chay lai script nay.
        pause
        exit /b 1
    )
)

REM Kiem tra moi truong ao
if not exist venv (
    echo Moi truong ao chua duoc tao. Dang tao moi truong ao...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo Khong the tao moi truong ao. Vui long cai dat venv: pip install virtualenv
        pause
        exit /b 1
    )
    echo Da tao moi truong ao.
    
    REM Kich hoat moi truong ao va cai dat cac thu vien
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo Khong the cai dat cac thu vien can thiet.
        pause
        exit /b 1
    )
    echo Da cai dat cac thu vien can thiet.
)

REM Kiem tra file .env
if not exist .env (
    echo File .env chua duoc tao. Dang tao tu .env.example...
    if exist .env.example (
        copy .env.example .env
        echo Vui long cap nhat thong tin trong file .env truoc khi tiep tuc.
        echo Nhan phim bat ky sau khi da cap nhat file .env...
        pause > nul
    ) else (
        echo Khong tim thay file .env.example. Vui long tao file .env thu cong.
        pause
        exit /b 1
    )
)

REM Tao bat file de chay bot
echo @echo off > "%CURRENT_DIR%\run_service.bat"
echo cd /d "%CURRENT_DIR%" >> "%CURRENT_DIR%\run_service.bat"
echo call venv\Scripts\activate.bat >> "%CURRENT_DIR%\run_service.bat"
echo python run.py >> "%CURRENT_DIR%\run_service.bat"

REM Cai dat service
echo Dang cai dat service...
nssm install TelegramTranslationBot "%CURRENT_DIR%\run_service.bat"
nssm set TelegramTranslationBot DisplayName "Telegram Translation Bot"
nssm set TelegramTranslationBot Description "Bot Telegram tự động dịch tin nhắn từ các kênh và bot khác"
nssm set TelegramTranslationBot AppDirectory "%CURRENT_DIR%"
nssm set TelegramTranslationBot AppStdout "%CURRENT_DIR%\logs\service.log"
nssm set TelegramTranslationBot AppStderr "%CURRENT_DIR%\logs\service_error.log"
nssm set TelegramTranslationBot AppStopMethodSkip 0
nssm set TelegramTranslationBot AppStopMethodConsole 1500
nssm set TelegramTranslationBot AppStopMethodWindow 1500
nssm set TelegramTranslationBot AppStopMethodThreads 1500
nssm set TelegramTranslationBot AppThrottle 5000
nssm set TelegramTranslationBot AppExit Default Restart
nssm set TelegramTranslationBot AppRestartDelay 10000
nssm set TelegramTranslationBot ObjectName LocalSystem

REM Tao thu muc logs
if not exist logs mkdir logs

REM Khoi dong service
echo Dang khoi dong service...
nssm start TelegramTranslationBot

echo === Cai dat hoan tat ===
echo Ban co the quan ly service bang cac lenh sau:
echo   nssm start TelegramTranslationBot - Khoi dong service
echo   nssm stop TelegramTranslationBot - Dung service
echo   nssm restart TelegramTranslationBot - Khoi dong lai service
echo   nssm status TelegramTranslationBot - Xem trang thai service
echo   nssm edit TelegramTranslationBot - Chinh sua cau hinh service
echo   nssm remove TelegramTranslationBot - Xoa service

pause 