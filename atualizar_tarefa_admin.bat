@echo off
chcp 65001 >nul
setlocal

:: ============================================================
:: atualizar_tarefa_admin.bat
:: Corrige as settings da tarefa "Nobel - Relatorio Captacao"
:: para permitir execução tanto com o PC bloqueado quanto
:: desbloqueado (remove restrição de bateria).
::
:: Execute como Administrador (botão direito -> Executar como
:: administrador).
:: ============================================================

set NOME_TAREFA=Nobel - Relatorio Captacao

echo.
echo  Atualizando settings da tarefa: %NOME_TAREFA%
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$s = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 10) -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew; " ^
  "Set-ScheduledTask -TaskName '%NOME_TAREFA%' -Settings $s | Out-Null; " ^
  "$t = Get-ScheduledTask -TaskName '%NOME_TAREFA%'; " ^
  "Write-Host ''; " ^
  "Write-Host ('  DisallowStartIfOnBatteries : ' + $t.Settings.DisallowStartIfOnBatteries); " ^
  "Write-Host ('  StopIfGoingOnBatteries     : ' + $t.Settings.StopIfGoingOnBatteries); " ^
  "Write-Host ('  StartWhenAvailable         : ' + $t.Settings.StartWhenAvailable); " ^
  "Write-Host ('  LogonType (Principal)      : ' + $t.Principal.LogonType); "

if %ERRORLEVEL% EQU 0 (
    echo.
    echo  SUCESSO! Tarefa agora dispara com PC ligado, bloqueado ou desbloqueado.
) else (
    echo.
    echo  ERRO ao atualizar. Execute como Administrador.
)

echo.
pause
