import logging
import pandas as pd
import config

logger = logging.getLogger(__name__)


def _agrupar_assessores(df: pd.DataFrame) -> pd.DataFrame:
    """Agrupa por assessor somando captação, filtrando apenas assessores ativos do JSON."""
    ativos = df.attrs.get('assessores_ativos', None)
    if ativos and 'Codigo Real' in df.columns:
        df = df[df['Codigo Real'].astype(str).str.strip().str.upper().isin(ativos)].copy()
    return (
        df.groupby(config.COLUNA_ASSESSOR)
        .agg(
            total_captacao=(config.COLUNA_VALOR, 'sum'),
            conversoes=(config.COLUNA_VALOR, 'count'),
            time=(config.COLUNA_TIME, 'first'),
        )
        .reset_index()
    )


def gerar_ranking_times(df: pd.DataFrame) -> pd.DataFrame:
    """Agrupa por time, soma captacao e ordena do maior para o menor."""
    logger.info("Gerando ranking de TIMES...")

    ranking = (
        df.groupby(config.COLUNA_TIME)
        .agg(
            total_captacao=(config.COLUNA_VALOR, 'sum'),
            conversoes=(config.COLUNA_VALOR, 'count'),
        )
        .sort_values('total_captacao', ascending=False)
        .reset_index()
    )

    ranking['posicao'] = range(1, len(ranking) + 1)
    ranking['total_captacao_fmt'] = ranking['total_captacao'].apply(_formatar_moeda)

    logger.info(f"  → {len(ranking)} times no ranking")
    return ranking


def gerar_ranking_assessores_positivos(df: pd.DataFrame) -> pd.DataFrame:
    """Assessores com captacao liquida positiva, do maior para o menor."""
    logger.info("Gerando ranking ASSESSORES POSITIVOS...")

    agrupado = _agrupar_assessores(df)
    ranking = (
        agrupado[agrupado['total_captacao'] > 0]
        .sort_values('total_captacao', ascending=False)
        .reset_index(drop=True)
    )

    ranking['posicao'] = range(1, len(ranking) + 1)
    ranking['total_captacao_fmt'] = ranking['total_captacao'].apply(_formatar_numero)

    logger.info(f"  → {len(ranking)} assessores positivos")
    return ranking


def gerar_ranking_assessores_negativos(df: pd.DataFrame) -> pd.DataFrame:
    """Assessores com captacao liquida negativa, do menor (mais negativo) para o maior."""
    logger.info("Gerando ranking ASSESSORES NEGATIVOS...")

    agrupado = _agrupar_assessores(df)
    ranking = (
        agrupado[agrupado['total_captacao'] < 0]
        .sort_values('total_captacao', ascending=True)
        .reset_index(drop=True)
    )

    ranking['posicao'] = range(1, len(ranking) + 1)
    ranking['total_captacao_fmt'] = ranking['total_captacao'].apply(_formatar_numero)

    logger.info(f"  → {len(ranking)} assessores negativos")
    return ranking


def gerar_ranking_custodia_times(df_cust: pd.DataFrame, df_escritorio: pd.DataFrame = None) -> pd.DataFrame:
    """Agrupa custodia por time sem filtro de assessor — usa df_escritorio se fornecido."""
    logger.info("Gerando ranking CUSTODIA por TIMES...")

    # Usa df_escritorio (sem filtro de assessores) para totais corretos por equipe
    fonte = df_escritorio if df_escritorio is not None else df_cust

    # Padroniza coluna de time
    fonte = fonte.copy()
    fonte[config.CUST_TIME] = fonte[config.CUST_TIME].astype(str).str.strip().str.upper()

    # Filtra apenas as 6 equipes permitidas
    permitidas = [e.upper() for e in config.EQUIPES_PERMITIDAS]
    fonte = fonte[fonte[config.CUST_TIME].isin(permitidas)]

    ranking = (
        fonte.groupby(config.CUST_TIME)
        .agg(total_custodia=(config.CUST_VALOR, 'sum'))
        .sort_values('total_custodia', ascending=False)
        .reset_index()
    )
    ranking['posicao'] = range(1, len(ranking) + 1)
    ranking['total_custodia_fmt'] = ranking['total_custodia'].apply(_formatar_moeda)
    logger.info(f"  → {len(ranking)} times no ranking de custodia")
    return ranking


def gerar_ranking_custodia_assessores(df_cust: pd.DataFrame):
    """Agrega custodia por assessor e separa em >=50mi e <50mi. Retorna (df_grande, df_pequeno)."""
    logger.info("Gerando ranking CUSTODIA por ASSESSORES...")

    # Normaliza nomes removendo acentos para unificar grafias diferentes
    import unicodedata
    def normalizar_nome(nome):
        return unicodedata.normalize('NFD', nome).encode('ascii', 'ignore').decode('utf-8').strip().upper()
    
    df_cust = df_cust.copy()
    df_cust[config.CUST_ASSESSOR] = df_cust[config.CUST_ASSESSOR].apply(normalizar_nome)

    agrupado = (
        df_cust.groupby(config.CUST_ASSESSOR)
        .agg(
            total_custodia=(config.CUST_VALOR, 'sum'),
            time=(config.CUST_TIME, 'first'),
        )
        .reset_index()
        .sort_values('total_custodia', ascending=False)
    )
    agrupado['total_custodia_fmt'] = agrupado['total_custodia'].apply(_formatar_moeda)
    agrupado['posicao'] = range(1, len(agrupado) + 1)

    limite = config.CUST_LIMITE_MI
    df_grande = agrupado[agrupado['total_custodia'] >= limite].reset_index(drop=True).copy()
    df_pequeno = agrupado[agrupado['total_custodia'] < limite].reset_index(drop=True).copy()
    df_grande['posicao'] = range(1, len(df_grande) + 1)
    df_pequeno['posicao'] = range(1, len(df_pequeno) + 1)

    logger.info(f"  → {len(df_grande)} assessores >=50mi | {len(df_pequeno)} assessores <50mi")
    return df_grande, df_pequeno


def _formatar_moeda(valor: float) -> str:
    """Formata valor para moeda brasileira completa (R$ X.XXX,XX)."""
    try:
        return f"R$ {valor:,.0f}".replace(',', '.')
    except Exception:
        return "R$ 0"


def _formatar_numero(valor: float) -> str:
    """Formata numero inteiro com separador de milhar (sem R$), igual ao print."""
    try:
        return f"{valor:,.0f}".replace(',', '.')
    except Exception:
        return "0"
