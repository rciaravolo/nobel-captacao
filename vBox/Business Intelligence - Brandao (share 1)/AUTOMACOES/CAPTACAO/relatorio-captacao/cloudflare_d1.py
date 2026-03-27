"""
cloudflare_d1.py
Cliente para o Cloudflare D1 — push e pull das tabelas TB_CAP e TB_POSITIVADOR.

Usa a API REST do D1:
  POST /client/v4/accounts/{account_id}/d1/database/{database_id}/query

Credenciais via variáveis de ambiente (ou arquivo .env):
  CF_ACCOUNT_ID  — ID da conta Cloudflare (f88f9d5c...)
  CF_API_KEY     — Global API Key (cfk_...)
  CF_API_EMAIL   — Email da conta Cloudflare
  CF_D1_DATABASE_ID — ID do banco D1
"""

import os
import logging
import requests
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)

# ── Credenciais (preenchidas em tempo de execução via env ou .env) ──────────
CF_ACCOUNT_ID     = ''
CF_API_KEY        = ''
CF_API_EMAIL      = ''
CF_D1_DATABASE_ID = ''

_BASE_URL = ''


def _init():
    """Lê credenciais do ambiente (chamado uma vez antes do primeiro uso)."""
    global CF_ACCOUNT_ID, CF_API_KEY, CF_API_EMAIL, CF_D1_DATABASE_ID, _BASE_URL
    CF_ACCOUNT_ID     = os.environ.get('CF_ACCOUNT_ID', '')
    CF_API_KEY        = os.environ.get('CF_API_KEY', '')
    CF_API_EMAIL      = os.environ.get('CF_API_EMAIL', '')
    CF_D1_DATABASE_ID = os.environ.get('CF_D1_DATABASE_ID', '')
    _BASE_URL = (
        f"https://api.cloudflare.com/client/v4/accounts/"
        f"{CF_ACCOUNT_ID}/d1/database/{CF_D1_DATABASE_ID}"
    )


def is_configured() -> bool:
    """True se as credenciais CF estão definidas no ambiente."""
    _init()
    return bool(CF_ACCOUNT_ID and CF_API_KEY and CF_API_EMAIL and CF_D1_DATABASE_ID)


def _headers() -> dict:
    return {
        "X-Auth-Key":   CF_API_KEY,
        "X-Auth-Email": CF_API_EMAIL,
        "Content-Type": "application/json",
    }


def _query(sql: str, params: list = None) -> dict:
    """Executa uma query SQL no D1 e retorna o resultado."""
    _init()
    url = f"{_BASE_URL}/query"
    body = {"sql": sql, "params": params or []}
    try:
        resp = requests.post(url, headers=_headers(), json=body, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"Erro na chamada D1 HTTP: {e}") from e
    data = resp.json()
    if not data.get('success'):
        raise RuntimeError(f"D1 query falhou: {data.get('errors')}")
    return data


# ── Schema ───────────────────────────────────────────────────────────────────

_SQL_CREATE = [
    """CREATE TABLE IF NOT EXISTS tb_cap (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_real     TEXT,
        captacao        REAL,
        nucleo          TEXT,
        assessor        TEXT,
        data_transacao  TEXT,
        status          TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS tb_positivador (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        assessor   TEXT,
        nucleo     TEXT,
        net_em_m   REAL,
        status     TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS metadata (
        chave      TEXT PRIMARY KEY,
        valor      TEXT,
        updated_at TEXT
    )""",
]


def criar_tabelas():
    """Cria as tabelas no D1 se ainda não existirem."""
    for sql in _SQL_CREATE:
        _query(sql)
    logger.info("Tabelas D1 verificadas/criadas.")


# ── Push (PC → D1) ───────────────────────────────────────────────────────────

def _push_dataframe(table: str, columns: list[str], rows: list[tuple]):
    """
    Substitui todos os dados de `table` pelos novos rows.
    Usa multi-row INSERT respeitando o limite de 100 parâmetros por query do D1.
    """
    _query(f"DELETE FROM {table}")

    col_list = ','.join(columns)
    ph_row = f"({','.join(['?'] * len(columns))})"
    # Máximo de linhas por INSERT: floor(100 / num_colunas)
    max_rows = max(1, 100 // len(columns))

    total = 0
    for i in range(0, len(rows), max_rows):
        chunk = rows[i:i + max_rows]
        multi_ph = ','.join([ph_row] * len(chunk))
        params = [v for row in chunk for v in row]
        _query(
            f"INSERT INTO {table} ({col_list}) VALUES {multi_ph}",
            params
        )
        total += len(chunk)

    logger.info(f"  → {total} linhas inseridas em '{table}'.")


def push_tb_cap(df: pd.DataFrame, data_atualizacao: str = None):
    """
    Substitui TB_CAP no D1 com os dados do DataFrame.
    df deve ter as colunas do Excel (após normalizar_colunas + padronizar_dataframe,
    mas SEM filtro de equipe/assessor para preservar o total escritório).
    """
    import config as _cfg

    logger.info(f"Push TB_CAP → D1: {len(df)} registros...")
    rows = []
    for _, row in df.iterrows():
        rows.append((
            str(row.get('Codigo Real') or '').strip(),
            float(row.get(_cfg.COLUNA_VALOR) or 0),
            str(row.get(_cfg.COLUNA_TIME) or '').strip(),
            str(row.get(_cfg.COLUNA_ASSESSOR) or '').strip(),
            str(row.get(_cfg.COLUNA_DATA) or ''),
            str(row.get(_cfg.COLUNA_STATUS) or '').strip(),
        ))

    _push_dataframe(
        'tb_cap',
        ['codigo_real', 'captacao', 'nucleo', 'assessor', 'data_transacao', 'status'],
        rows,
    )

    # Salva a data de referência nos metadados
    now = datetime.now().isoformat()
    _query(
        "INSERT OR REPLACE INTO metadata (chave, valor, updated_at) VALUES (?,?,?)",
        ['tb_cap_data_ref', data_atualizacao or now, now],
    )
    logger.info("Push TB_CAP concluído.")


def push_tb_positivador(df: pd.DataFrame):
    """Substitui TB_POSITIVADOR no D1 com os dados do DataFrame."""
    import config as _cfg

    logger.info(f"Push TB_POSITIVADOR → D1: {len(df)} registros...")
    rows = []
    for _, row in df.iterrows():
        rows.append((
            str(row.get(_cfg.CUST_ASSESSOR) or '').strip(),
            str(row.get(_cfg.CUST_TIME) or '').strip(),
            float(row.get(_cfg.CUST_VALOR) or 0),
            str(row.get(_cfg.CUST_STATUS) or '').strip(),
        ))

    _push_dataframe(
        'tb_positivador',
        ['assessor', 'nucleo', 'net_em_m', 'status'],
        rows,
    )

    now = datetime.now().isoformat()
    _query(
        "INSERT OR REPLACE INTO metadata (chave, valor, updated_at) VALUES (?,?,?)",
        ['tb_positivador_updated_at', now, now],
    )
    logger.info("Push TB_POSITIVADOR concluído.")


# ── Pull (D1 → Python) ───────────────────────────────────────────────────────

def pull_tb_cap() -> tuple[pd.DataFrame, str]:
    """
    Lê TB_CAP do D1.
    Retorna (DataFrame com colunas no formato esperado pelo etl_bases, data_ref_str).
    """
    import config as _cfg

    logger.info("Pull TB_CAP ← D1...")
    result = _query("SELECT * FROM tb_cap ORDER BY id")
    rows = result['result'][0]['results']

    if not rows:
        logger.warning("TB_CAP está vazio no D1!")
        return pd.DataFrame(), datetime.now().strftime('%d/%m/%Y')

    df = pd.DataFrame(rows)

    # Renomeia colunas ASCII → nomes originais do Excel
    df = df.rename(columns={
        'codigo_real':    'Codigo Real',
        'captacao':       _cfg.COLUNA_VALOR,
        'nucleo':         _cfg.COLUNA_TIME,
        'assessor':       _cfg.COLUNA_ASSESSOR,
        'data_transacao': _cfg.COLUNA_DATA,
        'status':         _cfg.COLUNA_STATUS,
    })

    df[_cfg.COLUNA_VALOR] = pd.to_numeric(df[_cfg.COLUNA_VALOR], errors='coerce').fillna(0)
    df[_cfg.COLUNA_DATA]  = pd.to_datetime(df[_cfg.COLUNA_DATA], errors='coerce')

    # Recupera a data de referência armazenada no push
    data_str = datetime.now().strftime('%d/%m/%Y')
    try:
        meta = _query(
            "SELECT valor FROM metadata WHERE chave = 'tb_cap_data_ref'"
        )
        raw = meta['result'][0]['results']
        if raw:
            val = raw[0]['valor']
            # Se for ISO datetime, converte para dd/mm/aaaa
            try:
                dt = datetime.fromisoformat(val)
                data_str = dt.strftime('%d/%m/%Y')
            except ValueError:
                data_str = val  # já está no formato desejado
    except Exception:
        pass

    logger.info(f"  → {len(df)} registros TB_CAP carregados do D1 (ref: {data_str})")
    return df, data_str


def pull_tb_positivador() -> pd.DataFrame:
    """Lê TB_POSITIVADOR do D1 e retorna DataFrame com colunas no formato original."""
    import config as _cfg

    logger.info("Pull TB_POSITIVADOR ← D1...")
    result = _query("SELECT * FROM tb_positivador ORDER BY id")
    rows = result['result'][0]['results']

    if not rows:
        logger.warning("TB_POSITIVADOR está vazio no D1!")
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df = df.rename(columns={
        'assessor': _cfg.CUST_ASSESSOR,
        'nucleo':   _cfg.CUST_TIME,
        'net_em_m': _cfg.CUST_VALOR,
        'status':   _cfg.CUST_STATUS,
    })
    df[_cfg.CUST_VALOR] = pd.to_numeric(df[_cfg.CUST_VALOR], errors='coerce').fillna(0)

    logger.info(f"  → {len(df)} registros TB_POSITIVADOR carregados do D1")
    return df
