import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class ProgressTracker:
    """
    Gerencia checkpoint e progresso do download.
    """
    
    def __init__(self, checkpoint_file: str = "checkpoints/download_state.json"):
        """
        Inicializa o rastreador de progresso.
        
        Args:
            checkpoint_file: Caminho do arquivo de checkpoint
        """
        self.checkpoint_file = checkpoint_file
        self.state = self._load_state()
        
    def _load_state(self) -> Dict[str, Any]:
        """
        Carrega estado do checkpoint ou cria novo.
        
        Returns:
            Dicionário com estado atual
        """
        Path(self.checkpoint_file).parent.mkdir(parents=True, exist_ok=True)
        
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erro ao carregar checkpoint: {e}")
                return self._create_new_state()
        else:
            return self._create_new_state()
    
    def _create_new_state(self) -> Dict[str, Any]:
        """
        Cria novo estado inicial.
        
        Returns:
            Dicionário com estado inicial
        """
        return {
            "last_execution": None,
            "total_batches": 0,
            "completed_batches": 0,
            "last_batch_processed": 0,
            "downloaded_files": [],
            "extracted_files": [],
            "status": "not_started",
            "errors": [],
            "start_time": None,
            "end_time": None
        }
    
    def save_state(self) -> None:
        """
        Salva estado atual no arquivo de checkpoint.
        """
        try:
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar checkpoint: {e}")
    
    def start_execution(self, total_batches: int) -> None:
        """
        Marca início de nova execução.
        
        Args:
            total_batches: Total de lotes a processar
        """
        self.state["start_time"] = datetime.now().isoformat()
        self.state["total_batches"] = total_batches
        self.state["status"] = "in_progress"
        self.save_state()
    
    def mark_batch_completed(self, batch_number: int, filename: str) -> None:
        """
        Marca um lote como concluído.
        
        Args:
            batch_number: Número do lote
            filename: Nome do arquivo baixado
        """
        self.state["completed_batches"] += 1
        self.state["last_batch_processed"] = batch_number
        
        if filename not in self.state["downloaded_files"]:
            self.state["downloaded_files"].append(filename)
        
        self.state["last_execution"] = datetime.now().isoformat()
        self.save_state()
    
    def mark_file_extracted(self, filename: str) -> None:
        """
        Marca um arquivo como extraído.
        
        Args:
            filename: Nome do arquivo extraído
        """
        if filename not in self.state["extracted_files"]:
            self.state["extracted_files"].append(filename)
        self.save_state()
    
    def add_error(self, error_msg: str, batch_number: Optional[int] = None) -> None:
        """
        Adiciona erro ao log.
        
        Args:
            error_msg: Mensagem de erro
            batch_number: Número do lote (opcional)
        """
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "message": error_msg,
            "batch": batch_number
        }
        self.state["errors"].append(error_entry)
        self.save_state()
    
    def complete_execution(self, success: bool = True) -> None:
        """
        Marca execução como concluída.
        
        Args:
            success: Se a execução foi bem-sucedida
        """
        self.state["end_time"] = datetime.now().isoformat()
        self.state["status"] = "completed" if success else "failed"
        self.save_state()
    
    def is_batch_completed(self, batch_number: int) -> bool:
        """
        Verifica se um lote já foi processado.
        
        Args:
            batch_number: Número do lote
            
        Returns:
            True se já foi processado
        """
        return batch_number <= self.state["last_batch_processed"]
    
    def get_resume_point(self) -> int:
        """
        Retorna o ponto de retomada.
        
        Returns:
            Número do próximo lote a processar
        """
        return self.state["last_batch_processed"] + 1
    
    def get_progress_percentage(self) -> float:
        """
        Calcula percentual de progresso.
        
        Returns:
            Percentual (0-100)
        """
        if self.state["total_batches"] == 0:
            return 0.0
        return (self.state["completed_batches"] / self.state["total_batches"]) * 100
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Retorna resumo do progresso.
        
        Returns:
            Dicionário com informações de resumo
        """
        return {
            "total_batches": self.state["total_batches"],
            "completed_batches": self.state["completed_batches"],
            "remaining_batches": self.state["total_batches"] - self.state["completed_batches"],
            "progress_percentage": self.get_progress_percentage(),
            "total_files_downloaded": len(self.state["downloaded_files"]),
            "total_files_extracted": len(self.state["extracted_files"]),
            "total_errors": len(self.state["errors"]),
            "status": self.state["status"]
        }
    
    def reset(self) -> None:
        """
        Reseta o estado para começar do zero.
        """
        self.state = self._create_new_state()
        self.save_state()
