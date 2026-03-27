@echo off
:: ============================================================
:: push_excel_github.bat
:: Copia o arquivo Excel para a pasta data/ do repositório e
:: faz commit + push para o GitHub antes das 17h.
::
:: Agendar este .bat para rodar às 16:45 (Segunda a Sexta).
:: ============================================================

chcp 65001 >nul
set PYTHONUTF8=1

cd /d "%~dp0"

set LOGFILE=%~dp0logs\push_excel.log
set EXCEL_ORIGEM=C:\Users\Usuário\vBox\ONE PAGE\ATUALIZAÇÃO - BASES ONE PAGE.xlsx
set EXCEL_DESTINO=%~dp0data\BASES_ONE_PAGE.xlsx
set ASSESSORES_ORIGEM=C:\Users\Usuário\vBox\Business Intelligence - Brandao (share 1)\AUTOMACOES\CAPTACAO\assessor.json
set ASSESSORES_DESTINO=%~dp0data\assessor.json

echo ============================================================ >> "%LOGFILE%" 2>&1
echo PUSH INICIADO: %date% %time% >> "%LOGFILE%" 2>&1
echo ============================================================ >> "%LOGFILE%" 2>&1

:: ── Cria pasta data/ se não existir ──────────────────────────
if not exist "%~dp0data" mkdir "%~dp0data"

:: ── Copia os arquivos de dados ───────────────────────────────
echo Copiando Excel... >> "%LOGFILE%" 2>&1
copy /Y "%EXCEL_ORIGEM%" "%EXCEL_DESTINO%" >> "%LOGFILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERRO: Nao foi possivel copiar o Excel. Verifique se o arquivo existe. >> "%LOGFILE%" 2>&1
    goto FIM
)

echo Copiando assessor.json... >> "%LOGFILE%" 2>&1
copy /Y "%ASSESSORES_ORIGEM%" "%ASSESSORES_DESTINO%" >> "%LOGFILE%" 2>&1

:: ── Git: adiciona, commita e faz push ────────────────────────
echo Executando git add... >> "%LOGFILE%" 2>&1
git add -f data\ >> "%LOGFILE%" 2>&1

:: Verifica se há algo para commitar
git diff --cached --quiet
if %ERRORLEVEL% EQU 0 (
    echo Sem alteracoes nos dados. Push nao necessario. >> "%LOGFILE%" 2>&1
    goto FIM
)

echo Executando git commit... >> "%LOGFILE%" 2>&1
git commit -m "dados: atualização automática %date% %time%" >> "%LOGFILE%" 2>&1

echo Executando git push... >> "%LOGFILE%" 2>&1
git push >> "%LOGFILE%" 2>&1

if %ERRORLEVEL% NEQ 0 (
    echo ERRO: git push falhou. Verifique a conexao e credenciais do GitHub. >> "%LOGFILE%" 2>&1
) else (
    echo SUCESSO: Dados enviados para o GitHub. GitHub Actions irá rodar às 17h. >> "%LOGFILE%" 2>&1
)

:FIM
echo ============================================================ >> "%LOGFILE%" 2>&1
echo. >> "%LOGFILE%" 2>&1
