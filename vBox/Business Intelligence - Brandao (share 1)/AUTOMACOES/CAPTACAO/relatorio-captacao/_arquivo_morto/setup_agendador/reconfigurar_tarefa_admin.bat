@echo off
echo ========================================
echo Reconfigurando Tarefa Nobel
echo ========================================
echo.

REM Remove tarefa antiga
schtasks /Delete /TN "Nobel_Relatorio_Captacao" /F

echo.
echo Criando nova tarefa...
echo IMPORTANTE: Quando solicitado, digite sua senha do Windows
echo.

REM Cria nova tarefa com LogonType Password (executa mesmo deslogado)
schtasks /Create /XML "c:\Users\Usuário\vBox\Business Intelligence - Brandao (share 1)\AUTOMACOES\CAPTACAO\relatorio-captacao\tarefa_nobel.xml" /TN "Nobel_Relatorio_Captacao" /RU "%USERDOMAIN%\%USERNAME%" /RP

echo.
echo ========================================
echo Tarefa reconfigurada!
echo Modo: Executa mesmo com usuario deslogado
echo Horario: 17:00 - Segunda a Sexta
echo ========================================
pause
