import os
import time
import logging
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.auth import XPIAuthenticator
from src.downloader import XPerformanceDownloader
from src.extractor import ZipExtractor
from src.progress import ProgressTracker
from src.utils import format_duration


class XPerformanceScraper:
    """
    Scraper principal para download em massa de relatórios XPerformance.
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        """
        Inicializa o scraper.
        
        Args:
            config: Dicionário de configurações
            logger: Logger para registro de eventos
        """
        self.config = config
        self.logger = logger
        self.console = Console()
        
        self.driver: Optional[webdriver.Chrome] = None
        self.authenticator: Optional[XPIAuthenticator] = None
        self.downloader: Optional[XPerformanceDownloader] = None
        self.extractor: Optional[ZipExtractor] = None
        self.progress: Optional[ProgressTracker] = None
        self.assessores: list = []
        
        self.start_time = None
        self.end_time = None
    
    def initialize(self) -> bool:
        """
        Inicializa componentes do scraper.
        
        Returns:
            True se inicialização bem-sucedida
        """
        try:
            self.logger.info("Inicializando XPerformance Scraper...")
            
            self.progress = ProgressTracker(self.config.get("checkpoint_file"))
            
            self.driver = self._setup_driver()
            if not self.driver:
                return False
            
            self.authenticator = XPIAuthenticator(self.driver, self.logger)
            self.downloader = XPerformanceDownloader(
                self.driver,
                self.logger,
                self.config.get("download_dir")
            )
            self.extractor = ZipExtractor(
                self.logger, 
                self.config.get("organize_by_month", True)
            )
            
            self.logger.info("✓ Scraper inicializado com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar scraper: {e}")
            return False
    
    def _setup_driver(self) -> Optional[webdriver.Chrome]:
        """
        Configura e retorna o WebDriver do Chrome.
        
        Returns:
            Instância do WebDriver ou None
        """
        try:
            chrome_options = Options()
            
            if self.config.get("headless_mode", False):
                chrome_options.add_argument("--headless")
            
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            download_dir = os.path.abspath(self.config.get("download_dir"))
            os.makedirs(download_dir, exist_ok=True)
            
            prefs = {
                "download.default_directory": download_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            }
            chrome_options.add_experimental_option("prefs", prefs)
            chrome_options.page_load_strategy = "none"

            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)

            driver.set_page_load_timeout(self.config.get("page_load_timeout", 60))
            
            self.logger.info("✓ WebDriver configurado")
            return driver
            
        except Exception as e:
            self.logger.error(f"Erro ao configurar WebDriver: {e}")
            return None
    
    def run(self, assessores: list, resume: bool = True) -> bool:
        """
        Executa o processo completo de scraping para a lista de assessores.

        Args:
            assessores: Lista de nomes de assessores
            resume: Se deve retomar de checkpoint anterior

        Returns:
            True se execução bem-sucedida
        """
        try:
            self.start_time = time.time()
            self.assessores = assessores

            self._display_header()

            if not self.authenticator.wait_for_manual_login(
                self.config.get("portal_url"),
                timeout=300
            ):
                self.logger.error("Falha na autenticação. Abortando execução.")
                return False

            if not self.downloader.navigate_to_reports():
                self.logger.error("Falha ao navegar para relatórios. Abortando execução.")
                return False

            total_assessores = len(assessores)
            self.progress.start_execution(total_assessores)
            self.logger.info(f"Total de assessores a processar: {total_assessores}")

            start_idx = 0
            if resume and self.progress.state["status"] == "in_progress":
                start_idx = self.progress.state.get("last_batch_processed", 0)
                if start_idx > 0:
                    self.logger.info(f"Retomando a partir do assessor #{start_idx + 1}")

            success = self._process_all_assessores(assessores, start_idx)

            if success:
                self._post_process()
                self.progress.complete_execution(success=True)
            else:
                self.progress.complete_execution(success=False)

            self.end_time = time.time()
            self._display_summary()

            return success

        except KeyboardInterrupt:
            self.logger.warning("\nExecução interrompida pelo usuário")
            self.progress.add_error("Execução interrompida pelo usuário")
            return False
        except Exception as e:
            self.logger.error(f"Erro durante execução: {e}")
            self.progress.add_error(f"Erro fatal: {str(e)}")
            return False
        finally:
            self.cleanup()
    
    def _process_all_assessores(self, assessores: list, start_idx: int = 0) -> bool:
        """
        Itera sobre todos os assessores e executa o fluxo de download para cada um.

        Args:
            assessores: Lista de nomes de assessores
            start_idx: Índice de retomada

        Returns:
            True ao concluir (mesmo com erros parciais)
        """
        delay = self.config.get("delay_between_batches", 5)
        download_timeout = self.config.get("download_timeout", 300)
        total = len(assessores)

        with tqdm(total=total, initial=start_idx, desc="Assessores", unit="assessor") as pbar:
            for idx in range(start_idx, total):
                assessor = assessores[idx]

                if not self.authenticator.check_session():
                    self.logger.warning("Sessão expirada, re-autenticando...")
                    if not self.authenticator.re_authenticate(self.config.get("portal_url")):
                        self.logger.error("Falha na re-autenticação")
                        return False

                batches_ok = self.downloader.process_assessor(
                    assessor,
                    download_timeout=download_timeout,
                    delay=delay
                )

                if batches_ok > 0:
                    self.progress.mark_batch_completed(idx + 1, assessor)
                else:
                    self.progress.add_error(f"Assessor '{assessor}' sem downloads", idx + 1)

                pbar.update(1)
                pbar.set_postfix_str(f"Atual: {assessor} | Lotes: {batches_ok}")

                if idx < total - 1:
                    self.downloader.apply_delay(delay)

        return True
    
    def _post_process(self) -> None:
        """
        Processa arquivos após download (extração de ZIPs).
        """
        self.logger.info("\n" + "="*60)
        self.logger.info("Iniciando pós-processamento...")
        
        total_extracted = self.extractor.extract_all_zips(
            self.config.get("download_dir"),
            self.config.get("extract_dir"),
            self.config.get("keep_zip_files", False)
        )
        
        self.logger.info(f"✓ Pós-processamento concluído: {total_extracted} PDFs extraídos")
    
    def _display_header(self) -> None:
        """
        Exibe cabeçalho inicial no terminal.
        """
        self.console.print(Panel.fit(
            "[bold cyan]XPerformance PDF Scraper[/bold cyan]\n"
            "[dim]Download em massa de relatórios XPI Hub[/dim]",
            border_style="cyan"
        ))
    
    def _display_summary(self) -> None:
        """
        Exibe resumo final da execução.
        """
        summary = self.progress.get_summary()
        extraction_summary = self.extractor.get_extraction_summary(
            self.config.get("extract_dir")
        )
        
        duration = self.end_time - self.start_time if self.end_time and self.start_time else 0
        
        table = Table(title="Resumo da Execução", show_header=True, header_style="bold magenta")
        table.add_column("Métrica", style="cyan")
        table.add_column("Valor", style="green")
        
        table.add_row("Lotes Processados", f"{summary['completed_batches']}/{summary['total_batches']}")
        table.add_row("Progresso", f"{summary['progress_percentage']:.1f}%")
        table.add_row("ZIPs Baixados", str(summary['total_files_downloaded']))
        table.add_row("PDFs Extraídos", str(extraction_summary['total_pdfs']))
        table.add_row("Tamanho Total", f"{extraction_summary['total_size_mb']:.2f} MB")
        table.add_row("Erros", str(summary['total_errors']))
        table.add_row("Tempo Total", format_duration(duration))
        table.add_row("Status", summary['status'].upper())
        
        self.console.print("\n")
        self.console.print(table)
        
        if extraction_summary['by_month']:
            self.console.print("\n[bold]PDFs por Mês:[/bold]")
            for month, count in extraction_summary['by_month'].items():
                self.console.print(f"  • {month}: {count} PDFs")
        
        if summary['total_errors'] == 0:
            self.console.print("\n[bold green]✓ Execução concluída com sucesso![/bold green]")
        else:
            self.console.print(f"\n[bold yellow]⚠ Execução concluída com {summary['total_errors']} erro(s)[/bold yellow]")
    
    def cleanup(self) -> None:
        """
        Limpa recursos e fecha o navegador.
        """
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("✓ Navegador fechado")
            except Exception as e:
                self.logger.warning(f"Erro ao fechar navegador: {e}")
