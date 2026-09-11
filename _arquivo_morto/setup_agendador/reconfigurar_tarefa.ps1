# ── Executar este script como ADMINISTRADOR ──────────────────
# Remove a tarefa antiga
schtasks /Delete /TN "Nobel_Relatorio_Captacao" /F

# Cria nova tarefa que executa mesmo com usuário deslogado
$batPath = 'c:\Users\Usuário\vBox\Business Intelligence - Brandao (share 1)\AUTOMACOES\CAPTACAO\relatorio-captacao\executar_relatorio.bat'

$action   = New-ScheduledTaskAction -Execute 'cmd.exe' -Argument "/c `"$batPath`""
$trigger  = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At 17:00

# Settings que permitem execução mesmo deslogado
$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1) `
    -StartWhenAvailable `
    -WakeToRun $false `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries

# Principal com RunLevel Highest e que permite execução deslogado
$principal = New-ScheduledTaskPrincipal `
    -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType S4U `
    -RunLevel Highest

Register-ScheduledTask `
    -TaskName   "Nobel_Relatorio_Captacao" `
    -Action     $action `
    -Trigger    $trigger `
    -Settings   $settings `
    -Principal  $principal `
    -Force

Write-Host ""
Write-Host "Tarefa reconfigurada com sucesso!" -ForegroundColor Green
Write-Host "  Nome    : Nobel_Relatorio_Captacao"
Write-Host "  Horario : 17:00 — Segunda a Sexta"
Write-Host "  Modo    : Executa mesmo com usuario deslogado"
Write-Host "  Script  : $batPath"
