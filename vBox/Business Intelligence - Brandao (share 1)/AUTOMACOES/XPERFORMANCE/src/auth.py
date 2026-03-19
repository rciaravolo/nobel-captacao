import time
import logging
from playwright.sync_api import Page


class XPIAuthenticator:
    """
    Gerencia autenticação no portal hub.xpi.com.br usando Playwright.
    """

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
        "advisor.xpi.com.br"
    ]

    _PORTAL_AUTHENTICATED_INDICATOR = "hub.xpi.com.br/new/dashboard"

    def __init__(self, page: Page, logger: logging.Logger):
        self.page = page
        self.logger = logger
        self.is_authenticated = False

    def wait_for_manual_login(self, portal_url: str, timeout: int = 300) -> bool:
        """
        Limpa sessão, abre o portal e aguarda login manual do usuário.

        Args:
            portal_url: URL do portal
            timeout: Timeout em segundos

        Returns:
            True se login bem-sucedido, False se timeout
        """
        try:
            self.logger.info("Limpando sessão anterior (cookies e storage)...")
            self.page.context.clear_cookies()
            self.page.goto("about:blank")
            self.page.evaluate("() => { try { localStorage.clear(); sessionStorage.clear(); } catch(e) {} }")

            self.logger.info(f"Acessando portal: {portal_url}")
            self.page.goto(portal_url, wait_until="domcontentloaded", timeout=30000)

            self.logger.info("=" * 60)
            self.logger.info("AGUARDANDO LOGIN MANUAL DO USUÁRIO")
            self.logger.info(f"Você tem {timeout // 60} minutos para fazer login no navegador")
            self.logger.info("=" * 60)

            start_time = time.time()
            check_interval = 1

            while time.time() - start_time < timeout:
                elapsed = int(time.time() - start_time)
                remaining = timeout - elapsed

                if elapsed % 30 == 0 and elapsed > 0:
                    self.logger.info(f"[auth] URL atual: {self.page.url}")
                    self.logger.info(f"Tempo restante: {remaining // 60}min {remaining % 60}s")

                if self._verify_authentication():
                    self.is_authenticated = True
                    self.logger.info("=" * 60)
                    self.logger.info("✓ Login detectado! Autenticação bem-sucedida!")
                    self.logger.info("=" * 60)
                    return True

                time.sleep(check_interval)

            self.logger.error("✗ TIMEOUT: Usuário não efetuou o login")
            return False

        except Exception as e:
            self.logger.error(f"Erro durante aguardo de login: {e}")
            return False

    def _verify_authentication(self) -> bool:
        """
        Retorna True somente quando a URL indica que o usuário está
        dentro do portal autenticado (dashboard), fora de qualquer
        etapa intermediária de login.
        """
        try:
            current_url = self.page.url.lower()

            for indicator in self._AUTH_FLOW_INDICATORS:
                if indicator in current_url:
                    return False

            if self._PORTAL_AUTHENTICATED_INDICATOR in current_url:
                self.logger.info(f"[auth] Dashboard detectado: {self.page.url}")
                return True

            return False

        except Exception:
            return False

    def check_session(self) -> bool:
        """
        Verifica se a sessão ainda está ativa.
        """
        try:
            current_url = self.page.url.lower()
            if any(ind in current_url for ind in ("login", "advisor.xpi.com.br")):
                self.is_authenticated = False
                return False
            return self.is_authenticated
        except Exception as e:
            self.logger.warning(f"Erro ao verificar sessão: {e}")
            return False

    def re_authenticate(self, portal_url: str) -> bool:
        """
        Re-autentica limpando sessão e aguardando novo login manual.
        """
        self.logger.warning("Sessão expirada. Aguardando novo login manual...")
        self.is_authenticated = False
        return self.wait_for_manual_login(portal_url, timeout=300)
