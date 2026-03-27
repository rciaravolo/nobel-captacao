from datetime import datetime

# ── CAMINHOS DAS BASES ──────────────────────────────────────
import glob, os as _os

# Suporte a variável de ambiente para execução em nuvem (GitHub Actions, etc.)
# Localmente usa o caminho padrão; na nuvem, defina CAMINHO_BASE no ambiente.
CAMINHO_BASE    = _os.environ.get(
    'CAMINHO_BASE',
    r'C:\Users\Usuário\vBox\ONE PAGE'
)

def _glob_arquivo(pasta, padrao):
    resultados = [f for f in glob.glob(_os.path.join(pasta, padrao)) if not _os.path.basename(f).startswith('~$')]
    # Filtrar para excluir arquivos com "Copia" no nome
    resultados = [f for f in resultados if 'Copia' not in _os.path.basename(f)]
    return resultados[0] if resultados else None

ARQUIVO_1       = _glob_arquivo(CAMINHO_BASE, '*BASES ONE PAGE*.xlsx')
ARQUIVO_2       = _glob_arquivo(CAMINHO_BASE, 'ONE PAGE - ATUAL_V2.xlsm')
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
    r'C:\Users\Usuário\vBox\Business Intelligence - Brandao (share 1)\AUTOMACOES\CAPTACAO\assessor.json'
)

# ── REGRAS DE NEGÓCIO ─────────────────────────────────────────
EQUIPES_EXCLUIDAS  = ['OPS']          # legado, mantido por compatibilidade
EQUIPES_PERMITIDAS = [                # unicas equipes exibidas no relatorio
    'PRIVATE', 'BRAVO', 'RIO PRETO',
    'SMART-GLOBAL', 'SMART-UNIQUE', 'SMART-ALFA',
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

# ── CLOUDFLARE D1 ────────────────────────────────────────────
# Credenciais via variáveis de ambiente ou arquivo .env local.
# Para criar o banco: painel Cloudflare > Workers & Pages > D1 > Create database
CF_ACCOUNT_ID     = _os.environ.get('CF_ACCOUNT_ID', '')
CF_API_KEY        = _os.environ.get('CF_API_KEY', '')
CF_API_EMAIL      = _os.environ.get('CF_API_EMAIL', '')
CF_D1_DATABASE_ID = _os.environ.get('CF_D1_DATABASE_ID', '')

# 'excel' → lê dos arquivos Excel locais (padrão, modo local)
# 'd1'    → lê do Cloudflare D1 (modo nuvem — GitHub Actions)
FONTE_DADOS = _os.environ.get('FONTE_DADOS', 'excel')

# ── CONTROLE ─────────────────────────────────────────────────
MODO_TESTE_EMAIL = False   # True = imprime HTML no console, não envia
LOG_LEVEL        = 'INFO'

# ── EMAIL — MODO DE ENVIO ────────────────────────────────────────────────────
# 'outlook' → usa Outlook via win32com (apenas local/Windows com Outlook instalado)
# 'smtp'    → usa SMTP direto (funciona em nuvem, GitHub Actions, qualquer SO)
# Para execução em nuvem, defina EMAIL_MODO=smtp nas variáveis de ambiente.
EMAIL_MODO = _os.environ.get('EMAIL_MODO', 'outlook')

# ── EMAIL — SMTP (Office 365 ou Gmail) ─────────────────────────────────────
# Configure via arquivo .env local ou Secrets no GitHub Actions.
SMTP_HOST        = _os.environ.get('SMTP_HOST',     'smtp.office365.com')
SMTP_PORT        = int(_os.environ.get('SMTP_PORT', '587') or '587')
SMTP_USER        = _os.environ.get('SMTP_USER',     '')   # ex: relatorio@nobelcapital.com.br
SMTP_PASSWORD    = _os.environ.get('SMTP_PASSWORD', '')   # senha ou app-password
SMTP_FROM        = _os.environ.get('SMTP_FROM',     SMTP_USER)
