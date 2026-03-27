@echo off
:: ============================================================
:: push_para_cloudflare.bat
:: Envia TB_CAP e TB_POSITIVADOR para o Cloudflare D1.
::
:: Agendar via Windows Task Scheduler para rodar:
::   - 10:00 (atualização da manhã)
::   - 13:00 (atualização do almoço)
::   - 16:30 (atualização final antes do relatório das 17h)
::   Segunda a Sexta
:: ============================================================

chcp 65001 >nul
set PYTHONUTF8=1

cd /d "%~dp0"

set LOGFILE=%~dp0logs\push_cloudflare.log

echo ============================================================ >> "%LOGFILE%" 2>&1
echo PUSH CLOUDFLARE D1 INICIADO: %date% %time% >> "%LOGFILE%" 2>&1
echo ============================================================ >> "%LOGFILE%" 2>&1

:: ── Executa o script Python de push ──────────────────────────
python push_cloudflare_d1.py >> "%LOGFILE%" 2>&1

if %ERRORLEVEL% NEQ 0 (
    echo ERRO: push_cloudflare_d1.py falhou. Verifique o log acima. >> "%LOGFILE%" 2>&1
) else (
    echo SUCESSO: Dados enviados para o Cloudflare D1. >> "%LOGFILE%" 2>&1
)

echo ============================================================ >> "%LOGFILE%" 2>&1
echo. >> "%LOGFILE%" 2>&1
