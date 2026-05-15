"""
push_metas.py
Push das tabelas de metas → Cloudflare D1.

Tabelas:
  tb_metas_times  ← meta_time_v2  (meta mensal por equipe)
  meta_captacao   ← meta_captacao (meta de captação por assessor)
  meta_receita    ← meta_receita  (meta de receita por assessor)

Uso:
  python push_metas.py [--no-schema]
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
_log_file = os.path.join(_log_dir, f"push_metas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

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


MESES = ['janeiro', 'fevereiro', 'marco', 'abril', 'maio', 'junho',
         'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']

METAS_CONFIG = {
    'tb_metas_times': {
        'sheet':   'meta_time_v2',
        'rename':  {'TIMES': 'equipe', **{m.capitalize(): m for m in MESES}},
        'columns': ['equipe'] + MESES,
    },
    'meta_captacao': {
        'sheet':   'meta_captacao',
        'rename':  {},
        'columns': ['id_assessor', 'nome_assessor', 'equipe', 'status', 'email_assessor'] + MESES,
    },
    'meta_receita': {
        'sheet':   'meta_receita',
        'rename':  {},
        'columns': ['id_assessor', 'nome_assessor', 'equipe', 'status', 'email_assessor'] + MESES,
    },
}


def main():
    no_schema = '--no-schema' in sys.argv

    logger.info('=' * 60)
    logger.info('PUSH METAS — 3 TABELAS')
    if no_schema:
        logger.info('  Modo: --no-schema (sem recriar tabelas)')
    logger.info('=' * 60)

    if not is_configured():
        logger.error(
            'Credenciais Cloudflare não encontradas!\n'
            'Crie o arquivo .env com:\n'
            '  CF_ACCOUNT_ID, CF_API_KEY, CF_API_EMAIL, CF_D1_DATABASE_ID'
        )
        sys.exit(1)

    if not os.path.exists(config.ARQUIVO_METAS):
        logger.error(f'Arquivo não encontrado: {config.ARQUIVO_METAS}')
        sys.exit(1)

    logger.info(f'Arquivo: {config.ARQUIVO_METAS}')

    if not no_schema:
        logger.info('Criando tabelas D1 (metas)...')
        criar_tabelas(['tb_metas_times', 'meta_captacao', 'meta_receita'])
    else:
        logger.info('Schema mantido (--no-schema).')

    for tabela, cfg in METAS_CONFIG.items():
        logger.info('-' * 40)
        logger.info(f'Processando {tabela} (sheet: {cfg["sheet"]})...')
        try:
            df = pd.read_excel(
                config.ARQUIVO_METAS,
                sheet_name=cfg['sheet'],
                engine='openpyxl',
                header=0,
            )
            # normaliza nomes de colunas (remove acentos)
            df.columns = [_norm_col(c) for c in df.columns]
            df = df.rename(columns=cfg['rename'])
            df = df.dropna(how='all')

            cols_presentes = [c for c in cfg['columns'] if c in df.columns]
            if not cols_presentes:
                logger.warning(f'  Nenhuma coluna mapeada — pulando.')
                continue

            df = df[cols_presentes]
            logger.info(f'  {len(df)} linhas lidas.')
            push_table(tabela, df, cols_presentes)
            _set_metadata(f'{tabela}_updated_at')
        except Exception as e:
            logger.error(f'  Erro em {tabela}: {e}', exc_info=True)

    logger.info('=' * 60)
    logger.info('PUSH METAS CONCLUÍDO')
    logger.info(f'Log: {_log_file}')
    logger.info('=' * 60)


if __name__ == '__main__':
    main()
