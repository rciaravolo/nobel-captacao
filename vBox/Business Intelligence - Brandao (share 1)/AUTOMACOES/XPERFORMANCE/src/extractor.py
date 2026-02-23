import os
import zipfile
import logging
from pathlib import Path
from typing import List, Optional
from src.utils import ensure_directory_exists, parse_date_from_filename, get_month_from_date


class ZipExtractor:
    """
    Gerencia extração de arquivos ZIP e organização de PDFs.
    """
    
    def __init__(self, logger: logging.Logger, organize_by_month: bool = True):
        """
        Inicializa o extrator.
        
        Args:
            logger: Logger para registro de eventos
            organize_by_month: Se deve organizar PDFs por mês
        """
        self.logger = logger
        self.organize_by_month = organize_by_month
    
    def extract_zip(self, zip_path: str, extract_dir: str, delete_zip: bool = False) -> List[str]:
        """
        Extrai um arquivo ZIP.
        
        Args:
            zip_path: Caminho do arquivo ZIP
            extract_dir: Diretório de destino
            delete_zip: Se deve deletar ZIP após extração
            
        Returns:
            Lista de arquivos extraídos
        """
        extracted_files = []
        
        try:
            if not os.path.exists(zip_path):
                self.logger.error(f"Arquivo ZIP não encontrado: {zip_path}")
                return extracted_files
            
            if not zipfile.is_zipfile(zip_path):
                self.logger.error(f"Arquivo não é um ZIP válido: {zip_path}")
                return extracted_files
            
            self.logger.info(f"Extraindo: {os.path.basename(zip_path)}")
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                
                for file_name in file_list:
                    if file_name.endswith('.pdf'):
                        target_dir = self._get_target_directory(file_name, extract_dir)
                        ensure_directory_exists(target_dir)
                        
                        target_path = os.path.join(target_dir, os.path.basename(file_name))
                        
                        with zip_ref.open(file_name) as source, open(target_path, 'wb') as target:
                            target.write(source.read())
                        
                        extracted_files.append(target_path)
                
                self.logger.info(f"✓ Extraídos {len(extracted_files)} PDFs")
            
            if delete_zip and extracted_files:
                try:
                    os.remove(zip_path)
                    self.logger.debug(f"ZIP removido: {zip_path}")
                except Exception as e:
                    self.logger.warning(f"Não foi possível remover ZIP: {e}")
            
            return extracted_files
            
        except zipfile.BadZipFile:
            self.logger.error(f"Arquivo ZIP corrompido: {zip_path}")
            return extracted_files
        except Exception as e:
            self.logger.error(f"Erro ao extrair ZIP: {e}")
            return extracted_files
    
    def _get_target_directory(self, filename: str, base_dir: str) -> str:
        """
        Determina diretório de destino baseado no nome do arquivo.
        
        Args:
            filename: Nome do arquivo
            base_dir: Diretório base
            
        Returns:
            Caminho do diretório de destino
        """
        if not self.organize_by_month:
            return base_dir
        
        date_str = parse_date_from_filename(filename)
        if date_str:
            month_str = get_month_from_date(date_str)
            if month_str:
                return os.path.join(base_dir, month_str)
        
        return os.path.join(base_dir, "outros")
    
    def extract_all_zips(self, zip_dir: str, extract_dir: str, delete_zips: bool = False) -> int:
        """
        Extrai todos os ZIPs de um diretório.
        
        Args:
            zip_dir: Diretório com arquivos ZIP
            extract_dir: Diretório de destino
            delete_zips: Se deve deletar ZIPs após extração
            
        Returns:
            Total de PDFs extraídos
        """
        total_extracted = 0
        
        if not os.path.exists(zip_dir):
            self.logger.warning(f"Diretório de ZIPs não encontrado: {zip_dir}")
            return total_extracted
        
        zip_files = [f for f in os.listdir(zip_dir) if f.endswith('.zip')]
        
        if not zip_files:
            self.logger.info("Nenhum arquivo ZIP encontrado para extrair")
            return total_extracted
        
        self.logger.info(f"Encontrados {len(zip_files)} arquivos ZIP para extrair")
        
        for zip_file in zip_files:
            zip_path = os.path.join(zip_dir, zip_file)
            extracted = self.extract_zip(zip_path, extract_dir, delete_zips)
            total_extracted += len(extracted)
        
        self.logger.info(f"✓ Total de {total_extracted} PDFs extraídos de {len(zip_files)} ZIPs")
        
        return total_extracted
    
    def validate_pdf(self, pdf_path: str) -> bool:
        """
        Valida se um arquivo PDF é válido.
        
        Args:
            pdf_path: Caminho do arquivo PDF
            
        Returns:
            True se válido, False caso contrário
        """
        try:
            if not os.path.exists(pdf_path):
                return False
            
            file_size = os.path.getsize(pdf_path)
            if file_size < 1024:
                self.logger.warning(f"PDF muito pequeno (possível corrupção): {pdf_path}")
                return False
            
            with open(pdf_path, 'rb') as f:
                header = f.read(5)
                if header != b'%PDF-':
                    self.logger.warning(f"Arquivo não é um PDF válido: {pdf_path}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao validar PDF: {e}")
            return False
    
    def get_extraction_summary(self, extract_dir: str) -> dict:
        """
        Retorna resumo dos arquivos extraídos.
        
        Args:
            extract_dir: Diretório de extração
            
        Returns:
            Dicionário com estatísticas
        """
        summary = {
            "total_pdfs": 0,
            "by_month": {},
            "total_size_mb": 0
        }
        
        try:
            for root, dirs, files in os.walk(extract_dir):
                pdf_files = [f for f in files if f.endswith('.pdf')]
                
                if pdf_files:
                    month = os.path.basename(root)
                    summary["by_month"][month] = len(pdf_files)
                    summary["total_pdfs"] += len(pdf_files)
                    
                    for pdf_file in pdf_files:
                        pdf_path = os.path.join(root, pdf_file)
                        summary["total_size_mb"] += os.path.getsize(pdf_path) / (1024 * 1024)
            
            summary["total_size_mb"] = round(summary["total_size_mb"], 2)
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar resumo: {e}")
        
        return summary
