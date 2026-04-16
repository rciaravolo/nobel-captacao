@echo off
chcp 65001 >nul
echo ============================================================
echo VERIFICACAO DA TAREFA AGENDADA
echo ============================================================
echo.

echo Consultando informacoes da tarefa...
echo.

schtasks /Query /TN "Relatorio_Diario_Captacao" /V /FO LIST

echo.
echo ============================================================
echo.
echo Deseja executar a tarefa AGORA para testar? (S/N)
set /p resposta=

if /i "%resposta%"=="S" (
    echo.
    echo Executando tarefa...
    schtasks /Run /TN "Relatorio_Diario_Captacao"
    echo.
    echo Tarefa iniciada! Verifique o log em: logs\task_scheduler.log
)

echo.
pause
