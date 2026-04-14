# Script para agendar tarefa do relatório Nobel Capital
# Executa: Segunda a Sexta às 17:00

$TaskName = "Nobel_Relatorio_Captacao"
$PythonScript = "c:\Users\Usuário\vBox\Business Intelligence - Brandao (share 1)\AUTOMACOES\CAPTACAO\relatorio-captacao\main.py"
$WorkingDir = "c:\Users\Usuário\vBox\Business Intelligence - Brandao (share 1)\AUTOMACOES\CAPTACAO\relatorio-captacao"
$LogFile = "$WorkingDir\logs\task_scheduler.log"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Configurando Tarefa Nobel Capital" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Remove tarefa antiga se existir
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "Removendo tarefa antiga..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Cria ação (executar Python)
$Action = New-ScheduledTaskAction -Execute "python.exe" -Argument "main.py >> logs\task_scheduler.log 2>&1" -WorkingDirectory $WorkingDir

# Cria trigger (Segunda a Sexta às 17:00)
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At 17:00

# Configurações
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 1)

# Principal (usuário atual com senha)
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Password -RunLevel Highest

Write-Host ""
Write-Host "Criando tarefa agendada..." -ForegroundColor Green
Write-Host "IMPORTANTE: Digite sua senha do Windows quando solicitado" -ForegroundColor Yellow
Write-Host ""

# Registra tarefa
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Tarefa configurada com sucesso!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Nome: $TaskName" -ForegroundColor White
Write-Host "Horário: 17:00 - Segunda a Sexta" -ForegroundColor White
Write-Host "Modo: Executa mesmo com usuário deslogado" -ForegroundColor White
Write-Host ""
Write-Host "Para verificar: Abra o Agendador de Tarefas do Windows" -ForegroundColor Cyan
Write-Host ""
