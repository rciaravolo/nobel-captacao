#!/usr/bin/env python3
"""
XPerformance PDF Scraper - Script Principal
Download em massa de relatórios PDF do portal hub.xpi.com.br
"""

import sys
import json
from pathlib import Path

from src.scraper import XPerformanceScraper
from src.utils import setup_logging, ensure_directory_exists


def load_config(config_path: str = "config/config.json") -> dict:
    """
    Carrega configurações do arquivo JSON.
    
    Args:
        config_path: Caminho do arquivo de configuração
        
    Returns:
        Dicionário de configurações
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Erro: Arquivo de configuração não encontrado: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Erro ao ler arquivo de configuração: {e}")
        sys.exit(1)


def load_assessores(assessores_path: str = "config/assessores.json") -> list:
    """
    Carrega a lista de assessores do arquivo JSON.

    Args:
        assessores_path: Caminho do arquivo de assessores

    Returns:
        Lista de nomes de assessores
    """
    try:
        with open(assessores_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        assessores = data.get("assessores", [])
        if not assessores:
            print(f"Erro: Nenhum assessor encontrado em '{assessores_path}'")
            sys.exit(1)
        return assessores
    except FileNotFoundError:
        print(f"Erro: Arquivo de assessores não encontrado: {assessores_path}")
        print("Crie o arquivo config/assessores.json com a lista de assessores.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Erro ao ler arquivo de assessores: {e}")
        sys.exit(1)


def setup_directories(config: dict) -> None:
    """
    Cria diretórios necessários.
    
    Args:
        config: Dicionário de configurações
    """
    directories = [
        config.get("download_dir", "downloads/zips"),
        config.get("extract_dir", "downloads/pdfs"),
        config.get("log_dir", "logs"),
        "checkpoints"
    ]
    
    for directory in directories:
        ensure_directory_exists(directory)


def main():
    """
    Função principal.
    """
    print("="*60)
    print("XPerformance PDF Scraper")
    print("Download em massa de relatórios XPI Hub")
    print("="*60)
    print()
    
    config = load_config()
    
    logger = setup_logging(config.get("log_dir", "logs"))
    
    setup_directories(config)
    
    assessores = load_assessores()
    logger.info(f"Assessores carregados: {len(assessores)}")
    for i, a in enumerate(assessores, 1):
        logger.info(f"  {i}. {a}")

    scraper = XPerformanceScraper(config, logger)

    if not scraper.initialize():
        logger.error("Falha ao inicializar scraper")
        sys.exit(1)

    try:
        success = scraper.run(assessores=assessores, resume=True)
        
        if success:
            logger.info("\n✓ Processo concluído com sucesso!")
            sys.exit(0)
        else:
            logger.error("\n✗ Processo concluído com erros")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.warning("\n\nExecução interrompida pelo usuário")
        logger.info("O progresso foi salvo. Execute novamente para retomar.")
        sys.exit(130)
    except Exception as e:
        logger.error(f"\n✗ Erro fatal: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
