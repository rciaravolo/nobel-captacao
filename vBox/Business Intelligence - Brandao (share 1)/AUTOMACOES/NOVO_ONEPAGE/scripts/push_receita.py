"""
push_receita.py
Push das tabelas de receita projetada → Cloudflare D1.

Tabelas (blocos horizontais da sheet RECEITA PROJETADA):
  receita_rv, receita_rf, receita_coe, receita_cambio, receita_seguros,
  receita_dominion, receita_oferta_fundos, receita_consorcio, receita_feefixo,
  receita_parceiros

Uso:
  python push_receita.py [--no-schema]
"""

import logging
import os
import sys
import unicodedata
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _carregar_dotenv():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    for candidate in [script_dir, os.path.join(script_dir, '..')]:
        env_path = os.path.normpath(os.path.join(candidate, '.env'))
        if os.path.exists(env_path):
            break
    else:
        return
    with open(env_path, encoding='utf-8') as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith('#') or '=' not in linha:
                continue
            chave, _, valor = linha.partition('=')
            os.environ.setdefault(chave.strip(), valor.strip().strip('"').strip("'"))


_carregar_dotenv()

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

_log_dir  = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(_log_dir, exist_ok=True)
_log_file = os.path.join(_log_dir, f"push_receita_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(_log_file, encoding='utf-8'),
    ],
)
logger = logging.getLogger(__name__)

import pandas as pd
import config
from cloudflare_d1 import is_configured, criar_tabelas, push_table, _set_metadata


def _norm_col(nome: str) -> str:
    s = unicodedata.normalize('NFKD', str(nome).strip())
    return ''.join(c for c in s if not unicodedata.combining(c))


def _ler_bloco_receita(df_raw: pd.DataFrame, col_start: int, col_end: int,
                       rename_map: dict, columns: list,
                       header_row: int = 1) -> pd.DataFrame:
    bloco = df_raw.iloc[:, col_start:col_end].copy()
    headers = [_norm_col(str(v)) for v in bloco.iloc[header_row].values]
    bloco.columns = headers
    bloco = bloco.iloc[header_row + 1:].reset_index(drop=True)
    bloco = bloco.dropna(how='all')
    bloco = bloco[~bloco.apply(
        lambda r: all(str(v).strip() in ('', 'nan') for v in r.values), axis=1
    )].reset_index(drop=True)
    bloco = bloco.rename(columns={k: v for k, v in rename_map.items() if k in bloco.columns})
    cols_presentes = [c for c in columns if c in bloco.columns]
    if not cols_presentes:
        return pd.DataFrame()
    return bloco[cols_presentes]


def main():
    no_schema = '--no-schema' in sys.argv

    logger.info("=" * 60)
    logger.info("PUSH RECEITA — 10 BLOCOS RECEITA PROJETADA")
    if no_schema:
        logger.info("  Modo: --no-schema (sem recriar tabelas)")
    logger.info("=" * 60)

    if not is_configured():
        logger.error(
            "Credenciais Cloudflare não encontradas!\n"
            "Crie o arquivo .env com:\n"
            "  CF_ACCOUNT_ID, CF_API_KEY, CF_API_EMAIL, CF_D1_DATABASE_ID"
        )
        sys.exit(1)

    if not config.ARQUIVO_2:
        logger.error("ARQUIVO_2 (ONE PAGE - ATUAL_V2) não encontrado.")
        sys.exit(1)

    logger.info(f"ARQUIVO_2: {config.ARQUIVO_2}")

    if not no_schema:
        logger.info("Criando tabelas D1 (receitas)...")
        criar_tabelas([
            'receita_rv', 'receita_rf', 'receita_coe', 'receita_cambio',
            'receita_seguros', 'receita_dominion', 'receita_oferta_fundos',
            'receita_consorcio', 'receita_feefixo', 'receita_parceiros',
        ])
    else:
        logger.info("Schema mantido (--no-schema).")

    # ── RECEITA PROJETADA (blocos horizontais) ────────────────────────────────
    logger.info("-" * 40)
    logger.info("RECEITA PROJETADA (lendo sheet completa)...")
    try:
        df_raw = pd.read_excel(
            config.ARQUIVO_2,
            sheet_name=config.SHEET_RECEITA,
            engine='openpyxl',
            header=None,
        )
        logger.info(f"  Shape bruto: {df_raw.shape}")

        for tipo, bloco_cfg in config.RECEITA_BLOCOS.items():
            logger.info(f"  Processando receita_{tipo}...")
            try:
                df_bloco = _ler_bloco_receita(
                    df_raw,
                    bloco_cfg['col_start'],
                    bloco_cfg['col_end'],
                    bloco_cfg['rename'],
                    bloco_cfg['columns'],
                    bloco_cfg.get('header_row', 1),
                )
                if df_bloco.empty:
                    logger.warning(f"    Bloco '{tipo}' vazio — pulando.")
                    continue
                dropna_key = bloco_cfg.get('dropna_key')
                if dropna_key and dropna_key in df_bloco.columns:
                    df_bloco = df_bloco.dropna(subset=[dropna_key]).reset_index(drop=True)
                logger.info(f"    {len(df_bloco)} linhas lidas.")
                push_table(f'receita_{tipo}', df_bloco, bloco_cfg['columns'])
                _set_metadata(f'receita_{tipo}_updated_at')
            except Exception as e:
                logger.error(f"    Erro receita_{tipo}: {e}", exc_info=True)

    except Exception as e:
        logger.error(f"Erro ao carregar RECEITA PROJETADA: {e}", exc_info=True)

    logger.info("=" * 60)
    logger.info("PUSH RECEITA CONCLUÍDO")
    logger.info(f"Log: {_log_file}")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
