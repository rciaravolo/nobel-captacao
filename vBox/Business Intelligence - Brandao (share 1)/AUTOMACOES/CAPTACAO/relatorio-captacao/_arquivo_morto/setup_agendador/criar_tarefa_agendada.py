"""
Script para criar tarefa agendada no Windows Task Scheduler
Executa o relatório de captação diariamente às 08:00
"""
import os
import sys

def criar_tarefa_agendada():
    """
    Cria tarefa agendada usando schtasks (Windows Task Scheduler)
    """
    # Caminho do script principal
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, "main.py")
    python_exe = sys.executable
    
    # Nome da tarefa
    task_name = "Relatorio_Diario_Captacao"
    
    # Primeiro, deletar tarefa existente se houver
    delete_cmd = f'schtasks /Delete /TN "Nobel Capital\\{task_name}" /F'
    print(f"Deletando tarefa existente (se houver)...")
    os.system(delete_cmd)
    
    # Criar nova tarefa
    # /SC DAILY = executa diariamente
    # /ST 08:00 = horário de início
    # /TN = nome da tarefa com pasta
    # /TR = comando a executar
    create_cmd = (
        f'schtasks /Create '
        f'/SC DAILY '
        f'/ST 08:00 '
        f'/TN "Nobel Capital\\{task_name}" '
        f'/TR "\\"\\"{python_exe}\\"\\\" \\"\\"{script_path}\\"\\\"" '
        f'/RL HIGHEST '
        f'/F'
    )
    
    print(f"\nCriando tarefa agendada...")
    print(f"Nome: Nobel Capital\\{task_name}")
    print(f"Horário: 08:00 (diariamente)")
    print(f"Script: {script_path}")
    print(f"Python: {python_exe}")
    
    result = os.system(create_cmd)
    
    if result == 0:
        print(f"\n✓ Tarefa criada com sucesso!")
        print(f"\nVerifique no Agendador de Tarefas:")
        print(f"  - Pasta: Nobel Capital")
        print(f"  - Tarefa: {task_name}")
    else:
        print(f"\n✗ Erro ao criar tarefa. Código: {result}")
        print(f"\nTente executar este script como Administrador")
    
    return result == 0

if __name__ == "__main__":
    print("=" * 60)
    print("CRIAÇÃO DE TAREFA AGENDADA - RELATÓRIO CAPTAÇÃO")
    print("=" * 60)
    
    sucesso = criar_tarefa_agendada()
    
    print("\n" + "=" * 60)
    input("\nPressione ENTER para sair...")
