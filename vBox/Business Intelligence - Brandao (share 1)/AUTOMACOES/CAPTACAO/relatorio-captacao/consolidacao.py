import logging
import pandas as pd
import config

logger = logging.getLogger(__name__)


def calcular_resumo(df: pd.DataFrame, df_escritorio: pd.DataFrame = None) -> dict:
    """Calcula métricas consolidadas. df_escritorio fornece os totais reais do escritório."""
    logger.info("=== CALCULANDO CONSOLIDAÇÃO ===")

    # Totais filtrados (6 equipes — para rankings)
    total_captacao   = df[config.COLUNA_VALOR].sum()
    total_conversoes = len(df)
    ticket_medio     = total_captacao / total_conversoes if total_conversoes > 0 else 0
    num_times        = df[config.COLUNA_TIME].nunique() if config.COLUNA_TIME in df.columns else 0
    num_assessores   = df[config.COLUNA_ASSESSOR].nunique() if config.COLUNA_ASSESSOR in df.columns else 0

    if config.COLUNA_ASSESSOR in df.columns:
        por_assessor = df.groupby(config.COLUNA_ASSESSOR)[config.COLUNA_VALOR].sum()
        num_positivos = int((por_assessor > 0).sum())
        num_negativos = int((por_assessor < 0).sum())
    else:
        num_positivos = 0
        num_negativos = 0

    # Totais do escritório (sem filtro — soma total da planilha)
    if df_escritorio is not None and config.COLUNA_VALOR in df_escritorio.columns:
        total_escritorio     = df_escritorio[config.COLUNA_VALOR].sum()
        positivo_escritorio  = df_escritorio[df_escritorio[config.COLUNA_VALOR] > 0][config.COLUNA_VALOR].sum()
        negativo_escritorio  = df_escritorio[df_escritorio[config.COLUNA_VALOR] < 0][config.COLUNA_VALOR].sum()
    else:
        total_escritorio    = total_captacao
        positivo_escritorio = df[df[config.COLUNA_VALOR] > 0][config.COLUNA_VALOR].sum()
        negativo_escritorio = df[df[config.COLUNA_VALOR] < 0][config.COLUNA_VALOR].sum()

    resumo = {
        'total_captacao':         total_captacao,
        'total_conversoes':       total_conversoes,
        'ticket_medio':           ticket_medio,
        'num_times':              num_times,
        'num_assessores':         num_assessores,
        'num_positivos':          num_positivos,
        'num_negativos':          num_negativos,
        'total_captacao_fmt':     _formatar_moeda(total_captacao),
        'ticket_medio_fmt':       _formatar_moeda(ticket_medio),
        # totais do escritório (barra divergente)
        'total_escritorio':       total_escritorio,
        'positivo_escritorio':    positivo_escritorio,
        'negativo_escritorio':    negativo_escritorio,
        'total_escritorio_fmt':   _formatar_moeda(total_escritorio),
        'positivo_escritorio_fmt': _formatar_moeda(positivo_escritorio),
        'negativo_escritorio_fmt': _formatar_moeda(negativo_escritorio),
    }

    logger.info(f"  Total Escritorio: {resumo['total_escritorio_fmt']}")
    logger.info(f"    Positivo: {resumo['positivo_escritorio_fmt']} | Negativo: {resumo['negativo_escritorio_fmt']}")
    logger.info(f"  Total Captacao (6 equipes): {resumo['total_captacao_fmt']}")
    logger.info(f"  Positivos: {num_positivos} | Negativos: {num_negativos}")
    logger.info("=== CONSOLIDACAO CONCLUIDA ===")

    return resumo


def calcular_resumo_custodia(df_cust: pd.DataFrame, df_escritorio_cust: pd.DataFrame = None) -> dict:
    """Calcula metricas de custodia. df_escritorio_cust fornece o total bruto (sem filtro)."""
    logger.info("=== CALCULANDO RESUMO CUSTODIA ===")

    # Total do escritório = soma total da TB_POSITIVADOR sem filtro
    if df_escritorio_cust is not None and config.CUST_VALOR in df_escritorio_cust.columns:
        total_escritorio = df_escritorio_cust[config.CUST_VALOR].sum()
    else:
        total_escritorio = df_cust[config.CUST_VALOR].sum()

    num_assessores = df_cust[config.CUST_ASSESSOR].nunique()
    num_times = df_cust[config.CUST_TIME].nunique()

    por_assessor = df_cust.groupby(config.CUST_ASSESSOR)[config.CUST_VALOR].sum()
    num_acima_50mi = int((por_assessor >= config.CUST_LIMITE_MI).sum())
    num_abaixo_50mi = int((por_assessor < config.CUST_LIMITE_MI).sum())

    resumo = {
        'total_custodia':       total_escritorio,
        'total_custodia_fmt':   _formatar_moeda(total_escritorio),
        'num_assessores_cust':  num_assessores,
        'num_times_cust':       num_times,
        'num_acima_50mi':       num_acima_50mi,
        'num_abaixo_50mi':      num_abaixo_50mi,
    }

    logger.info(f"  Custodia Nobel (total): {resumo['total_custodia_fmt']}")
    logger.info(f"  Assessores      : {num_assessores} | >=50mi: {num_acima_50mi} | <50mi: {num_abaixo_50mi}")
    logger.info("=== RESUMO CUSTODIA CONCLUIDO ===")
    return resumo


def _formatar_moeda(valor: float) -> str:
    """Formata um valor numérico para moeda brasileira (R$ X.XXX.XXX,XX)."""
    try:
        return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except Exception:
        return "R$ 0,00"
