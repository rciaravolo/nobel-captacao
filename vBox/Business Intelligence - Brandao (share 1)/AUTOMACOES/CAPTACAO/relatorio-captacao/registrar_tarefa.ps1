# ── Executar este script como ADMINISTRADOR ──────────────────
$batPath = 'c:\Users\Usuário\vBox\Business Intelligence - Brandao (share 1)\AUTOMACOES\CAPTACAO\relatorio-captacao\executar_relatorio.bat'

$action   = New-ScheduledTaskAction -Execute 'cmd.exe' -Argument "/c `"$batPath`""
$trigger  = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At 17:00
$settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 1) -StartWhenAvailable -WakeToRun $false

Register-ScheduledTask `
    -TaskName   "Nobel_Relatorio_Captacao" `
    -Action     $action `
    -Trigger    $trigger `
    -Settings   $settings `
    -RunLevel   Highest `
    -Force

Write-Host ""
Write-Host "Tarefa registrada com sucesso!" -ForegroundColor Green
Write-Host "  Nome  : Nobel_Relatorio_Captacao"
Write-Host "  Horario: 17:00 — Segunda a Sexta"
Write-Host "  Script: $batPath"
