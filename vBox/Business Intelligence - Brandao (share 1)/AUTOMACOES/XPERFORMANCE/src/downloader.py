import os
import re
import time
import logging
from typing import Optional, Tuple
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

REPORTS_URL = "https://hub.xpi.com.br/new/relatorios-xperformance#/"


class XPerformanceDownloader:
    """
    Gerencia o fluxo completo de download de relatórios XPerformance usando Playwright.
    Usa pierce selector (>>>) para penetrar Shadow DOM dos componentes soma-*.
    """

    def __init__(self, page: Page, logger: logging.Logger, download_dir: str):
        self.page = page
        self.logger = logger
        self.download_dir = download_dir

    # ------------------------------------------------------------------
    # Navegação
    # ------------------------------------------------------------------

    def navigate_to_reports(self, timeout: int = 60) -> bool:
        """
        Navega para a página de relatórios XPerformance e aguarda carregar.
        """
        try:
            self.logger.info(f"Navegando para: {REPORTS_URL}")
            self.page.goto(REPORTS_URL, wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)

            self.logger.info(f"URL atual após navegação: {self.page.url}")

            # Aguarda o container principal da página carregar
            self.page.wait_for_selector("div.sc-gGKoUb", timeout=timeout * 1000)
            self.logger.info("✓ Página de relatórios carregada")
            return True

        except PlaywrightTimeoutError:
            self.logger.error(f"Timeout ao carregar página de relatórios. URL: {self.page.url}")
            return False
        except Exception as e:
            self.logger.error(f"Erro ao navegar para relatórios: {e}")
            return False

    # ------------------------------------------------------------------
    # Seleção de Assessor
    # ------------------------------------------------------------------

    def select_assessor(self, assessor_name: str, timeout: int = 20) -> bool:
        """
        Fluxo completo de seleção de assessor:
        1. Clica no soma-caption "Exibindo como:" para abrir o dropdown
        2. Digita o código no soma-search (via pierce selector >>>)
        3. Clica no li > soma-caption correspondente na lista suspensa
        """
        try:
            self.logger.info(f"Selecionando assessor: {assessor_name}")

            # Passo 1: clicar no container que abre o dropdown de assessor
            # O elemento é div.sc-gGKoUb que contém soma-caption "Exibindo como:" + soma-icon chevron-down
            self.page.wait_for_selector("div.sc-gGKoUb", timeout=timeout * 1000)
            container = self.page.locator("div.sc-gGKoUb").first
            container.click()
            self.logger.info("[select_assessor] clicou no container do dropdown de assessor")
            time.sleep(1.5)

            # Passo 2: digitar no input dentro do Shadow DOM de soma-search
            # Pierce selector >>> penetra o shadow root automaticamente
            search_input = self.page.locator("soma-search >>> input")
            search_input.wait_for(state="visible", timeout=timeout * 1000)
            search_input.fill("")
            search_input.type(assessor_name, delay=80)
            self.logger.info(f"[select_assessor] digitou '{assessor_name}' no soma-search")
            time.sleep(2)

            # Passo 3: aguarda o primeiro li aparecer na ul e clica
            # Não depende de classe — usa ul > li simples (primeiro resultado)
            li_locator = self.page.locator("ul > li").first
            li_locator.wait_for(state="visible", timeout=timeout * 1000)
            texto = li_locator.inner_text()
            li_locator.click()
            self.logger.info(f"✓ Assessor selecionado: {texto.strip()}")
            time.sleep(2)
            return True

        except PlaywrightTimeoutError as e:
            self.logger.error(f"[select_assessor] Timeout ao selecionar assessor '{assessor_name}': {e}")
            return False
        except Exception as e:
            self.logger.error(f"Erro ao selecionar assessor '{assessor_name}': {e}")
            return False

    # ------------------------------------------------------------------
    # Paginação
    # ------------------------------------------------------------------

    def get_pagination_info(self) -> Tuple[int, int]:
        """
        Lê a paginação da página atual.
        Formato esperado: "1 - 50 de 104"
        """
        try:
            pagination_el = self.page.locator("section.pagination-details p").first
            pagination_el.wait_for(state="visible", timeout=10000)
            text = pagination_el.inner_text().strip()
            self.logger.info(f"Paginação: {text}")

            match = re.search(r'(\d+)\s*-\s*(\d+)\s+de\s+(\d+)', text)
            if match:
                per_page = int(match.group(2)) - int(match.group(1)) + 1
                total = int(match.group(3))
                total_pages = -(-total // per_page)
                return total, total_pages

            return 0, 0

        except Exception as e:
            self.logger.warning(f"Não foi possível ler paginação: {e}")
            return 0, 0

    def go_to_next_page(self, timeout: int = 15) -> bool:
        """
        Clica no botão de próxima página.
        """
        try:
            next_btn = self.page.locator("button.button-pagination-next").first
            next_btn.wait_for(state="visible", timeout=timeout * 1000)
            next_btn.click()
            time.sleep(2)
            self.logger.info("✓ Avançou para próxima página")
            return True

        except PlaywrightTimeoutError:
            self.logger.warning("Botão de próxima página não encontrado (última página?)")
            return False
        except Exception as e:
            self.logger.error(f"Erro ao avançar página: {e}")
            return False

    # ------------------------------------------------------------------
    # Seleção e Download
    # ------------------------------------------------------------------

    def select_all_checkmarks(self, timeout: int = 15) -> bool:
        """
        Clica no checkmark principal para selecionar todos os itens da página.
        """
        try:
            checkmark = self.page.locator("div.checkmark").first
            checkmark.wait_for(state="visible", timeout=timeout * 1000)
            checkmark.click()
            time.sleep(1.5)
            self.logger.info("✓ Checkmark selecionado")
            return True

        except PlaywrightTimeoutError:
            self.logger.error("Timeout ao clicar no checkmark")
            return False
        except Exception as e:
            self.logger.error(f"Erro ao clicar no checkmark: {e}")
            return False

    def click_solicitar_download(self, timeout: int = 15) -> bool:
        """
        Fluxo de download conforme documentação:
        1. 1º clique em 'Download Pdf' — abre modal
        2. 2º clique em 'Download Pdf' — confirma download em segundo plano
        3. Clique em 'Fechar' — fecha modal e volta à lista
        """
        try:
            # 1º clique — abre o modal
            btn = self.page.locator("button[aria-label='Download Pdf']").first
            btn.wait_for(state="visible", timeout=timeout * 1000)
            btn.click()
            self.logger.info("✓ 1º clique em 'Download Pdf'")
            time.sleep(2)

            # 2º clique — confirma o download em segundo plano
            btn2 = self.page.locator("button[aria-label='Download Pdf']").first
            btn2.wait_for(state="visible", timeout=timeout * 1000)
            btn2.click()
            self.logger.info("✓ 2º clique em 'Download Pdf' (confirma)")
            time.sleep(2)

            # Clica em Fechar (soma-button com shadow DOM) para voltar à lista
            fechar = self.page.locator("soma-button[aria-label='Fechar'] >>> button").first
            fechar.wait_for(state="visible", timeout=timeout * 1000)
            fechar.click()
            self.logger.info("✓ Modal fechado")
            time.sleep(1.5)
            return True

        except PlaywrightTimeoutError:
            self.logger.error("Botão 'Download Pdf' ou 'Fechar' não apareceu")
            return False
        except Exception as e:
            self.logger.error(f"Erro ao solicitar download: {e}")
            return False

    def wait_for_zip_download(self, files_before: set, timeout: int = 300) -> Optional[str]:
        """
        Aguarda o arquivo ZIP aparecer no diretório de download.
        """
        self.logger.info(f"Aguardando download do ZIP (timeout: {timeout}s)...")
        start = time.time()

        while time.time() - start < timeout:
            time.sleep(2)
            current = set(os.listdir(self.download_dir))
            new_files = current - files_before

            for f in new_files:
                if f.endswith('.zip') and not f.endswith('.crdownload'):
                    filepath = os.path.join(self.download_dir, f)
                    if self._is_stable(filepath):
                        self.logger.info(f"✓ ZIP recebido: {f}")
                        return f

        self.logger.error("✗ Timeout aguardando ZIP")
        return None

    def _is_stable(self, filepath: str, wait: int = 3) -> bool:
        """Verifica se o arquivo parou de crescer (download concluído)."""
        try:
            s1 = os.path.getsize(filepath)
            time.sleep(wait)
            s2 = os.path.getsize(filepath)
            return s1 == s2 and s2 > 0
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Fluxo completo por assessor
    # ------------------------------------------------------------------

    def process_assessor(self, assessor_name: str, download_timeout: int = 300, delay: int = 5) -> int:
        """
        Executa o fluxo completo de download para um assessor.
        """
        self.logger.info("=" * 60)
        self.logger.info(f"Processando assessor: {assessor_name}")
        self.logger.info("=" * 60)

        if not self.select_assessor(assessor_name):
            self.logger.error(f"✗ Falha ao selecionar assessor '{assessor_name}'. Pulando.")
            return 0

        time.sleep(2)
        total_clients, total_pages = self.get_pagination_info()

        if total_clients == 0:
            self.logger.warning(f"Nenhum cliente encontrado para '{assessor_name}'")
            return 0

        self.logger.info(f"Assessor '{assessor_name}': {total_clients} clientes | {total_pages} página(s)")

        batches_ok = 0

        for page_num in range(1, total_pages + 1):
            self.logger.info(f"  → Página {page_num}/{total_pages}")

            files_before = set(os.listdir(self.download_dir))

            if not self.select_all_checkmarks():
                self.logger.error(f"  ✗ Falha no checkmark (página {page_num})")
                continue

            if not self.click_solicitar_download():
                self.logger.error(f"  ✗ Falha ao solicitar download (página {page_num})")
                continue

            downloaded = self.wait_for_zip_download(files_before, timeout=download_timeout)

            if downloaded:
                batches_ok += 1
                self.logger.info(f"  ✓ Lote {page_num}/{total_pages} baixado: {downloaded}")
            else:
                self.logger.error(f"  ✗ Download não recebido (página {page_num})")

            if page_num < total_pages:
                time.sleep(delay)
                if not self.go_to_next_page():
                    self.logger.warning(f"  Não foi possível avançar para página {page_num + 1}")
                    break

        self.logger.info(f"✓ Assessor '{assessor_name}' concluído: {batches_ok}/{total_pages} lotes")
        return batches_ok

    def apply_delay(self, delay_seconds: int) -> None:
        """Aplica delay entre operações."""
        if delay_seconds > 0:
            time.sleep(delay_seconds)
