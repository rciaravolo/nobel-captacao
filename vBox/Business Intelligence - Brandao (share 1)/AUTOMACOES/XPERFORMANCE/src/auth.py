import time
import logging
from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class XPIAuthenticator:
    """
    Gerencia autenticação no portal hub.xpi.com.br
    """
    
    def __init__(self, driver: webdriver.Chrome, logger: logging.Logger):
        """
        Inicializa o autenticador.
        
        Args:
            driver: Instância do WebDriver
            logger: Logger para registro de eventos
        """
        self.driver = driver
        self.logger = logger
        self.is_authenticated = False
    
    def wait_for_manual_login(self, portal_url: str, timeout: int = 300) -> bool:
        """
        Abre o portal e aguarda o usuário fazer login manualmente.
        
        Args:
            portal_url: URL do portal
            timeout: Timeout em segundos (padrão: 300 = 5 minutos)
            
        Returns:
            True se login bem-sucedido, False se timeout
        """
        try:
            self.logger.info(f"Acessando portal: {portal_url}")
            self.driver.get(portal_url)
            
            self.logger.info("="*60)
            self.logger.info("AGUARDANDO LOGIN MANUAL DO USUÁRIO")
            self.logger.info(f"Você tem {timeout // 60} minutos para fazer login no navegador")
            self.logger.info("="*60)
            
            start_time = time.time()
            check_interval = 2
            
            while time.time() - start_time < timeout:
                elapsed = int(time.time() - start_time)
                remaining = timeout - elapsed
                
                if elapsed % 30 == 0 and elapsed > 0:
                    self.logger.info(f"Tempo restante: {remaining // 60}min {remaining % 60}s")
                
                if self._verify_authentication():
                    self.is_authenticated = True
                    self.logger.info("="*60)
                    self.logger.info("✓ Login detectado! Autenticação bem-sucedida!")
                    self.logger.info("="*60)
                    return True
                
                time.sleep(check_interval)
            
            self.logger.error("="*60)
            self.logger.error("✗ TIMEOUT: Usuário não efetuou o login")
            self.logger.error("Recomeçar automação.")
            self.logger.error("="*60)
            return False
                
        except Exception as e:
            self.logger.error(f"Erro durante aguardo de login: {e}")
            return False
    
    # URLs ou fragmentos que indicam que ainda estamos em fluxo de autenticação
    _AUTH_FLOW_INDICATORS = [
        "login",
        "signin",
        "sign-in",
        "token",
        "otp",
        "mfa",
        "2fa",
        "two-factor",
        "verification",
        "verify",
        "auth",
        "callback",
        "sso",
    ]

    # A URL deve conter este fragmento para ser considerada dentro do portal
    _PORTAL_AUTHENTICATED_INDICATOR = "hub.xpi.com.br/new/"

    def _verify_authentication(self) -> bool:
        """
        Verifica se o fluxo completo de autenticação (incluindo 2FA/token) foi concluído.
        Só retorna True quando o usuário está dentro do portal autenticado,
        não em nenhuma página intermediária de login ou verificação.

        Returns:
            True se autenticado dentro do portal, False caso contrário
        """
        try:
            current_url = self.driver.execute_script("return window.location.href;")
            if not current_url:
                return False
            current_url = current_url.lower()

            # Ainda em alguma etapa do fluxo de autenticação
            for indicator in self._AUTH_FLOW_INDICATORS:
                if indicator in current_url:
                    return False

            # Deve estar dentro do portal autenticado
            if self._PORTAL_AUTHENTICATED_INDICATOR not in current_url:
                return False

            return True

        except Exception:
            return False
    
    def check_session(self) -> bool:
        """
        Verifica se a sessão ainda está ativa.
        
        Returns:
            True se sessão ativa, False caso contrário
        """
        try:
            current_url = self.driver.current_url
            
            if "login" in current_url.lower():
                self.is_authenticated = False
                return False
            
            return self.is_authenticated
            
        except Exception as e:
            self.logger.warning(f"Erro ao verificar sessão: {e}")
            return False
    
    def re_authenticate(self, portal_url: str) -> bool:
        """
        Tenta re-autenticar se a sessão expirou.
        
        Args:
            portal_url: URL do portal
            
        Returns:
            True se re-autenticação bem-sucedida
        """
        self.logger.warning("Sessão expirada. Aguardando novo login manual...")
        self.is_authenticated = False
        return self.wait_for_manual_login(portal_url, timeout=300)
