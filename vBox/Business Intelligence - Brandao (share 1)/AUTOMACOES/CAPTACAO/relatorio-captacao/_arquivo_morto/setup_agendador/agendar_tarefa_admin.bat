@echo off
echo ========================================
echo Agendando Tarefa Nobel Capital
echo ========================================
echo.
echo Este script vai configurar o agendamento automatico
echo Horario: 17:00 - Segunda a Sexta
echo.
echo IMPORTANTE: Execute como ADMINISTRADOR
echo.
pause

PowerShell -NoProfile -ExecutionPolicy Bypass -File "%~dp0agendar_tarefa.ps1"

pause
