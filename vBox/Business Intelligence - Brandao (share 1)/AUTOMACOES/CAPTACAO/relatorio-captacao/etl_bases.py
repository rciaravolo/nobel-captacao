import json
import logging
import pandas as pd
import config

logger = logging.getLogger(__name__)

# ── Helpers PostgreSQL ────────────────────────────────────────────────────────

def _pg_conn():
    import psycopg2
    return psycopg2.connect(
        host=config.PG_HOST,
        port=config.PG_PORT,
        dbname=config.PG_DB,
        user=config.PG_USER,
        password=config.PG_PASSWORD,
        sslmode=config.PG_SSLMODE,
        connect_timeout=15,
    )


def _pull_tb_cap_postgres() -> tuple[pd.DataFrame, str]:
    """Lê captacao.tb_cap do PostgreSQL e retorna (df, data_referencia_str)."""
    logger.info("  [PG] Lendo captacao.tb_cap...")
    conn = _pg_conn()
    try:
        df = pd.read_sql("""
            SELECT codigo_real   AS "Codigo Real",
                   captacao      AS "Captação",
                   nucleo        AS "Núcleo",
                   assessor      AS "Assessor",
                   data_transacao AS "Data",
                   status        AS "STATUS"
            FROM captacao.tb_cap
        """, conn)

        # Data de referência armazenada em metadata
        try:
            cur = conn.cursor()
            cur.execute("SELECT valor FROM captacao.metadata WHERE chave = 'data_referencia'")
            row = cur.fetchone()
            data_str = row[0] if row else pd.Timestamp.now().strftime('%d/%m/%Y')
            cur.close()
        except Exception:
            data_str = pd.Timestamp.now().strftime('%d/%m/%Y')

        logger.info(f"  [PG] {len(df)} registros de tb_cap | referência: {data_str}")
        return df, data_str
    finally:
        conn.close()


def _pull_tb_positivador_postgres() -> pd.DataFrame:
    """Lê captacao.tb_positivador do PostgreSQL."""
    logger.info("  [PG] Lendo captacao.tb_positivador...")
    conn = _pg_conn()
    try:
        df = pd.read_sql("""
            SELECT assessor  AS "Assessor",
                   nucleo    AS "Núcleo",
                   net_em_m  AS "Net Em M",
                   status    AS "Status"
            FROM captacao.tb_positivador
        """, conn)
        logger.info(f"  [PG] {len(df)} registros de tb_positivador")
        return df
    finally:
        conn.close()

# Colunas mínimas necessárias para o relatório
COLUNAS_NECESSARIAS = [config.COLUNA_VALOR, config.COLUNA_TIME, config.COLUNA_ASSESSOR]


def carregar_assessores_ativos() -> set:
    """Lê assessor.json e retorna set de ids dos assessores ativos."""
    logger.info("Carregando assessores ativos do assessor.json...")
    with open(config.ARQUIVO_ASSESSORES, encoding='utf-8-sig') as f:
        data = json.load(f)
    ativos = {a['id_assessor'].strip().upper() for a in data if a.get('status', '').strip().lower() == 'ativo'}
    logger.info(f"  → {len(ativos)} assessores ativos carregados do JSON")
    return ativos


def carregar_base(caminho: str, sheet: str, engine: str = 'openpyxl') -> pd.DataFrame:
    """Lê uma aba de um arquivo Excel e retorna um DataFrame."""
    logger.info(f"Lendo arquivo: {caminho} | sheet: {sheet}")
    try:
        df = pd.read_excel(caminho, sheet_name=sheet, engine=engine)
        logger.info(f"  → {len(df)} linhas carregadas")
        return df
    except FileNotFoundError:
        logger.error(f"Arquivo não encontrado: {caminho}")
        raise
    except Exception as e:
        logger.error(f"Erro ao ler '{caminho}': {e}")
        raise


def normalizar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    """Remove espaços extras dos nomes de colunas."""
    df.columns = [str(c).strip() for c in df.columns]
    return df


def padronizar_dataframe(df: pd.DataFrame, nome_base: str = '') -> pd.DataFrame:
    """Limpa e padroniza os campos-chave do DataFrame."""
    df = normalizar_colunas(df)

    # Remove linhas completamente vazias
    df = df.dropna(how='all').copy()

    # Remove linhas de totais/cabeçalho duplicado (coluna valor não numérica)
    df = df[pd.to_numeric(df[config.COLUNA_VALOR], errors='coerce').notna()].copy()

    # Padroniza strings (strip + upper) nos campos-chave
    for col in [config.COLUNA_STATUS, config.COLUNA_TIME, config.COLUNA_ASSESSOR]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.upper()

    # Converte valor para numérico (erros viram 0)
    df[config.COLUNA_VALOR] = pd.to_numeric(df[config.COLUNA_VALOR], errors='coerce').fillna(0)

    # Converte Data para datetime (garante tipo uniforme para o merge)
    if config.COLUNA_DATA in df.columns:
        df[config.COLUNA_DATA] = pd.to_datetime(df[config.COLUNA_DATA], errors='coerce')

    # Remove duplicatas exatas
    antes = len(df)
    df = df.drop_duplicates()
    if antes != len(df):
        logger.info(f"  → [{nome_base}] Removidas {antes - len(df)} duplicatas")

    return df


def filtrar_por_equipes(df: pd.DataFrame) -> pd.DataFrame:
    """Filtra apenas pelas 6 equipes permitidas (sem filtrar assessores)."""
    permitidas = [e.upper() for e in config.EQUIPES_PERMITIDAS]
    antes = len(df)
    df = df[df[config.COLUNA_TIME].str.upper().isin(permitidas)].copy()
    logger.info(f"  → Equipes permitidas: {antes} → {len(df)} registros")
    if not config.CONSIDERAR_ZERADOS:
        antes = len(df)
        df = df[df[config.COLUNA_VALOR] != 0]
        logger.info(f"  → Removidos zeros: {antes} → {len(df)} registros")
    return df


def filtrar_dados(df: pd.DataFrame, assessores_ativos: set = None) -> pd.DataFrame:
    """Filtra pelas 6 equipes permitidas + assessores ativos (para rankings de assessores)."""
    df = filtrar_por_equipes(df)
    if assessores_ativos and 'Codigo Real' in df.columns:
        antes = len(df)
        df = df[df['Codigo Real'].astype(str).str.strip().str.upper().isin(assessores_ativos)].copy()
        logger.info(f"  → Assessores ativos: {antes} → {len(df)} registros")
    return df


def executar_etl_escritorio() -> tuple[pd.DataFrame, str]:
    """Usa Base1 (TB_CAP histórico) para calcular o total bruto do escritório (barra divergente).
    Retorna (df, data_atualizacao_str)."""
    if config.FONTE_DADOS == 'postgres':
        logger.info("=== ETL ESCRITORIO (PostgreSQL — total bruto sem filtro) ===")
        df, data_str = _pull_tb_cap_postgres()
        df = padronizar_dataframe(df, nome_base='tb_cap-postgres-escritorio')
        return df, data_str

    if config.FONTE_DADOS == 'd1':
        from cloudflare_d1 import pull_tb_cap
        logger.info("=== ETL ESCRITORIO (D1 — total bruto sem filtro) ===")
        df, data_str = pull_tb_cap()
        return df, data_str

    logger.info("=== ETL ESCRITORIO (Base1 — total bruto sem filtro) ===")
    df1 = carregar_base(config.ARQUIVO_1, config.SHEET_BASE1, engine='openpyxl')
    df1 = normalizar_colunas(df1)
    
    # Extrai data de atualização da coluna J antes de padronizar
    data_atualizacao = None
    if 'Data Atualização' in df1.columns or 'Data Atualizacao' in df1.columns:
        col_data = 'Data Atualização' if 'Data Atualização' in df1.columns else 'Data Atualizacao'
        data_atualizacao = pd.to_datetime(df1[col_data].dropna().iloc[0] if len(df1[col_data].dropna()) > 0 else None, errors='coerce')
    
    data_str = data_atualizacao.strftime('%d/%m/%Y') if data_atualizacao and not pd.isna(data_atualizacao) else pd.Timestamp.now().strftime('%d/%m/%Y')
    
    df1 = padronizar_dataframe(df1, nome_base='Base1-Escritorio')
    logger.info(f"  → {len(df1)} registros totais do escritorio")
    logger.info(f"  → Data de atualização: {data_str}")
    return df1, data_str


def executar_etl(assessores_ativos: set = None) -> pd.DataFrame:
    """Pipeline ETL: usa TB_CAP (Base1) como fonte única de captação."""
    if config.FONTE_DADOS == 'postgres':
        logger.info("=== INICIANDO ETL (fonte: PostgreSQL) ===")
        if assessores_ativos is None:
            assessores_ativos = carregar_assessores_ativos()
        df, _ = _pull_tb_cap_postgres()
        df = padronizar_dataframe(df, nome_base='tb_cap-postgres')
        df = filtrar_por_equipes(df)
        if assessores_ativos and 'Codigo Real' in df.columns:
            antes = len(df)
            df = df[df['Codigo Real'].astype(str).str.strip().str.upper().isin(assessores_ativos)].copy()
            logger.info(f"  → Assessores ativos: {antes} → {len(df)} registros")
        df.attrs['assessores_ativos'] = assessores_ativos
        logger.info(f"=== ETL POSTGRES CONCLUÍDO: {len(df)} registros válidos ===")
        return df

    if config.FONTE_DADOS == 'd1':
        from cloudflare_d1 import pull_tb_cap
        logger.info("=== INICIANDO ETL (fonte: Cloudflare D1) ===")
        if assessores_ativos is None:
            assessores_ativos = carregar_assessores_ativos()
        df, _ = pull_tb_cap()
        df = filtrar_por_equipes(df)
        if assessores_ativos and 'Codigo Real' in df.columns:
            antes = len(df)
            df = df[df['Codigo Real'].astype(str).str.strip().str.upper().isin(assessores_ativos)].copy()
            logger.info(f"  → Assessores ativos: {antes} → {len(df)} registros")
        df.attrs['assessores_ativos'] = assessores_ativos
        logger.info(f"=== ETL D1 CONCLUÍDO: {len(df)} registros válidos ===")
        return df

    logger.info("=== INICIANDO ETL ===")

    if not config.ARQUIVO_1:
        raise FileNotFoundError("Base 1 não encontrada. Verifique CAMINHO_BASE em config.py.")

    # 1. Leitura da TB_CAP (Base1 - fonte única)
    df1 = carregar_base(config.ARQUIVO_1, config.SHEET_BASE1, engine='openpyxl')
    df1 = normalizar_colunas(df1)
    logger.info(f"  → TB_CAP carregada: {len(df1)} registros brutos")

    # 2. Remove linha de cabeçalho duplicada
    df1 = df1[df1[config.COLUNA_ASSESSOR].astype(str).str.strip() != 'Assessor'].copy()

    # 3. Padroniza DataFrame
    df1 = padronizar_dataframe(df1, nome_base='TB_CAP')

    # 4. Carrega assessores ativos
    if assessores_ativos is None:
        assessores_ativos = carregar_assessores_ativos()

    # 5. Seleciona colunas finais
    cols_finais = [c for c in ['Codigo Real', config.COLUNA_VALOR, config.COLUNA_TIME, 
                               config.COLUNA_ASSESSOR, config.COLUNA_DATA] if c in df1.columns]
    df = df1[cols_finais].copy()

    # 6. Filtro de equipes
    df = filtrar_por_equipes(df)

    # 7. Filtro de assessores ativos
    if assessores_ativos and 'Codigo Real' in df.columns:
        antes = len(df)
        df = df[df['Codigo Real'].astype(str).str.strip().str.upper().isin(assessores_ativos)].copy()
        logger.info(f"  → Assessores ativos (por nome): {antes} → {len(df)} registros")

    # Guarda assessores_ativos no df como atributo para uso posterior no ranking
    df.attrs['assessores_ativos'] = assessores_ativos

    logger.info(f"=== ETL CONCLUÍDO: {len(df)} registros válidos ===")
    return df


def executar_etl_custodia_escritorio() -> pd.DataFrame:
    """Retorna TB_POSITIVADOR sem filtro de assessores — para total Nobel de custódia."""
    if config.FONTE_DADOS == 'postgres':
        logger.info("=== ETL CUSTODIA ESCRITORIO (PostgreSQL — sem filtro) ===")
        df = _pull_tb_positivador_postgres()
        df[config.CUST_VALOR] = pd.to_numeric(df[config.CUST_VALOR], errors='coerce').fillna(0)
        return df

    if config.FONTE_DADOS == 'd1':
        from cloudflare_d1 import pull_tb_positivador
        logger.info("=== ETL CUSTODIA ESCRITORIO (D1 — sem filtro) ===")
        return pull_tb_positivador()

    logger.info("=== ETL CUSTODIA ESCRITORIO (sem filtro de assessores) ===")
    df = carregar_base(config.ARQUIVO_1, config.SHEET_CUSTODIA, engine='openpyxl')
    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(how='all').copy()
    df[config.CUST_VALOR] = pd.to_numeric(df[config.CUST_VALOR], errors='coerce').fillna(0)
    logger.info(f"  → {len(df)} registros totais de custódia do escritório")
    return df


def executar_etl_custodia(assessores_ativos: set = None) -> pd.DataFrame:
    """ETL da TB_POSITIVADOR: retorna custodia por assessor sem OPS."""
    if config.FONTE_DADOS == 'postgres':
        import unicodedata
        logger.info("=== INICIANDO ETL CUSTODIA (fonte: PostgreSQL) ===")
        if assessores_ativos is None:
            assessores_ativos = carregar_assessores_ativos()
        df = _pull_tb_positivador_postgres()
        df[config.CUST_VALOR] = pd.to_numeric(df[config.CUST_VALOR], errors='coerce').fillna(0)
        for col in [config.CUST_ASSESSOR, config.CUST_TIME, config.CUST_STATUS]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.upper()
        permitidas = [e.upper() for e in config.EQUIPES_PERMITIDAS]
        antes = len(df)
        df = df[df[config.CUST_TIME].isin(permitidas)].copy()
        logger.info(f"  → Equipes permitidas: {antes} → {len(df)} registros")
        if assessores_ativos and config.CUST_ASSESSOR in df.columns:
            def _norm(nome):
                return unicodedata.normalize('NFD', nome).encode('ascii', 'ignore').decode('utf-8').strip().upper()
            with open(config.ARQUIVO_ASSESSORES, 'r', encoding='utf-8') as _f:
                _data = json.load(_f)
            nomes_ativos = {_norm(a['nome_assessor']) for a in _data if a.get('status', '').upper() == 'ATIVO'}
            antes = len(df)
            df['_norm'] = df[config.CUST_ASSESSOR].apply(_norm)
            df = df[df['_norm'].isin(nomes_ativos)].copy()
            df = df.drop(columns=['_norm'])
            logger.info(f"  → Assessores ativos: {antes} → {len(df)} registros")
        cols = [c for c in [config.CUST_ASSESSOR, config.CUST_TIME, config.CUST_VALOR, config.CUST_STATUS] if c in df.columns]
        logger.info(f"=== ETL CUSTODIA POSTGRES CONCLUÍDO: {len(df)} registros ===")
        return df[cols]

    if config.FONTE_DADOS == 'd1':
        from cloudflare_d1 import pull_tb_positivador
        import unicodedata
        logger.info("=== INICIANDO ETL CUSTODIA (fonte: Cloudflare D1) ===")
        if assessores_ativos is None:
            assessores_ativos = carregar_assessores_ativos()
        df = pull_tb_positivador()
        # Filtra equipes permitidas
        permitidas = [e.upper() for e in config.EQUIPES_PERMITIDAS]
        antes = len(df)
        df = df[df[config.CUST_TIME].isin(permitidas)].copy()
        logger.info(f"  → Equipes permitidas: {antes} → {len(df)} registros")
        # Filtra assessores ativos por nome
        if assessores_ativos and config.CUST_ASSESSOR in df.columns:
            def _norm(nome):
                return unicodedata.normalize('NFD', nome).encode('ascii', 'ignore').decode('utf-8').strip().upper()
            with open(config.ARQUIVO_ASSESSORES, 'r', encoding='utf-8') as _f:
                import json as _json
                _data = _json.load(_f)
            nomes_ativos = {_norm(a['nome_assessor']) for a in _data if a.get('status', '').upper() == 'ATIVO'}
            antes = len(df)
            df['_norm'] = df[config.CUST_ASSESSOR].apply(_norm)
            df = df[df['_norm'].isin(nomes_ativos)].copy()
            df = df.drop(columns=['_norm'])
            logger.info(f"  → Assessores ativos: {antes} → {len(df)} registros")
        logger.info(f"=== ETL CUSTODIA D1 CONCLUÍDO: {len(df)} registros ===")
        return df

    logger.info("=== INICIANDO ETL CUSTODIA ===")

    if not config.ARQUIVO_1:
        raise FileNotFoundError("Base 1 nao encontrada.")

    df = carregar_base(config.ARQUIVO_1, config.SHEET_CUSTODIA, engine='openpyxl')

    # Normaliza colunas (strip + unicode)
    df.columns = [str(c).strip() for c in df.columns]

    # Remove linhas completamente vazias
    df = df.dropna(how='all').copy()

    # Garante que Net Em M e numerica
    df[config.CUST_VALOR] = pd.to_numeric(df[config.CUST_VALOR], errors='coerce').fillna(0)

    # Padroniza strings
    for col in [config.CUST_ASSESSOR, config.CUST_TIME, config.CUST_STATUS]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.upper()

    # Carrega assessores ativos (se não passado externamente)
    if assessores_ativos is None:
        assessores_ativos = carregar_assessores_ativos()

    # Filtra 6 equipes permitidas
    permitidas = [e.upper() for e in config.EQUIPES_PERMITIDAS]
    antes = len(df)
    df = df[df[config.CUST_TIME].isin(permitidas)].copy()
    logger.info(f"  → Equipes permitidas: {antes} → {len(df)} registros")

    # Filtra assessores ativos via nome do assessor (comparação com JSON)
    if assessores_ativos and config.CUST_ASSESSOR in df.columns:
        # Carrega nomes dos assessores ativos do JSON
        import json
        import unicodedata
        
        def normalizar_nome(nome):
            """Remove acentos e normaliza para comparação."""
            return unicodedata.normalize('NFD', nome).encode('ascii', 'ignore').decode('utf-8').strip().upper()
        
        with open(config.ARQUIVO_ASSESSORES, 'r', encoding='utf-8') as f:
            assessores_json = json.load(f)
        nomes_ativos = {normalizar_nome(a['nome_assessor']) for a in assessores_json if a.get('status', '').upper() == 'ATIVO'}
        
        antes = len(df)
        df['_nome_normalizado'] = df[config.CUST_ASSESSOR].apply(normalizar_nome)
        df = df[df['_nome_normalizado'].isin(nomes_ativos)].copy()
        df = df.drop(columns=['_nome_normalizado'])
        logger.info(f"  → Assessores ativos (por nome): {antes} → {len(df)} registros")

    # Seleciona colunas relevantes
    cols = [c for c in [config.CUST_ASSESSOR, config.CUST_TIME,
                        config.CUST_VALOR, config.CUST_STATUS] if c in df.columns]
    df = df[cols]

    logger.info(f"=== ETL CUSTODIA CONCLUIDO: {len(df)} clientes ===")
    return df


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
    df = executar_etl()
    print("\n" + df.head(10).to_string())
    print(f"\nTotal de registros: {len(df)}")
    print(f"Colunas: {list(df.columns)}")
    print(f"\nResumo por Nucleo:")
    print(df.groupby(config.COLUNA_TIME)[config.COLUNA_VALOR].sum().sort_values(ascending=False))
