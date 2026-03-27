@echo off
chcp 65001 >nul

:: ── ENCODING FIX: força Python a usar UTF-8 mesmo ao redirecionar stdout ──
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8

cd /d "%~dp0"

echo ============================================================ >> logs\task_scheduler.log 2>&1
echo EXECUCAO INICIADA: %date% %time% >> logs\task_scheduler.log 2>&1
echo ============================================================ >> logs\task_scheduler.log 2>&1

:: ── Tenta usar o launcher 'py' (mais robusto no Agendador de Tarefas) ──
:: ── Se não encontrar, usa 'python' diretamente ──
where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    py main.py >> logs\task_scheduler.log 2>&1
) else (
    python main.py >> logs\task_scheduler.log 2>&1
)

if %ERRORLEVEL% NEQ 0 (
    echo ERRO: Script falhou com codigo %ERRORLEVEL% >> logs\task_scheduler.log 2>&1
) else (
    echo SUCESSO: Script executado com sucesso >> logs\task_scheduler.log 2>&1
)

echo ============================================================ >> logs\task_scheduler.log 2>&1
echo. >> logs\task_scheduler.log 2>&1
