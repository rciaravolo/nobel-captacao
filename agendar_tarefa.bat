@echo off
chcp 65001 >nul
setlocal

:: ============================================================
:: agendar_tarefa.bat
:: Registra o relatório de captação no Agendador de Tarefas
:: do Windows para rodar às 17h45, Segunda a Sexta.
::
:: Execute UMA VEZ como Administrador (botão direito → Executar
:: como administrador).
:: ============================================================

set NOME_TAREFA=Nobel - Relatorio Captacao
set BAT_PATH=%~dp0executar_relatorio.bat

echo.
echo  Registrando tarefa: %NOME_TAREFA%
echo  Script: %BAT_PATH%
echo.

:: Usa PowerShell para criar a tarefa sem solicitar senha
:: "Run only when user is logged on" — necessário para Outlook via COM
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "Unregister-ScheduledTask -TaskName '%NOME_TAREFA%' -Confirm:$false -ErrorAction SilentlyContinue; " ^
  "$action  = New-ScheduledTaskAction -Execute 'cmd.exe' -Argument ('/c \"' + '%BAT_PATH%' + '\"'); " ^
  "$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At '17:45'; " ^
  "$settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 1) -StartWhenAvailable; " ^
  "Register-ScheduledTask -TaskName '%NOME_TAREFA%' -Action $action -Trigger $trigger -Settings $settings -RunLevel Limited -Force | Out-Null; " ^
  "Write-Host 'OK'"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo  SUCESSO! Tarefa agendada para rodar Segunda a Sexta as 17h45.
    echo  Para verificar : Agendador de Tarefas -^> Biblioteca -^> "%NOME_TAREFA%"
    echo  Para testar    : schtasks /run /tn "%NOME_TAREFA%"
    echo  Para ver o log : logs\task_scheduler.log
) else (
    echo.
    echo  ERRO ao registrar a tarefa. Execute como Administrador.
)

echo.
pause
