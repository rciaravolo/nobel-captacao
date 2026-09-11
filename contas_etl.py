"""
contas_etl.py
Lê as planilhas de Ativação, Evasão e Habilitação do relatório de
movimentação de base (CONTAS) e retorna as métricas e dados de gráfico necessários
para integrar ao relatório de captação. O Net Em M (custódia por cliente) é obtido
do TB_DIVERSIFICADOR (ATUALIZAÇÃO - BASES ONE PAGE.xlsx).
"""

import logging
import os
import unicodedata

import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)

# Diretório padrão das planilhas — pode ser sobrescrito via variável de ambiente CONTAS_DIR
_CONTAS_DIR = os.environ.get(
    'CONTAS_DIR',
    r'C:\Users\Usuário\vBox\ONE PAGE\TESTE',
)

FAIXAS_ORD   = ["Até 300k", "300k - 1MM", "1MM - 10MM"]
FAIXAS_LABEL = ["Até 300k", "300k – 1MM", "1MM – 10MM"]


def _caminho(arquivo: str, base_dir: str = None) -> str:
    return os.path.join(base_dir or _CONTAS_DIR, arquivo)


def _resolver_arquivo(base_dir: str, nome: str) -> str | None:
    # Windows não normaliza NFC/NFD automaticamente; OneDrive costuma salvar em NFD.
    # Tenta match direto, depois busca no listdir comparando com normalização NFC.
    direto = os.path.join(base_dir, nome)
    if os.path.exists(direto):
        return direto
    alvo = unicodedata.normalize('NFC', nome).casefold()
    try:
        for f in os.listdir(base_dir):
            if unicodedata.normalize('NFC', f).casefold() == alvo:
                return os.path.join(base_dir, f)
    except OSError:
        pass
    return None


def carregar_dados_contas(base_dir: str = None) -> dict | None:
    """
    Lê as planilhas de movimentação de base e retorna dicionário com métricas e dados de gráfico.
    Retorna None se algum arquivo não for encontrado ou ocorrer erro de leitura.
    """
    dir_base = base_dir or _CONTAS_DIR
    arquivos = {
        'ativacao':    'ativacao.xlsx',
        'evasao':      'evasao.xlsx',
        'habilitacao': 'habilitacao.xlsx',
    }

    resolvidos = {}
    for chave, nome in arquivos.items():
        path = _resolver_arquivo(dir_base, nome)
        if path is None:
            logger.warning(f"[contas_etl] Arquivo não encontrado: {os.path.join(dir_base, nome)} — seção de contas não será gerada.")
            return None
        resolvidos[chave] = path

    try:
        ativ = pd.read_excel(resolvidos['ativacao'])
        evas = pd.read_excel(resolvidos['evasao'])
        hab  = pd.read_excel(resolvidos['habilitacao'])
    except Exception as e:
        logger.warning(f"[contas_etl] Erro ao ler planilhas de contas: {e}")
        return None

    try:
        # Limpeza habilitacao — remove rodapés e metadados
        hab = hab[hab["Conta"].notna()].copy()
        hab = hab[hab["Conta"].apply(lambda x: str(x).strip().isdigit())].copy()

        def _norm_id(s):
            # Excel mistura int, float e str na coluna de conta/cliente.
            # Normaliza tudo para string ("12345.0" → "12345") para o merge não quebrar.
            return (
                pd.Series(s)
                .astype("string")
                .str.strip()
                .str.replace(r"\.0$", "", regex=True)
            )

        # Cruzamento com TB_DIVERSIFICADOR para Net Em M (custódia por cliente)
        try:
            import config as _config
            df_div = pd.read_excel(_config.ARQUIVO_1, sheet_name=_config.SHEET_CUSTODIA, engine='openpyxl')
            df_div.columns = [str(c).strip().replace('\xa0', '').strip() for c in df_div.columns]
            df_div['NET'] = pd.to_numeric(df_div['NET'], errors='coerce').fillna(0)
            df_div['Cliente'] = _norm_id(df_div['Cliente']).values
            div_net = df_div.groupby('Cliente', as_index=False)['NET'].sum()
            div_net.columns = ['Cliente', 'Net Em M']
            logger.info(f"[contas_etl] TB_DIVERSIFICADOR carregado: {len(div_net)} clientes únicos")
        except Exception as e:
            logger.warning(f"[contas_etl] Erro ao carregar TB_DIVERSIFICADOR para Net Em M: {e} — usando zero")
            div_net = pd.DataFrame(columns=['Cliente', 'Net Em M'])

        def cruzar(df_base):
            df = df_base.copy()
            df["Conta"] = _norm_id(df["Conta"]).values
            return df.merge(div_net, left_on="Conta", right_on="Cliente", how="left")

        ativ_m = cruzar(ativ)
        evas_m = cruzar(evas)
        hab_m  = cruzar(hab)

        # Métricas principais
        ativ_net  = ativ_m["Net Em M"].sum()
        evas_net  = evas_m["Net Em M"].sum()
        hab_net   = hab_m["Net Em M"].sum()

        saldo     = len(ativ) - len(evas)
        razao     = len(evas) / len(ativ) if len(ativ) > 0 else 0

        seg1_ativ = int(len(ativ[ativ["Faixa"] == "1MM - 10MM"]))
        seg1_evas = int(len(evas[evas["Faixa"] == "1MM - 10MM"]))

        # Dados do gráfico por faixa
        def contagem(df, faixa):
            return int((df["Faixa"] == faixa).sum())

        chart_ativ = [contagem(ativ, f) for f in FAIXAS_ORD]
        chart_hab  = [contagem(hab,  f) for f in FAIXAS_ORD]
        chart_evas = [contagem(evas, f) for f in FAIXAS_ORD]

        periodo = _detectar_periodo(ativ, evas, hab)

        logger.info(
            f"[contas_etl] Ativação={len(ativ)} Habilitação={len(hab)} "
            f"Evasão={len(evas)} Período='{periodo}'"
        )

        return {
            'ativ_total': len(ativ),
            'ativ_net':   ativ_net,
            'hab_total':  len(hab),
            'evas_total': len(evas),
            'evas_net':   evas_net,
            'saldo':      saldo,
            'razao':      razao,
            'seg1_ativ':  seg1_ativ,
            'seg1_evas':  seg1_evas,
            'chart_ativ': chart_ativ,
            'chart_hab':  chart_hab,
            'chart_evas': chart_evas,
            'periodo':    periodo,
        }

    except Exception as e:
        logger.warning(f"[contas_etl] Erro ao calcular métricas de contas: {e}")
        return None


def _detectar_periodo(ativ: pd.DataFrame, evas: pd.DataFrame, hab: pd.DataFrame) -> str:
    """Detecta o intervalo de datas dos dados e retorna label como 'Semana DD–DD/MM/YYYY'."""
    datas = []
    for df in [ativ, evas, hab]:
        if "Data" in df.columns:
            datas += pd.to_datetime(df["Data"], dayfirst=True, errors="coerce").dropna().tolist()

    if not datas:
        return datetime.today().strftime("Semana %d/%m/%Y")

    data_min = min(datas)
    data_max = max(datas)

    if data_min.date() == data_max.date():
        return data_min.strftime("%d/%m/%Y")

    if data_min.month == data_max.month:
        return f"Semana {data_min.strftime('%d')}–{data_max.strftime('%d/%m/%Y')}"

    return f"Semana {data_min.strftime('%d/%m')}–{data_max.strftime('%d/%m/%Y')}"
