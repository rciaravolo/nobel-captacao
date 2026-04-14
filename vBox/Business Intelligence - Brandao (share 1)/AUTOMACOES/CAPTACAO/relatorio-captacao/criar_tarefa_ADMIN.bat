@echo off
echo ============================================================
echo CRIACAO DE TAREFA AGENDADA - RELATORIO CAPTACAO
echo ============================================================
echo.
echo IMPORTANTE: Execute este arquivo como Administrador!
echo (Botao direito -^> Executar como administrador)
echo.
pause

cd /d "%~dp0"
python criar_tarefa_agendada.py

pause
