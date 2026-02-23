import os
import re
import time
import logging
from typing import Optional, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

REPORTS_URL = "https://hub.xpi.com.br/new/relatorios-xperformance#/"


class XPerformanceDownloader:
    """
    Gerencia o fluxo completo de download de relatórios XPerformance:
    navegação → seleção de assessor → paginação → checkmark → solicitar download.
    """

    def __init__(self, driver: webdriver.Chrome, logger: logging.Logger, download_dir: str):
        """
        Inicializa o downloader.

        Args:
            driver: Instância do WebDriver
            logger: Logger para registro de eventos
            download_dir: Diretório de download
        """
        self.driver = driver
        self.logger = logger
        self.download_dir = download_dir

    # ------------------------------------------------------------------
    # Navegação
    # ------------------------------------------------------------------

    def _wait_for_page_ready(self, timeout: int = 60) -> bool:
        """
        Aguarda a página SPA terminar de carregar via polling de JS.
        Compativel com page_load_strategy='none'.
        """
        start = time.time()
        while time.time() - start < timeout:
            try:
                state = self.driver.execute_script("return document.readyState;")
                if state == "complete":
                    return True
            except Exception:
                pass
            time.sleep(0.5)
        return False

    def _find_in_shadow_dom(self, js_path: str):
        """
        Executa JS para localizar elemento dentro de Shadow DOMs aninhados.
        Retorna o elemento ou None.
        """
        try:
            return self.driver.execute_script(js_path)
        except Exception:
            return None

    def navigate_to_reports(self, timeout: int = 60) -> bool:
        """
        Navega diretamente para a página de relatórios XPerformance.
        Usa polling JS para compatibilidade com SPA e Shadow DOM.

        Returns:
            True se a página carregou com sucesso
        """
        try:
            self.logger.info(f"Navegando para: {REPORTS_URL}")
            self.driver.get(REPORTS_URL)

            self._wait_for_page_ready(timeout=30)
            time.sleep(3)

            current_url = self.driver.execute_script("return window.location.href;")
            self.logger.info(f"URL atual após navegação: {current_url}")

            start = time.time()
            while time.time() - start < timeout:
                found = self.driver.execute_script("""
                    var el = document.querySelector("soma-icon");
                    if (el) return true;
                    el = document.querySelector(".soma-icon");
                    if (el) return true;
                    el = document.querySelector("input[placeholder='Search']");
                    if (el) return true;
                    el = document.querySelector("section.pagination-details");
                    if (el) return true;
                    return false;
                """)
                if found:
                    self.logger.info("✓ Página de relatórios carregada")
                    return True
                time.sleep(1)

            self.logger.error(f"Timeout ao carregar página de relatórios. URL: {current_url}")
            return False

        except Exception as e:
            self.logger.error(f"Erro ao navegar para relatórios: {e}")
            return False

    # ------------------------------------------------------------------
    # Seleção de Assessor
    # ------------------------------------------------------------------

    def select_assessor(self, assessor_name: str, timeout: int = 20) -> bool:
        """
        Abre o popup de busca e seleciona o assessor pelo nome.
        Usa JavaScript para penetrar Shadow DOMs (componentes soma-*).

        Args:
            assessor_name: Nome do assessor a buscar
            timeout: Timeout em segundos

        Returns:
            True se assessor selecionado com sucesso
        """
        try:
            self.logger.info(f"Selecionando assessor: {assessor_name}")

            # Clicar no soma-icon (chevron-down) que abre o dropdown
            # O elemento pode estar em shadow DOM, usamos JS para clicar
            clicked = self.driver.execute_script("""
                var icons = document.querySelectorAll('soma-icon');
                for (var i = 0; i < icons.length; i++) {
                    var root = icons[i].shadowRoot;
                    if (root) {
                        var div = root.querySelector('div.soma-icon');
                        if (div) { div.click(); return true; }
                    }
                    icons[i].click();
                    return true;
                }
                var btn = document.querySelector('div.soma-icon');
                if (btn) { btn.click(); return true; }
                return false;
            """)

            if not clicked:
                self.logger.warning("Dropdown soma-icon não encontrado, tentando clique direto...")
                try:
                    el = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "soma-icon, div.soma-icon"))
                    )
                    el.click()
                except Exception:
                    pass

            time.sleep(1.5)

            # Localizar o input de busca - pode estar em shadow DOM
            search_input = self.driver.execute_script("""
                var el = document.querySelector("input[aria-label='Busca Assessor']");
                if (el) return el;
                el = document.querySelector("input[placeholder='Search']");
                if (el) return el;
                el = document.querySelector("input[type='search']");
                if (el) return el;
                return null;
            """)

            if not search_input:
                self.logger.error("Input de busca de assessor não encontrado")
                return False

            self.driver.execute_script("arguments[0].focus();", search_input)
            search_input.clear()
            search_input.send_keys(assessor_name)
            time.sleep(1.5)

            # Localizar e clicar no resultado
            result_clicked = self.driver.execute_script("""
                var name = arguments[0].toLowerCase();
                var candidates = document.querySelectorAll('li[role="option"], .assessor-option, .dropdown-item, li');
                for (var i = 0; i < candidates.length; i++) {
                    if (candidates[i].textContent.toLowerCase().includes(name)) {
                        candidates[i].click();
                        return candidates[i].textContent.trim();
                    }
                }
                return null;
            """, assessor_name)

            if result_clicked:
                self.logger.info(f"✓ Assessor selecionado: {result_clicked}")
                time.sleep(2)
                return True

            self.logger.warning(f"Assessor '{assessor_name}' não encontrado nos resultados")
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

        Returns:
            Tupla (total_clientes, total_paginas)
        """
        try:
            pagination_el = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "section.pagination-details p"))
            )
            text = pagination_el.text.strip()
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

        Returns:
            True se navegou com sucesso
        """
        try:
            next_btn = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "path[d='M9 18L15 12L9 6']")
                )
            )
            self.driver.execute_script("arguments[0].closest('button').click();", next_btn)
            time.sleep(2)
            self.logger.info("✓ Avançou para próxima página")
            return True

        except TimeoutException:
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
        Clica no checkmark principal para selecionar todos os 50 itens da página.

        Returns:
            True se seleção bem-sucedida
        """
        try:
            checkmark = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.checkmark"))
            )
            checkmark.click()
            time.sleep(1.5)
            self.logger.info("✓ Checkmark selecionado")
            return True

        except TimeoutException:
            self.logger.error("Timeout ao clicar no checkmark")
            return False
        except Exception as e:
            self.logger.error(f"Erro ao clicar no checkmark: {e}")
            return False

    def click_solicitar_download(self, timeout: int = 15) -> bool:
        """
        Clica no botão 'Solicitar download' que aparece após seleção.

        Returns:
            True se clique bem-sucedido
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "button[aria-label='Download Pdf']")
                )
            )

            btn = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Download Pdf']")
            self.driver.execute_script("arguments[0].click();", btn)

            self.logger.info("✓ 'Solicitar download' clicado")
            time.sleep(2)
            return True

        except TimeoutException:
            self.logger.error("Botão 'Solicitar download' não apareceu")
            return False
        except Exception as e:
            self.logger.error(f"Erro ao clicar em 'Solicitar download': {e}")
            return False

    def wait_for_zip_download(self, files_before: set, timeout: int = 300) -> Optional[str]:
        """
        Aguarda o arquivo ZIP aparecer no diretório de download.

        Args:
            files_before: Arquivos presentes antes do clique
            timeout: Timeout em segundos

        Returns:
            Nome do arquivo baixado ou None
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
        Executa o fluxo completo de download para um assessor:
        seleciona → verifica paginação → loop de páginas (checkmark + download).

        Args:
            assessor_name: Nome do assessor
            download_timeout: Timeout por download em segundos
            delay: Delay entre lotes em segundos

        Returns:
            Número de lotes baixados com sucesso
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

        for page in range(1, total_pages + 1):
            self.logger.info(f"  → Página {page}/{total_pages}")

            files_before = set(os.listdir(self.download_dir))

            if not self.select_all_checkmarks():
                self.logger.error(f"  ✗ Falha no checkmark (página {page})")
                continue

            if not self.click_solicitar_download():
                self.logger.error(f"  ✗ Falha ao solicitar download (página {page})")
                continue

            downloaded = self.wait_for_zip_download(files_before, timeout=download_timeout)

            if downloaded:
                batches_ok += 1
                self.logger.info(f"  ✓ Lote {page}/{total_pages} baixado: {downloaded}")
            else:
                self.logger.error(f"  ✗ Download não recebido (página {page})")

            if page < total_pages:
                time.sleep(delay)
                if not self.go_to_next_page():
                    self.logger.warning(f"  Não foi possível avançar para página {page + 1}")
                    break

        self.logger.info(f"✓ Assessor '{assessor_name}' concluído: {batches_ok}/{total_pages} lotes")
        return batches_ok

    def apply_delay(self, delay_seconds: int) -> None:
        """Aplica delay entre operações."""
        if delay_seconds > 0:
            self.logger.debug(f"Aguardando {delay_seconds}s...")
            time.sleep(delay_seconds)
