/**
 * Configuração global do frontend.
 * Em produção, aponte API_BASE_URL para a URL do seu Worker:
 *   https://reembolsos-api.<seu-subdominio>.workers.dev
 *
 * Em desenvolvimento local (wrangler dev), use:
 *   http://localhost:8787
 */
const API_BASE_URL = (() => {
  // Permite sobrescrever via variável de ambiente em tempo de build (Pages)
  // ou auto-detectar o ambiente
  const hostname = window.location.hostname;
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:8787';
  }
  // PRODUÇÃO: substitua pela URL real do Worker após o deploy
  return 'https://reembolsos-api.SEU_SUBDOMINIO.workers.dev';
})();
