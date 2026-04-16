"""
contas_etl.py
Lê as planilhas de Ativação, Evasão, Habilitação e Positivador do relatório de
movimentação de base (CONTAS) e retorna as métricas e dados de gráfico necessários
para integrar ao relatório de captação.
"""

import logging
import os

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


def carregar_dados_contas(base_dir: str = None) -> dict | None:
    """
    Lê as 4 planilhas e retorna dicionário com métricas e dados de gráfico.
    Retorna None se algum arquivo não for encontrado ou ocorrer erro de leitura.
    """
    arquivos = {
        'ativacao':    'ativacao.xlsx',
        'evasao':      'evasao.xlsx',
        'habilitacao': 'habilitacao.xlsx',
        'positivador': 'Relatório Positivador.xlsx',
    }

    for chave, nome in arquivos.items():
        path = _caminho(nome, base_dir)
        if not os.path.exists(path):
            logger.warning(f"[contas_etl] Arquivo não encontrado: {path} — seção de contas não será gerada.")
            return None

    try:
        ativ = pd.read_excel(_caminho(arquivos['ativacao'], base_dir))
        evas = pd.read_excel(_caminho(arquivos['evasao'], base_dir))
        hab  = pd.read_excel(_caminho(arquivos['habilitacao'], base_dir))
        pos  = pd.read_excel(_caminho(arquivos['positivador'], base_dir))
    except Exception as e:
        logger.warning(f"[contas_etl] Erro ao ler planilhas de contas: {e}")
        return None

    try:
        # Limpeza habilitacao — remove rodapés e metadados
        hab = hab[hab["Conta"].notna()].copy()
        hab = hab[hab["Conta"].apply(lambda x: str(x).strip().isdigit())].copy()

        # Positivador: ignora linhas sem status (transferências internas)
        pos_f = pos[pos["Status"].notna() & (pos["Status"].astype(str).str.strip() != "")].copy()

        # Cruzamento com Positivador para Net Em M, Tipo Pessoa, Receita no Mês
        colunas_pos = ["Cliente", "Net Em M", "Tipo Pessoa", "Receita no Mês"]

        def cruzar(df_base):
            return df_base.merge(
                pos_f[colunas_pos], left_on="Conta", right_on="Cliente", how="left"
            )

        ativ_m = cruzar(ativ)
        evas_m = cruzar(evas)
        hab_m  = cruzar(hab)

        # Métricas principais
        ativ_net  = ativ_m["Net Em M"].sum()
        evas_net  = evas_m["Net Em M"].sum()
        hab_net   = hab_m["Net Em M"].sum()

        hab_sim   = int((hab["Conta Ativada"] == "Sim").sum())
        hab_nao   = int((hab["Conta Ativada"] == "Não").sum())
        hab_tx    = hab_sim / len(hab) * 100 if len(hab) > 0 else 0

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
            'hab_sim':    hab_sim,
            'hab_nao':    hab_nao,
            'hab_tx':     hab_tx,
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
