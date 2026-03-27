"""
push_cloudflare_d1.py
Lê TB_CAP e TB_POSITIVADOR do Excel e envia para o Cloudflare D1.

Agendar via Windows Task Scheduler para rodar durante o dia de trabalho
(ex.: às 10h, 13h e 16h30, Segunda a Sexta).

Uso:
  python push_cloudflare_d1.py

Credenciais: defina no arquivo .env (na mesma pasta) ou como variáveis de ambiente:
  CF_ACCOUNT_ID
  CF_API_TOKEN
  CF_D1_DATABASE_ID
"""

import os
import sys
import logging
from datetime import datetime

# ── Garante que o diretório do script está no path ───────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _carregar_dotenv():
    """Carrega .env do mesmo diretório (sem dependência de python-dotenv)."""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if not os.path.exists(env_path):
        return
    with open(env_path, encoding='utf-8') as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith('#') or '=' not in linha:
                continue
            chave, _, valor = linha.partition('=')
            chave = chave.strip()
            valor = valor.strip().strip('"').strip("'")
            os.environ.setdefault(chave, valor)


_carregar_dotenv()

# ── Encoding UTF-8 no console Windows ────────────────────────────────────────
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ── Logging ──────────────────────────────────────────────────────────────────
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"push_d1_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_file, encoding='utf-8'),
    ]
)
logger = logging.getLogger(__name__)

import pandas as pd
import config
from cloudflare_d1 import (
    is_configured, criar_tabelas,
    push_tb_cap, push_tb_positivador,
)
from etl_bases import carregar_base, normalizar_colunas, padronizar_dataframe


def main():
    logger.info("=" * 60)
    logger.info("PUSH CLOUDFLARE D1 — INICIO")
    logger.info("=" * 60)

    # ── Verifica credenciais ──────────────────────────────────────
    if not is_configured():
        logger.error(
            "Credenciais Cloudflare não encontradas!\n"
            "Crie o arquivo .env na pasta relatorio-captacao com:\n"
            "  CF_ACCOUNT_ID=...\n"
            "  CF_API_TOKEN=...\n"
            "  CF_D1_DATABASE_ID=..."
        )
        sys.exit(1)

    # ── Verifica arquivo Excel ────────────────────────────────────
    if not config.ARQUIVO_1:
        logger.error(
            f"Excel não encontrado em: {config.CAMINHO_BASE}\n"
            "Verifique se o arquivo 'ATUALIZAÇÃO - BASES ONE PAGE.xlsx' existe."
        )
        sys.exit(1)

    logger.info(f"Excel: {config.ARQUIVO_1}")

    # ── Garante que as tabelas existem ───────────────────────────
    logger.info("Verificando tabelas no D1...")
    criar_tabelas()

    # ────────────────────────────────────────────────────────────
    # TB_CAP
    # ────────────────────────────────────────────────────────────
    logger.info("Carregando TB_CAP do Excel...")
    df_cap = carregar_base(config.ARQUIVO_1, config.SHEET_BASE1, engine='openpyxl')
    df_cap = normalizar_colunas(df_cap)

    # Extrai a data de atualização antes de normalizar
    data_ref = None
    for col_nome in ['Data Atualização', 'Data Atualizacao']:
        if col_nome in df_cap.columns:
            vals = df_cap[col_nome].dropna()
            if len(vals) > 0:
                dt = pd.to_datetime(vals.iloc[0], errors='coerce')
                if dt is not None and not pd.isna(dt):
                    data_ref = dt.strftime('%d/%m/%Y')
            break

    # Remove cabeçalho duplicado e normaliza
    df_cap = df_cap[df_cap[config.COLUNA_ASSESSOR].astype(str).str.strip() != 'Assessor'].copy()
    df_cap = padronizar_dataframe(df_cap, nome_base='TB_CAP')

    logger.info(f"  → {len(df_cap)} registros (data ref: {data_ref})")
    push_tb_cap(df_cap, data_atualizacao=data_ref)

    # ────────────────────────────────────────────────────────────
    # TB_POSITIVADOR (Custódia)
    # ────────────────────────────────────────────────────────────
    logger.info("Carregando TB_POSITIVADOR do Excel...")
    df_pos = carregar_base(config.ARQUIVO_1, config.SHEET_CUSTODIA, engine='openpyxl')
    df_pos.columns = [str(c).strip() for c in df_pos.columns]
    df_pos = df_pos.dropna(how='all').copy()
    df_pos[config.CUST_VALOR] = pd.to_numeric(
        df_pos[config.CUST_VALOR], errors='coerce'
    ).fillna(0)

    logger.info(f"  → {len(df_pos)} registros de custódia")
    push_tb_positivador(df_pos)

    logger.info("=" * 60)
    logger.info("PUSH CONCLUÍDO COM SUCESSO")
    logger.info(f"Log salvo em: {log_file}")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
