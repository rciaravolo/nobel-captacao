import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional


def setup_logging(log_dir: str = "logs") -> logging.Logger:
    """
    Configura sistema de logging com arquivo e console.
    
    Args:
        log_dir: Diretório para salvar logs
        
    Returns:
        Logger configurado
    """
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(log_dir, f"scraper_{timestamp}.log")
    error_log_file = os.path.join(log_dir, f"errors_{timestamp}.log")
    
    logger = logging.getLogger("XPerformanceScraper")
    logger.setLevel(logging.DEBUG)
    
    if logger.handlers:
        logger.handlers.clear()
    
    file_formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = logging.Formatter(
        '[%(asctime)s] %(message)s',
        datefmt='%H:%M:%S'
    )
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    error_handler = logging.FileHandler(error_log_file, encoding='utf-8')
    error_handler.setLevel(logging.WARNING)
    error_handler.setFormatter(file_formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)
    
    return logger


def validate_file_exists(filepath: str) -> bool:
    """
    Valida se um arquivo existe.
    
    Args:
        filepath: Caminho do arquivo
        
    Returns:
        True se existe, False caso contrário
    """
    return os.path.isfile(filepath)


def get_file_size(filepath: str) -> Optional[int]:
    """
    Retorna o tamanho de um arquivo em bytes.
    
    Args:
        filepath: Caminho do arquivo
        
    Returns:
        Tamanho em bytes ou None se arquivo não existe
    """
    if validate_file_exists(filepath):
        return os.path.getsize(filepath)
    return None


def format_file_size(size_bytes: int) -> str:
    """
    Formata tamanho de arquivo em formato legível.
    
    Args:
        size_bytes: Tamanho em bytes
        
    Returns:
        String formatada (ex: "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def parse_date_from_filename(filename: str) -> Optional[str]:
    """
    Extrai data do nome do arquivo no formato DD.MM.
    
    Args:
        filename: Nome do arquivo (ex: "XPerformance - 123 - Ref.15.01.pdf")
        
    Returns:
        Data no formato "DD.MM" ou None se não encontrado
    """
    import re
    pattern = r'Ref\.(\d{2}\.\d{2})'
    match = re.search(pattern, filename)
    if match:
        return match.group(1)
    return None


def get_month_from_date(date_str: str) -> Optional[str]:
    """
    Converte data DD.MM para formato YYYY-MM.
    
    Args:
        date_str: Data no formato "DD.MM"
        
    Returns:
        String no formato "YYYY-MM" ou None
    """
    try:
        day, month = date_str.split('.')
        current_year = datetime.now().year
        return f"{current_year}-{month.zfill(2)}"
    except:
        return None


def ensure_directory_exists(directory: str) -> None:
    """
    Garante que um diretório existe, criando se necessário.
    
    Args:
        directory: Caminho do diretório
    """
    Path(directory).mkdir(parents=True, exist_ok=True)


def format_duration(seconds: float) -> str:
    """
    Formata duração em formato legível.
    
    Args:
        seconds: Duração em segundos
        
    Returns:
        String formatada (ex: "1h 23min 45s")
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}min")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")
    
    return " ".join(parts)


def sanitize_filename(filename: str) -> str:
    """
    Remove caracteres inválidos de nomes de arquivo.
    
    Args:
        filename: Nome do arquivo original
        
    Returns:
        Nome do arquivo sanitizado
    """
    import re
    invalid_chars = r'[<>:"/\\|?*]'
    return re.sub(invalid_chars, '_', filename)
