"""
push_para_postgres.py
PC → VPS PostgreSQL

Lê TB_CAP e TB_POSITIVADOR dos arquivos Excel locais e envia para
o schema captacao no PostgreSQL da VPS (82.25.74.187:5433).

Uso:
    python push_para_postgres.py
    python push_para_postgres.py --dry-run   # só lê, não escreve
"""

import sys
import os
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Carrega .env local antes de importar config
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / '.env')
except ImportError:
    pass  # python-dotenv opcional no PC

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

import config

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            Path(__file__).parent / 'logs' / f"push_postgres_{datetime.now():%Y%m%d_%H%M%S}.log",
            encoding='utf-8'
        ),
    ]
)
logger = logging.getLogger(__name__)

# ── Conexão ───────────────────────────────────────────────────────────────────

def _get_conn():
    return psycopg2.connect(
        host=config.PG_HOST,
        port=config.PG_PORT,
        dbname=config.PG_DB,
        user=config.PG_USER,
        password=config.PG_PASSWORD,
        sslmode=config.PG_SSLMODE,
        connect_timeout=15,
    )


def _truncate_insert(conn, table: str, columns: list[str], rows: list[tuple], batch: int = 500):
    with conn.cursor() as cur:
        cur.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY;")
    conn.commit()

    total = len(rows)
    with conn.cursor() as cur:
        for i in range(0, total, batch):
            chunk = rows[i:i + batch]
            execute_values(cur, f"INSERT INTO {table} ({', '.join(columns)}) VALUES %s", chunk)
            conn.commit()
            logger.info(f"  {table}: {min(i + batch, total)}/{total} linhas inseridas")

    return total


# ── TB_CAP ────────────────────────────────────────────────────────────────────

def _ler_tb_cap() -> tuple[pd.DataFrame, str]:
    """Lê TB_CAP do Excel e retorna (df, data_atualizacao_str)."""
    if not config.ARQUIVO_1:
        raise FileNotFoundError("ARQUIVO_1 não encontrado. Verifique CAMINHO_BASE.")

    logger.info(f"Lendo {config.ARQUIVO_1} | sheet: {config.SHEET_BASE1}")
    df = pd.read_excel(config.ARQUIVO_1, sheet_name=config.SHEET_BASE1, engine='openpyxl')
    df.columns = [str(c).strip() for c in df.columns]

    # Extrai data de atualização
    data_str = datetime.now().strftime('%d/%m/%Y')
    col_data_atu = next(
        (c for c in df.columns if 'atualiza' in c.lower()),
        None
    )
    if col_data_atu:
        val = df[col_data_atu].dropna()
        if len(val) > 0:
            ts = pd.to_datetime(val.iloc[0], errors='coerce')
            if ts and not pd.isna(ts):
                data_str = ts.strftime('%d/%m/%Y')

    logger.info(f"  → {len(df)} linhas brutas | data de referência: {data_str}")
    return df, data_str


def push_tb_cap(conn, dry_run: bool = False) -> tuple[int, str]:
    df, data_str = _ler_tb_cap()
    df = df.dropna(how='all')

    # Mapeia colunas Excel → postgres
    col_map = {
        'Codigo Real':    'codigo_real',
        config.COLUNA_VALOR:    'captacao',
        config.COLUNA_TIME:     'nucleo',
        config.COLUNA_ASSESSOR: 'assessor',
        config.COLUNA_DATA:     'data_transacao',
        config.COLUNA_STATUS:   'status',
    }

    cols_pg = []
    cols_ex = []
    for ex_col, pg_col in col_map.items():
        if ex_col in df.columns:
            cols_pg.append(pg_col)
            cols_ex.append(ex_col)

    df_sel = df[cols_ex].copy()

    # Limpa tipos
    if config.COLUNA_VALOR in df_sel.columns:
        df_sel[config.COLUNA_VALOR] = pd.to_numeric(df_sel[config.COLUNA_VALOR], errors='coerce')
    if config.COLUNA_DATA in df_sel.columns:
        df_sel[config.COLUNA_DATA] = pd.to_datetime(df_sel[config.COLUNA_DATA], errors='coerce')

    df_sel = df_sel[pd.to_numeric(df_sel[config.COLUNA_VALOR], errors='coerce').notna()]

    import numpy as np
    df_sel = df_sel.replace({float('nan'): None, pd.NaT: None})
    df_sel = df_sel.where(pd.notnull(df_sel), None)

    rows = [tuple(r) for r in df_sel.values]
    logger.info(f"  → {len(rows)} linhas válidas para captacao.tb_cap")

    if dry_run:
        logger.info("  [DRY-RUN] Sem escrita no banco.")
        return len(rows), data_str

    total = _truncate_insert(conn, 'captacao.tb_cap', cols_pg, rows)
    return total, data_str


# ── TB_POSITIVADOR ────────────────────────────────────────────────────────────

def push_tb_positivador(conn, dry_run: bool = False) -> int:
    if not config.ARQUIVO_1:
        raise FileNotFoundError("ARQUIVO_1 não encontrado.")

    logger.info(f"Lendo {config.ARQUIVO_1} | sheet: {config.SHEET_CUSTODIA}")
    df = pd.read_excel(config.ARQUIVO_1, sheet_name=config.SHEET_CUSTODIA, engine='openpyxl')
    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(how='all')

    col_map = {
        config.CUST_ASSESSOR: 'assessor',
        config.CUST_TIME:     'nucleo',
        config.CUST_VALOR:    'net_em_m',
        config.CUST_STATUS:   'status',
    }

    cols_pg = []
    cols_ex = []
    for ex_col, pg_col in col_map.items():
        if ex_col in df.columns:
            cols_pg.append(pg_col)
            cols_ex.append(ex_col)

    df_sel = df[cols_ex].copy()
    if config.CUST_VALOR in df_sel.columns:
        df_sel[config.CUST_VALOR] = pd.to_numeric(df_sel[config.CUST_VALOR], errors='coerce')

    df_sel = df_sel.where(pd.notnull(df_sel), None)
    rows = [tuple(r) for r in df_sel.values]
    logger.info(f"  → {len(rows)} linhas para captacao.tb_positivador")

    if dry_run:
        logger.info("  [DRY-RUN] Sem escrita no banco.")
        return len(rows)

    total = _truncate_insert(conn, 'captacao.tb_positivador', cols_pg, rows)
    return total


# ── Metadata ──────────────────────────────────────────────────────────────────

def _upsert_metadata(conn, chave: str, valor: str):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO captacao.metadata (chave, valor, updated_at)
            VALUES (%s, %s, NOW())
            ON CONFLICT (chave) DO UPDATE
                SET valor = EXCLUDED.valor, updated_at = NOW()
        """, (chave, valor))
    conn.commit()


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Push Excel → PostgreSQL VPS')
    parser.add_argument('--dry-run', action='store_true', help='Lê dados mas não escreve no banco')
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info(f"PUSH PARA POSTGRES  |  {'DRY-RUN' if args.dry_run else 'LIVE'}")
    logger.info(f"  Host: {config.PG_HOST}:{config.PG_PORT}  DB: {config.PG_DB}")
    logger.info("=" * 60)

    conn = None
    if not args.dry_run:
        logger.info("Conectando ao PostgreSQL...")
        conn = _get_conn()
        logger.info("  Conectado.")

    try:
        rows_cap, data_ref = push_tb_cap(conn, dry_run=args.dry_run)
        rows_pos = push_tb_positivador(conn, dry_run=args.dry_run)

        if not args.dry_run and conn:
            _upsert_metadata(conn, 'data_referencia', data_ref)
            _upsert_metadata(conn, 'ultima_atualizacao', datetime.now().isoformat())
            logger.info(f"  Metadata atualizado: data_referencia={data_ref}")

        logger.info("=" * 60)
        logger.info(f"CONCLUÍDO  |  tb_cap: {rows_cap} linhas  |  tb_positivador: {rows_pos} linhas")
        logger.info("=" * 60)

    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    os.makedirs(Path(__file__).parent / 'logs', exist_ok=True)
    main()
