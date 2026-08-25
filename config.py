from datetime import datetime

# ── CAMINHOS DAS BASES ──────────────────────────────────────
import glob, os as _os, unicodedata as _ud

# Suporte a variável de ambiente para execução em nuvem (GitHub Actions, etc.)
# Localmente usa o caminho padrão; na nuvem, defina CAMINHO_BASE no ambiente.
CAMINHO_BASE    = _os.environ.get(
    'CAMINHO_BASE',
    r'C:\Users\Usuário\vBox\ONE PAGE'
)

def _arquivo_exato(pasta, nome):
    # Nomes fixos e exatos — usuário mantém backups com datas no nome (ex.: "... - Julho.xlsx"),
    # então NUNCA usar wildcard: exigir match exato para não pegar arquivo arquivado.
    # Windows/OneDrive pode armazenar nomes em NFD; comparamos normalizado (NFC) contra listdir.
    alvo = _ud.normalize('NFC', nome)
    try:
        for real in _os.listdir(pasta):
            if _ud.normalize('NFC', real) == alvo:
                return _os.path.join(pasta, real)
    except FileNotFoundError:
        pass
    return None

ARQUIVO_1       = _arquivo_exato(CAMINHO_BASE, 'ATUALIZAÇÃO - BASES ONE PAGE.xlsx')
ARQUIVO_2       = _arquivo_exato(CAMINHO_BASE, 'ONE PAGE - ATUAL_V2.xlsm')
SHEET_BASE1     = 'TB_CAP'            # sheet da Base 1 (transações diárias)
SHEET_BASE2     = 'CAPTAÇÃO ATUAL'    # sheet da Base 2 (transações diárias)
SHEET_HISTORICO = 'HISTÓRICO CAP'     # sheet com dados acumulados mensais
SHEET_CUSTODIA  = 'TB_POSITIVADOR'    # sheet de custódia

# ── COLUNAS CAPTAÇÃO ─────────────────────────────────────────
COLUNA_STATUS   = 'STATUS'
COLUNA_VALOR    = 'Captação'
COLUNA_TIME     = 'Núcleo'
COLUNA_ASSESSOR = 'Assessor'
COLUNA_DATA     = 'Data'

# ── COLUNAS CUSTÓDIA (TB_POSITIVADOR) ───────────────────────
CUST_ASSESSOR   = 'Assessor'
CUST_TIME       = 'Núcleo'
CUST_VALOR      = 'Net Em M'
CUST_STATUS     = 'Status'
CUST_LIMITE_MI  = 50_000_000          # separador >=50mi vs <50mi

# ── ASSESSORES ATIVOS ────────────────────────────────────
ARQUIVO_ASSESSORES = _os.environ.get(
    'ARQUIVO_ASSESSORES',
    _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'assessor.json')
)

# ── REGRAS DE NEGÓCIO ─────────────────────────────────────────
EQUIPES_EXCLUIDAS  = ['OPS']          # legado, mantido por compatibilidade
EQUIPES_PERMITIDAS = [                # unicas equipes exibidas no relatorio
    'PRIVATE', 'BRAVO', 'SMART',
]
CONSIDERAR_ZERADOS = False

# ── EMAIL — OUTLOOK LOGADO NA MÁQUINA (win32com) ────────────
# Em modo teste, define EMAIL_DESTINATARIO no ambiente para sobrescrever o padrão
EMAIL_DESTINATARIO  = _os.environ.get('EMAIL_DESTINATARIO', 'timenobel@nobelcapital.com.br')

# ── ASSUNTO DINÂMICO ──────────────────────────────────────────
ASSUNTO_EMAIL = f"Captacao e Custodia - {datetime.now().strftime('%d/%m/%y')}"

# ── RANKINGS ─────────────────────────────────────────────────
TOP_TIMES       = 10

# ── TEMA DO EMAIL ─────────────────────────────────────────────
TEMA_COR_PRIMARIA   = '#1E3A5F'   # Azul escuro Nobel
TEMA_COR_SECUNDARIA = '#C9A84C'   # Dourado
FONTE_RELATORIO     = 'Arial, sans-serif'

# ── POSTGRESQL (VPS) ─────────────────────────────────────────
# Usado tanto pelo push local (PC→VPS) quanto pela leitura no container VPS.
# PC (push): PG_HOST=82.25.74.187, PG_PORT=5433, PG_SSLMODE=require
# Container Docker (leitura): PG_HOST=postgres_nobel_v2, PG_PORT=5432, PG_SSLMODE=disable
PG_HOST     = _os.environ.get('PG_HOST',     '82.25.74.187')
PG_PORT     = int(_os.environ.get('PG_PORT', '5433') or '5433')
PG_DB       = _os.environ.get('PG_DB',       'nobel_db')
PG_USER     = _os.environ.get('PG_USER',     'app_user')
PG_PASSWORD = _os.environ.get('PG_PASSWORD', '')
PG_SSLMODE  = _os.environ.get('PG_SSLMODE',  'require')

# ── CLOUDFLARE D1 ────────────────────────────────────────────
# Credenciais via variáveis de ambiente ou arquivo .env local.
# Para criar o banco: painel Cloudflare > Workers & Pages > D1 > Create database
CF_ACCOUNT_ID     = _os.environ.get('CF_ACCOUNT_ID', '')
CF_API_KEY        = _os.environ.get('CF_API_KEY', '')
CF_API_EMAIL      = _os.environ.get('CF_API_EMAIL', '')
CF_D1_DATABASE_ID = _os.environ.get('CF_D1_DATABASE_ID', '')

# 'excel'    → lê dos arquivos Excel locais (padrão, modo local)
# 'd1'       → lê do Cloudflare D1 (modo nuvem — GitHub Actions)
# 'postgres' → lê do PostgreSQL VPS (modo container Docker / VPS)
FONTE_DADOS = _os.environ.get('FONTE_DADOS', 'excel')

# ── CONTROLE ─────────────────────────────────────────────────
MODO_TESTE_EMAIL = False   # True = imprime HTML no console, não envia
LOG_LEVEL        = 'INFO'

# ── EMAIL — MODO DE ENVIO ────────────────────────────────────────────────────
# 'outlook' → Outlook via win32com (apenas local/Windows com Outlook instalado)
# 'smtp'    → SMTP direto (bloqueado no M365 desde 2022 — usar graph)
# 'graph'   → Microsoft Graph API (recomendado para nuvem/GitHub Actions)
EMAIL_MODO = _os.environ.get('EMAIL_MODO', 'outlook')

# ── EMAIL — SMTP (Office 365 ou Gmail) ─────────────────────────────────────
# Configure via arquivo .env local ou Secrets no GitHub Actions.
SMTP_HOST        = _os.environ.get('SMTP_HOST',     'smtp.office365.com')
SMTP_PORT        = int(_os.environ.get('SMTP_PORT', '587') or '587')
SMTP_USER        = _os.environ.get('SMTP_USER',     '')   # ex: relatorio@nobelcapital.com.br
SMTP_PASSWORD    = _os.environ.get('SMTP_PASSWORD', '')   # senha ou app-password
SMTP_FROM        = _os.environ.get('SMTP_FROM',     SMTP_USER)

# ── EMAIL — MICROSOFT GRAPH API ──────────────────────────────────────────────
# Para uso em nuvem quando o tenant M365 bloqueia SMTP AUTH básico.
# Requer app registrada no Entra ID com permissão Mail.Send (application).
# Ver: docs/PEDIDO_TI_ENTRA_ID.md
GRAPH_CLIENT_ID     = _os.environ.get('GRAPH_CLIENT_ID',     '')
GRAPH_TENANT_ID     = _os.environ.get('GRAPH_TENANT_ID',     '')
GRAPH_CLIENT_SECRET = _os.environ.get('GRAPH_CLIENT_SECRET', '')
GRAPH_FROM          = _os.environ.get('GRAPH_FROM',          '')   # mailbox remetente
