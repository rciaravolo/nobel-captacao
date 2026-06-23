@echo off
chcp 65001 >nul
setlocal

set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
set OPENBLAS_NUM_THREADS=1

cd /d "%~dp0"

echo ============================================================ >> logs\task_scheduler.log 2>&1
echo EXECUCAO INICIADA: %date% %time% >> logs\task_scheduler.log 2>&1
echo ============================================================ >> logs\task_scheduler.log 2>&1

:: Usa Python 3.14 diretamente (caminho fixo, robusto no Agendador de Tarefas)
C:\Python314\python.exe main.py >> logs\task_scheduler.log 2>&1
set EXIT_CODE=%ERRORLEVEL%

if %EXIT_CODE% NEQ 0 (
    echo ERRO: Script falhou com codigo %EXIT_CODE% >> logs\task_scheduler.log 2>&1
) else (
    echo SUCESSO: Script executado com sucesso >> logs\task_scheduler.log 2>&1
)

echo ============================================================ >> logs\task_scheduler.log 2>&1
echo. >> logs\task_scheduler.log 2>&1

exit /b %EXIT_CODE%
