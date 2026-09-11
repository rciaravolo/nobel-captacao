@echo off
:: push_para_postgres.bat
:: Carrega .env e envia dados Excel -> PostgreSQL VPS
:: Agendar no Task Scheduler: 16:30, Seg-Sex

setlocal

:: Diretório do script
set "SCRIPT_DIR=%~dp0"
set "LOG_DIR=%SCRIPT_DIR%logs"
set "LOG_FILE=%LOG_DIR%\push_postgres_%DATE:~6,4%%DATE:~3,2%%DATE:~0,2%_%TIME:~0,2%%TIME:~3,2%.log"

:: Remove espaço no horário (ex: " 9:00" -> "090")
set "LOG_FILE=%LOG_FILE: =0%"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo [%DATE% %TIME%] Iniciando push_para_postgres... >> "%LOG_FILE%"

:: Carrega variáveis do .env (formato KEY=VALUE, ignora linhas com #)
if exist "%SCRIPT_DIR%.env" (
    for /f "usebackq tokens=1,* delims==" %%A in ("%SCRIPT_DIR%.env") do (
        set "line=%%A"
        if not "!line:~0,1!"=="#" (
            set "%%A=%%B"
        )
    )
)

:: Ativa virtualenv se existir
if exist "%SCRIPT_DIR%venv\Scripts\activate.bat" (
    call "%SCRIPT_DIR%venv\Scripts\activate.bat"
)

:: Executa script Python
python "%SCRIPT_DIR%push_para_postgres.py" >> "%LOG_FILE%" 2>&1

if %ERRORLEVEL% NEQ 0 (
    echo [%DATE% %TIME%] ERRO ao executar push_para_postgres.py (code %ERRORLEVEL%) >> "%LOG_FILE%"
    exit /b %ERRORLEVEL%
)

echo [%DATE% %TIME%] Push concluido com sucesso. >> "%LOG_FILE%"
endlocal
