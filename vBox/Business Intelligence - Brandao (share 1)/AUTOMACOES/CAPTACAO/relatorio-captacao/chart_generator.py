"""
chart_generator.py
Gera grafico de barras divergente (Aporte vs Resgate) por dia do mes atual.
Retorna a imagem como string base64 para embed inline no HTML do email.
"""

import base64
import io
import logging
from datetime import datetime

import matplotlib
matplotlib.use('Agg')  # backend sem GUI
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

import config

logger = logging.getLogger(__name__)


def _formatar_valor_eixo(valor: float) -> str:
    """Formata valor numerico para label legivel (Mi / Bi)."""
    abs_val = abs(valor)
    if abs_val >= 1_000_000_000:
        return f"{valor / 1_000_000_000:.1f} Bi"
    if abs_val >= 1_000_000:
        return f"{valor / 1_000_000:.1f} Mi"
    if abs_val >= 1_000:
        return f"{valor / 1_000:.0f} K"
    return f"{valor:.0f}"


def _formatar_valor_barra(valor: float) -> str:
    """Formata valor para label sobre as barras."""
    abs_val = abs(valor)
    if abs_val >= 1_000_000_000:
        txt = f"{abs_val / 1_000_000_000:.1f} Bi"
    elif abs_val >= 1_000_000:
        txt = f"{abs_val / 1_000_000:.1f} Mi"
    elif abs_val >= 1_000:
        txt = f"{abs_val / 1_000:.0f} K"
    elif abs_val == 0:
        txt = "0"
    else:
        txt = f"{abs_val:,.0f}"
    return txt


def preparar_dados_diarios(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega dados diarios do mes atual: separa Aporte (positivo) e Resgate (negativo).

    Retorna DataFrame com colunas: dia, aporte, resgate, liquida.
    """
    if config.COLUNA_DATA not in df.columns:
        logger.warning(f"Coluna '{config.COLUNA_DATA}' nao encontrada. Grafico nao sera gerado.")
        return pd.DataFrame()

    df = df.copy()
    df[config.COLUNA_DATA] = pd.to_datetime(df[config.COLUNA_DATA], errors='coerce')
    df = df.dropna(subset=[config.COLUNA_DATA])

    # Filtra mes atual
    hoje = datetime.now()
    mask = (df[config.COLUNA_DATA].dt.year == hoje.year) & (df[config.COLUNA_DATA].dt.month == hoje.month)
    df_mes = df[mask].copy()

    if df_mes.empty:
        logger.warning("Nenhum dado encontrado para o mes atual.")
        return pd.DataFrame()

    df_mes['dia'] = df_mes[config.COLUNA_DATA].dt.day

    # Agrupa por dia
    aporte_por_dia = (
        df_mes[df_mes[config.COLUNA_VALOR] > 0]
        .groupby('dia')[config.COLUNA_VALOR]
        .sum()
    )
    resgate_por_dia = (
        df_mes[df_mes[config.COLUNA_VALOR] < 0]
        .groupby('dia')[config.COLUNA_VALOR]
        .sum()
    )

    # Monta DataFrame com todos os dias que tem dados
    dias = sorted(df_mes['dia'].unique())
    resultado = pd.DataFrame({'dia': dias})
    resultado['aporte'] = resultado['dia'].map(aporte_por_dia).fillna(0)
    resultado['resgate'] = resultado['dia'].map(resgate_por_dia).fillna(0)
    resultado['liquida'] = resultado['aporte'] + resultado['resgate']

    logger.info(f"  Grafico: {len(resultado)} dias com dados no mes {hoje.month:02d}/{hoje.year}")
    return resultado


def gerar_grafico_captacao(df_diario: pd.DataFrame) -> str:
    """Gera grafico de barras divergente e retorna imagem PNG em base64.

    Parametros:
        df_diario: DataFrame com colunas dia, aporte, resgate, liquida.

    Retorna:
        String base64 da imagem PNG, ou string vazia se sem dados.
    """
    if df_diario.empty:
        return ''

    # Cores alinhadas com o tema Nobel
    COR_APORTE  = '#C9A84C'   # dourado
    COR_RESGATE = '#3d3d3d'   # cinza escuro
    COR_FUNDO   = '#ffffff'
    COR_TEXTO   = '#333333'
    COR_GRID    = '#e0e0e0'

    acumulado = df_diario['liquida'].sum()

    dias = df_diario['dia'].values
    aportes = df_diario['aporte'].values
    resgates = df_diario['resgate'].values  # ja sao negativos

    n = len(dias)
    x = np.arange(n)
    largura = 0.38

    # ── Cria figura ──────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(max(10, n * 0.65), 5.5))
    fig.patch.set_facecolor(COR_FUNDO)
    ax.set_facecolor(COR_FUNDO)

    # Barras
    bars_aporte = ax.bar(x - largura / 2, aportes, largura,
                         color=COR_APORTE, label='Aporte', zorder=3,
                         edgecolor='none')
    bars_resgate = ax.bar(x + largura / 2, resgates, largura,
                          color=COR_RESGATE, label='Resgate', zorder=3,
                          edgecolor='none')

    # Labels sobre cada barra (com padding maior)
    PADDING = max(aportes.max(), abs(resgates.min())) * 0.04  # 4% do maior valor
    for bar in bars_aporte:
        h = bar.get_height()
        if h != 0:
            ax.text(bar.get_x() + bar.get_width() / 2, h + PADDING,
                    _formatar_valor_barra(h),
                    ha='center', va='bottom', fontsize=7, color=COR_TEXTO,
                    fontweight='bold')

    for bar in bars_resgate:
        h = bar.get_height()
        if h != 0:
            ax.text(bar.get_x() + bar.get_width() / 2, h - PADDING,
                    _formatar_valor_barra(h),
                    ha='center', va='top', fontsize=7, color=COR_TEXTO,
                    fontweight='bold')

    # Eixo X — data completa DD/MM
    hoje = datetime.now()
    labels_x = [f"{d:02d}/{hoje.month:02d}" for d in dias]
    ax.set_xticks(x)
    ax.set_xticklabels(labels_x, fontsize=8, color=COR_TEXTO)

    # Eixo Y — remove labels, mantém grid
    ax.yaxis.set_visible(False)

    # Grid
    ax.axhline(y=0, color='#999999', linewidth=0.8, zorder=1)
    ax.grid(axis='y', color=COR_GRID, linewidth=0.5, linestyle='--', zorder=0)
    ax.set_axisbelow(True)

    # Remove bordas
    for spine in ['top', 'right', 'left']:
        ax.spines[spine].set_visible(False)
    ax.spines['bottom'].set_color(COR_GRID)

    # Titulo — centralizado
    mes_nome = datetime.now().strftime('%B/%Y').title()
    ax.set_title(f'Captacao Liquida | Evolucao Diaria — {mes_nome}',
                 fontsize=13, fontweight='bold', color='#111111',
                 loc='center', pad=15)

    # Box acumulado (canto superior direito)
    acum_fmt = _formatar_valor_barra(acumulado)
    sinal = '-' if acumulado < 0 else ''
    ax.text(0.98, 0.97,
            f'Captacao Liquida\nAcumulada\n{sinal}{acum_fmt}',
            transform=ax.transAxes, fontsize=9, fontweight='bold',
            color='#111111', ha='right', va='top',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#f5f5f5',
                      edgecolor=COR_GRID, alpha=0.9))

    # Legenda
    legend = ax.legend(loc='upper left', frameon=True, fontsize=9,
                       edgecolor=COR_GRID, fancybox=True)
    legend.get_frame().set_facecolor(COR_FUNDO)

    plt.tight_layout()

    # ── Exporta como base64 ──────────────────────────────────────
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                facecolor=COR_FUNDO, edgecolor='none')
    plt.close(fig)
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode()
    buf.close()

    logger.info(f"  Grafico gerado: {len(img_b64)} chars base64")
    return img_b64


def gerar_grafico_contas(
    chart_ativ: list,
    chart_hab: list,
    chart_evas: list,
    faixas_label: list,
    periodo: str = '',
) -> str:
    """Gera gráfico de barras agrupadas (Ativação / Habilitação / Evasão por faixa patrimonial).

    Retorna imagem PNG em base64 pronta para embed inline no HTML do e-mail.
    """
    COR_ATIV   = '#C9A84C'   # dourado Nobel
    COR_HAB    = '#111111'   # preto
    COR_EVAS   = '#8B2929'   # vermelho escuro
    COR_FUNDO  = '#F5F5F5'
    COR_GRID   = '#E0E0E0'
    COR_TEXTO  = '#333333'

    n = len(faixas_label)
    x = np.arange(n)
    largura = 0.25

    fig, ax = plt.subplots(figsize=(8, 5.2))
    fig.patch.set_facecolor(COR_FUNDO)
    ax.set_facecolor(COR_FUNDO)

    bars_a = ax.bar(x - largura, chart_ativ, largura, color=COR_ATIV,  label='Ativação',    zorder=3, edgecolor='none')
    bars_h = ax.bar(x,           chart_hab,  largura, color=COR_HAB,   label='Habilitação',  zorder=3, edgecolor='none')
    bars_e = ax.bar(x + largura, chart_evas, largura, color=COR_EVAS,  label='Evasão',      zorder=3, edgecolor='none')

    # Labels acima de cada barra
    for bars, dados in [(bars_a, chart_ativ), (bars_h, chart_hab), (bars_e, chart_evas)]:
        for bar, val in zip(bars, dados):
            if val > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.08,
                    str(val),
                    ha='center', va='bottom',
                    fontsize=8, fontweight='bold', color=COR_TEXTO,
                )

    ax.set_xticks(x)
    ax.set_xticklabels(faixas_label, fontsize=9, color=COR_TEXTO)
    ax.yaxis.set_visible(False)

    ax.grid(axis='y', color=COR_GRID, linewidth=0.5, linestyle='--', zorder=0)
    ax.axhline(y=0, color='#cccccc', linewidth=0.6, zorder=1)
    ax.set_axisbelow(True)

    for spine in ['top', 'right', 'left']:
        ax.spines[spine].set_visible(False)
    ax.spines['bottom'].set_color(COR_GRID)

    fig.text(
        0.5, 0.96,
        'ATIVAÇÃO · HABILITAÇÃO · EVASÃO POR FAIXA PATRIMONIAL',
        ha='center', va='top',
        fontsize=9, fontweight='bold', color='#111111',
    )
    if periodo:
        fig.text(
            0.5, 0.89,
            periodo.upper(),
            ha='center', va='top',
            fontsize=7.5, color='#666666',
        )

    ax.legend(
        loc='lower center',
        bbox_to_anchor=(0.5, -0.22),
        ncol=3,
        frameon=True,
        fontsize=8.5,
        edgecolor=COR_GRID,
        fancybox=False,
    )

    fig.subplots_adjust(top=0.78, bottom=0.22, left=0.05, right=0.97)

    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                facecolor=COR_FUNDO, edgecolor='none')
    plt.close(fig)
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode()
    buf.close()

    logger.info(f"  Grafico contas gerado: {len(img_b64)} chars base64")
    return img_b64
