import base64
import logging
import os
from datetime import datetime

import pandas as pd
import config


def _logo_base64() -> str:
    """Carrega a logo Nobel em base64 para embed inline no HTML."""
    try:
        logo_path = os.path.join(os.path.dirname(config.ARQUIVO_ASSESSORES), 'nobel.png')
        with open(logo_path, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ''

logger = logging.getLogger(__name__)


# ── GERAÇÃO DO HTML ──────────────────────────────────────────────────────────

def gerar_html_relatorio(
    resumo: dict,
    rank_times: pd.DataFrame,
    rank_positivos: pd.DataFrame,
    rank_negativos: pd.DataFrame,
    resumo_cust: dict = None,
    rank_cust_times: pd.DataFrame = None,
    rank_cust_grande: pd.DataFrame = None,
    rank_cust_pequeno: pd.DataFrame = None,
    data_atualizacao: str = None,
    grafico_captacao_b64: str = '',
) -> str:
    """Gera o HTML completo do relatorio de captacao e custodia."""
    data_str = data_atualizacao if data_atualizacao else datetime.now().strftime('%d/%m/%Y')
    cor1 = '#111111'                     # preto
    cor2 = config.TEMA_COR_SECUNDARIA    # #C9A84C dourado
    fonte = config.FONTE_RELATORIO
    logo_b64 = _logo_base64()

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background-color:#e8e8e8;font-family:{fonte};">
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#e8e8e8;padding:20px 0;">
<tr><td align="center">
<table width="700" cellpadding="0" cellspacing="0"
       style="background-color:#ffffff;border-radius:8px;
              box-shadow:0 2px 10px rgba(0,0,0,0.15);overflow:hidden;">

  <!-- CABECALHO -->
  <tr>
    <td colspan="2" style="background-color:{cor1};padding:24px 32px 20px;text-align:center;">
      {'<img src="data:image/png;base64,' + logo_b64 + '" alt="Nobel Capital" width="180" style="display:block;margin:0 auto 14px;" />' if logo_b64 else '<p style="margin:0 0 8px;color:' + cor2 + ';font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:2px;">Nobel Capital</p>'}
      <h1 style="margin:0 0 4px;color:#ffffff;font-size:20px;font-weight:700;
                 letter-spacing:0.5px;">CAPTACAO DIARIA - ASSESSOR</h1>
      <p style="margin:0;color:{cor2};font-size:12px;font-weight:600;">
        Data de Referência: {data_str}
      </p>
    </td>
  </tr>

  <!-- BARRA DIVERGENTE CAPTACAO -->
  <tr>
    <td colspan="2" style="padding:24px 32px 12px;">
      {_barra_divergente(resumo, cor1, cor2)}
    </td>
  </tr>

  <!-- GRAFICO CAPTACAO DIARIA -->
  {_secao_grafico(grafico_captacao_b64)}

  <!-- RANKING TIMES -->
  <tr>
    <td colspan="2" style="padding:20px 32px 8px;">
      <p style="margin:0 0 10px;color:{cor1};font-size:13px;font-weight:700;
                text-transform:uppercase;letter-spacing:1px;
                border-bottom:2px solid {cor2};padding-bottom:6px;">
        Ranking por Equipe
      </p>
      {_tabela_times(rank_times, cor1, cor2)}
    </td>
  </tr>

  <!-- RANKINGS ASSESSORES — DUAS COLUNAS -->
  <tr>
    <td style="padding:20px 16px 20px 32px;vertical-align:top;width:50%;">
      <p style="margin:0 0 10px;color:{cor1};font-size:13px;font-weight:700;
                text-transform:uppercase;letter-spacing:1px;
                border-bottom:2px solid {cor2};padding-bottom:6px;">
        Ranking Geral PF - Positivo
      </p>
      {_tabela_assessores_positivo(rank_positivos, cor1, cor2)}
    </td>
    <td style="padding:20px 32px 20px 16px;vertical-align:top;width:50%;">
      <p style="margin:0 0 10px;color:{cor1};font-size:13px;font-weight:700;
                text-transform:uppercase;letter-spacing:1px;
                border-bottom:2px solid {cor2};padding-bottom:6px;">
        Ranking Geral PF - Negativo
      </p>
      {_tabela_assessores_negativo(rank_negativos, cor1, cor2)}
    </td>
  </tr>

  {_secao_custodia(resumo_cust, rank_cust_times, rank_cust_grande, rank_cust_pequeno, cor1, cor2, data_str)}

  <!-- RODAPE -->
  <tr>
    <td colspan="2" style="background-color:{cor1};padding:14px 32px;
                           text-align:center;">
      <p style="margin:0;color:{cor2};font-size:11px;">
        Gerado automaticamente em {datetime.now().strftime('%d/%m/%Y as %H:%M')} | Nobel Capital
      </p>
    </td>
  </tr>

</table>
</td></tr>
</table>
</body>
</html>"""
    return html


# ── COMPONENTES HTML ──────────────────────────────────────────────────────────

def _barra_divergente(resumo: dict, cor1: str, cor2: str) -> str:
    """Gera card de captacao com total no topo e barra divergente negativo|positivo."""
    total     = resumo.get('total_escritorio', 0)
    positivo  = resumo.get('positivo_escritorio', 0)
    negativo  = resumo.get('negativo_escritorio', 0)
    total_fmt = resumo.get('total_escritorio_fmt', 'R$ 0,00')
    pos_fmt   = resumo.get('positivo_escritorio_fmt', 'R$ 0,00')
    neg_fmt   = resumo.get('negativo_escritorio_fmt', 'R$ 0,00')

    total_abs = abs(positivo) + abs(negativo)
    pct_neg = round(abs(negativo) / total_abs * 100, 1) if total_abs > 0 else 50
    pct_pos = round(100 - pct_neg, 1)

    cor_total = '#c0392b' if total < 0 else '#1a6e2e'

    return f"""<table width="100%" cellpadding="0" cellspacing="0"
       style="border:1px solid #dde3ea;border-radius:8px;background:#fff;">
  <tr>
    <td style="padding:18px 24px 6px;text-align:center;">
      <div style="color:{cor1};font-size:12px;font-weight:700;
                  text-transform:uppercase;letter-spacing:1px;margin-bottom:4px;">Captacao</div>
      <div style="color:{cor_total};font-size:22px;font-weight:700;line-height:1.2;">{total_fmt}</div>
    </td>
  </tr>
  <tr>
    <td style="padding:10px 24px 4px;">
      <table width="100%" cellpadding="0" cellspacing="0" style="border-radius:4px;overflow:hidden;">
        <tr>
          <td width="{pct_neg}%" style="background-color:#111111;padding:10px 8px;
                      text-align:right;vertical-align:middle;">
            <span style="color:#ffffff;font-size:11px;font-weight:700;white-space:nowrap;">{neg_fmt}</span>
          </td>
          <td width="{pct_pos}%" style="background-color:#C9A84C;padding:10px 8px;
                      text-align:left;vertical-align:middle;">
            <span style="color:#ffffff;font-size:11px;font-weight:700;white-space:nowrap;">{pos_fmt}</span>
          </td>
        </tr>
      </table>
    </td>
  </tr>
  <tr>
    <td style="padding:4px 24px 14px;">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td width="{pct_neg}%" style="text-align:right;padding-right:4px;">
            <span style="color:#9aaab8;font-size:9px;">{pct_neg}%</span>
          </td>
          <td width="{pct_pos}%" style="text-align:left;padding-left:4px;">
            <span style="color:#9aaab8;font-size:9px;">{pct_pos}%</span>
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>"""


def _secao_grafico(grafico_b64: str) -> str:
    """Retorna bloco HTML com o grafico de captacao embutido, ou vazio se nao disponivel."""
    if not grafico_b64:
        return ''
    return f"""<tr>
    <td colspan="2" style="padding:12px 32px 4px;">
      <img src="data:image/png;base64,{grafico_b64}"
           alt="Captacao Liquida - Evolucao Diaria"
           width="100%" style="display:block;border-radius:6px;
           border:1px solid #dde3ea;" />
    </td>
  </tr>"""


def _card(cor1: str, cor2: str, titulo: str, valor: str) -> str:
    return f"""<td style="background-color:{cor1};border-radius:6px;padding:14px 10px;
                          text-align:center;vertical-align:middle;">
  <div style="color:{cor2};font-size:9px;font-weight:700;text-transform:uppercase;
              letter-spacing:1px;margin-bottom:5px;">{titulo}</div>
  <div style="color:#ffffff;font-size:16px;font-weight:700;line-height:1.2;">{valor}</div>
</td>"""


def _tabela_times(df: pd.DataFrame, cor1: str, cor2: str) -> str:
    if df.empty:
        return '<p style="color:#888;font-size:12px;">Sem dados.</p>'

    linhas = ''
    for _, row in df.iterrows():
        bg = '#f5f5f5' if int(row['posicao']) % 2 == 0 else '#ffffff'
        val = row['total_captacao']
        cor_val = '#c0392b' if val < 0 else '#1a6e2e'
        linhas += f"""<tr style="background-color:{bg};">
          <td style="padding:8px 10px;text-align:center;font-weight:700;
                     color:{cor1};font-size:12px;width:30px;">{int(row['posicao'])}</td>
          <td style="padding:8px 10px;color:#111111;font-size:13px;font-weight:600;">
            {str(row[config.COLUNA_TIME]).title()}</td>
          <td style="padding:8px 10px;font-weight:700;text-align:right;
                     font-size:13px;color:{cor_val};">{row['total_captacao_fmt']}</td>
          <td style="padding:8px 10px;color:#666;text-align:center;font-size:12px;">
            {int(row['conversoes'])}</td>
        </tr>"""

    return f"""<table width="100%" cellpadding="0" cellspacing="0"
       style="border-collapse:collapse;border:1px solid #dde3ea;border-radius:6px;">
  <thead><tr style="background-color:{cor1};">
    <th style="padding:9px 10px;color:{cor2};font-size:10px;font-weight:700;
               text-transform:uppercase;text-align:center;width:30px;">#</th>
    <th style="padding:9px 10px;color:{cor2};font-size:10px;font-weight:700;
               text-transform:uppercase;text-align:left;">Equipe</th>
    <th style="padding:9px 10px;color:{cor2};font-size:10px;font-weight:700;
               text-transform:uppercase;text-align:right;">Captacao</th>
    <th style="padding:9px 10px;color:{cor2};font-size:10px;font-weight:700;
               text-transform:uppercase;text-align:center;">Mov.</th>
  </tr></thead>
  <tbody>{linhas}</tbody>
</table>"""


def _tabela_assessores_positivo(df: pd.DataFrame, cor1: str, cor2: str) -> str:
    if df.empty:
        return '<p style="color:#888;font-size:12px;">Nenhum assessor positivo.</p>'

    linhas = ''
    for _, row in df.iterrows():
        bg = '#f5f5f5' if int(row['posicao']) % 2 == 0 else '#ffffff'
        linhas += f"""<tr style="background-color:{bg};">
          <td style="padding:7px 8px;color:#111111;font-size:12px;">
            {str(row[config.COLUNA_ASSESSOR]).title()}</td>
          <td style="padding:7px 8px;color:#1a6e2e;font-weight:700;
                     text-align:right;font-size:12px;">{row['total_captacao_fmt']}</td>
        </tr>"""

    return f"""<table width="100%" cellpadding="0" cellspacing="0"
       style="border-collapse:collapse;border:1px solid #e0e0e0;">
  <thead><tr style="background-color:{cor1};">
    <th style="padding:8px;color:{cor2};font-size:10px;font-weight:700;
               text-transform:uppercase;text-align:left;">Assessor</th>
    <th style="padding:8px;color:{cor2};font-size:10px;font-weight:700;
               text-transform:uppercase;text-align:right;">Captacao</th>
  </tr></thead>
  <tbody>{linhas}</tbody>
</table>"""


def _tabela_assessores_negativo(df: pd.DataFrame, cor1: str, cor2: str) -> str:
    if df.empty:
        return '<p style="color:#888;font-size:12px;">Nenhum assessor negativo.</p>'

    linhas = ''
    for _, row in df.iterrows():
        bg = '#f5f5f5' if int(row['posicao']) % 2 == 0 else '#ffffff'
        linhas += f"""<tr style="background-color:{bg};">
          <td style="padding:7px 8px;color:#111111;font-size:12px;">
            {str(row[config.COLUNA_ASSESSOR]).title()}</td>
          <td style="padding:7px 8px;color:#c0392b;font-weight:700;
                     text-align:right;font-size:12px;">{row['total_captacao_fmt']}</td>
        </tr>"""

    return f"""<table width="100%" cellpadding="0" cellspacing="0"
       style="border-collapse:collapse;border:1px solid #e0e0e0;">
  <thead><tr style="background-color:{cor1};">
    <th style="padding:8px;color:{cor2};font-size:10px;font-weight:700;
               text-transform:uppercase;text-align:left;">Assessor</th>
    <th style="padding:8px;color:{cor2};font-size:10px;font-weight:700;
               text-transform:uppercase;text-align:right;">Captacao</th>
  </tr></thead>
  <tbody>{linhas}</tbody>
</table>"""


def _secao_custodia(
    resumo_cust: dict,
    rank_cust_times: pd.DataFrame,
    rank_cust_grande: pd.DataFrame,
    rank_cust_pequeno: pd.DataFrame,
    cor1: str,
    cor2: str,
    data_str: str,
) -> str:
    """Retorna o bloco HTML da secao de custodia, ou string vazia se sem dados."""
    if resumo_cust is None:
        return ''

    tabela_times_cust = _tabela_custodia_times(rank_cust_times, cor1, cor2)
    tabela_grande     = _tabela_custodia_assessores(rank_cust_grande, cor1, cor2, '>=50mi')
    tabela_pequeno    = _tabela_custodia_assessores(rank_cust_pequeno, cor1, cor2, '<50mi')

    return f"""
  <!-- DIVISOR CUSTODIA -->
  <tr>
    <td colspan="2" style="padding:10px 32px 0;">
      <hr style="border:none;border-top:3px solid {cor2};margin:0;">
    </td>
  </tr>

  <!-- TITULO CUSTODIA -->
  <tr>
    <td colspan="2" style="background-color:{cor1};padding:20px 32px;text-align:center;">
      <h2 style="margin:0 0 4px;color:#ffffff;font-size:20px;font-weight:700;
                 letter-spacing:0.5px;">CUSTODIA NOBEL</h2>
      <p style="margin:0;color:{cor2};font-size:12px;font-weight:600;">
        Posição de Referência: {data_str}
      </p>
    </td>
  </tr>

  <!-- CARDS CUSTODIA -->
  <tr>
    <td colspan="2" style="padding:24px 32px 8px;">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          {_card(cor1, cor2, 'Custodia Nobel', resumo_cust['total_custodia_fmt'])}
          <td width="10"></td>
          {_card(cor1, cor2, 'Equipes', str(resumo_cust['num_times_cust']))}
          <td width="10"></td>
          {_card(cor1, cor2, 'Acima 50mi', str(resumo_cust['num_acima_50mi']))}
          <td width="10"></td>
          {_card(cor1, cor2, 'Abaixo 50mi', str(resumo_cust['num_abaixo_50mi']))}
        </tr>
      </table>
    </td>
  </tr>

  <!-- RANKING CUSTODIA TIMES -->
  <tr>
    <td colspan="2" style="padding:20px 32px 8px;">
      <p style="margin:0 0 10px;color:{cor1};font-size:13px;font-weight:700;
                text-transform:uppercase;letter-spacing:1px;
                border-bottom:2px solid {cor2};padding-bottom:6px;">
        Custodia por Equipe
      </p>
      {tabela_times_cust}
    </td>
  </tr>

  <!-- RANKING CUSTODIA ASSESSORES — DUAS COLUNAS -->
  <tr>
    <td style="padding:20px 16px 20px 32px;vertical-align:top;width:50%;">
      <p style="margin:0 0 10px;color:{cor1};font-size:13px;font-weight:700;
                text-transform:uppercase;letter-spacing:1px;
                border-bottom:2px solid {cor2};padding-bottom:6px;">
        Carteira >= 50mi
      </p>
      {tabela_grande}
    </td>
    <td style="padding:20px 32px 20px 16px;vertical-align:top;width:50%;">
      <p style="margin:0 0 10px;color:{cor1};font-size:13px;font-weight:700;
                text-transform:uppercase;letter-spacing:1px;
                border-bottom:2px solid {cor2};padding-bottom:6px;">
        Carteira < 50mi
      </p>
      {tabela_pequeno}
    </td>
  </tr>"""


def _tabela_custodia_times(df: pd.DataFrame, cor1: str, cor2: str) -> str:
    if df is None or df.empty:
        return '<p style="color:#888;font-size:12px;">Sem dados.</p>'

    linhas = ''
    for _, row in df.iterrows():
        bg = '#f5f5f5' if int(row['posicao']) % 2 == 0 else '#ffffff'
        val = row['total_custodia']
        cor_val = '#1a6e2e' if val >= 0 else '#c0392b'
        linhas += f"""<tr style="background-color:{bg};">
          <td style="padding:8px 10px;text-align:center;font-weight:700;
                     color:{cor1};font-size:12px;width:30px;">{int(row['posicao'])}</td>
          <td style="padding:8px 10px;color:#111111;font-size:13px;font-weight:600;">
            {str(row[config.CUST_TIME]).title()}</td>
          <td style="padding:8px 10px;font-weight:700;text-align:right;
                     font-size:13px;color:{cor_val};">{row['total_custodia_fmt']}</td>
        </tr>"""

    return f"""<table width="100%" cellpadding="0" cellspacing="0"
       style="border-collapse:collapse;border:1px solid #dde3ea;border-radius:6px;">
  <thead><tr style="background-color:{cor1};">
    <th style="padding:9px 10px;color:{cor2};font-size:10px;font-weight:700;
               text-transform:uppercase;text-align:center;width:30px;">#</th>
    <th style="padding:9px 10px;color:{cor2};font-size:10px;font-weight:700;
               text-transform:uppercase;text-align:left;">Equipe</th>
    <th style="padding:9px 10px;color:{cor2};font-size:10px;font-weight:700;
               text-transform:uppercase;text-align:right;">Custodia</th>
  </tr></thead>
  <tbody>{linhas}</tbody>
</table>"""


def _tabela_custodia_assessores(df: pd.DataFrame, cor1: str, cor2: str, label: str) -> str:
    if df is None or df.empty:
        return f'<p style="color:#888;font-size:12px;">Nenhum assessor {label}.</p>'

    linhas = ''
    for _, row in df.iterrows():
        bg = '#f5f5f5' if int(row['posicao']) % 2 == 0 else '#ffffff'
        linhas += f"""<tr style="background-color:{bg};">
          <td style="padding:7px 8px;color:#111111;font-size:12px;">
            {str(row[config.CUST_ASSESSOR]).title()}</td>
          <td style="padding:7px 8px;color:#1a6e2e;font-weight:700;
                     text-align:right;font-size:12px;">{row['total_custodia_fmt']}</td>
        </tr>"""

    return f"""<table width="100%" cellpadding="0" cellspacing="0"
       style="border-collapse:collapse;border:1px solid #dde3ea;">
  <thead><tr style="background-color:{cor1};">
    <th style="padding:8px;color:{cor2};font-size:10px;font-weight:700;
               text-transform:uppercase;text-align:left;">Assessor</th>
    <th style="padding:8px;color:{cor2};font-size:10px;font-weight:700;
               text-transform:uppercase;text-align:right;">Custodia</th>
  </tr></thead>
  <tbody>{linhas}</tbody>
</table>"""


# ── ENVIO VIA WIN32COM — Outlook logado na máquina ───────────────────────────

def _enviar_com_win32(html_corpo: str, destinatario: str, assunto: str) -> None:
    """Envia o e-mail pelo Outlook aberto na maquina, preservando assinatura."""
    import win32com.client

    logger.info("Conectando ao Outlook via win32com...")
    outlook = win32com.client.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)
    mail.To = destinatario
    mail.Subject = assunto

    # Seta o corpo do e-mail diretamente
    mail.HTMLBody = html_corpo
    mail.Send()
    logger.info(f"  → E-mail enviado para {destinatario}")


# ── ENVIO VIA SMTP — funciona em nuvem / sem Outlook ─────────────────────────

def _enviar_com_smtp(html_corpo: str, destinatario: str, assunto: str) -> None:
    """Envia o e-mail via SMTP (Office 365, Gmail ou qualquer servidor SMTP).

    Configuração via variáveis de ambiente ou config.py:
      SMTP_HOST     - servidor SMTP       (padrão: smtp.office365.com)
      SMTP_PORT     - porta               (padrão: 587)
      SMTP_USER     - usuário/remetente   (ex: relatorio@nobelcapital.com.br)
      SMTP_PASSWORD - senha ou app-password
      SMTP_FROM     - remetente exibido   (padrão: igual a SMTP_USER)
    """
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    if not config.SMTP_USER or not config.SMTP_PASSWORD:
        raise ValueError(
            "SMTP_USER e SMTP_PASSWORD não configurados. "
            "Defina as variáveis de ambiente ou configure config.py."
        )

    logger.info(f"Enviando e-mail via SMTP ({config.SMTP_HOST}:{config.SMTP_PORT})...")

    msg = MIMEMultipart('alternative')
    msg['Subject'] = assunto
    msg['From']    = config.SMTP_FROM or config.SMTP_USER
    msg['To']      = destinatario
    msg.attach(MIMEText(html_corpo, 'html', 'utf-8'))

    with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as servidor:
        servidor.ehlo()
        servidor.starttls()
        servidor.login(config.SMTP_USER, config.SMTP_PASSWORD)
        servidor.sendmail(config.SMTP_USER, destinatario, msg.as_string())

    logger.info(f"  → E-mail enviado para {destinatario}")


# ── DISPATCHER PRINCIPAL ──────────────────────────────────────────────────────

def enviar_relatorio(
    resumo: dict,
    rank_times: pd.DataFrame,
    rank_positivos: pd.DataFrame,
    rank_negativos: pd.DataFrame,
    resumo_cust: dict = None,
    rank_cust_times: pd.DataFrame = None,
    rank_cust_grande: pd.DataFrame = None,
    rank_cust_pequeno: pd.DataFrame = None,
    data_atualizacao: str = None,
    grafico_captacao_b64: str = '',
) -> None:
    """Gera o HTML e envia via Outlook (local) ou SMTP (nuvem)."""
    html = gerar_html_relatorio(
        resumo, rank_times, rank_positivos, rank_negativos,
        resumo_cust, rank_cust_times, rank_cust_grande, rank_cust_pequeno,
        data_atualizacao=data_atualizacao,
        grafico_captacao_b64=grafico_captacao_b64,
    )

    if config.MODO_TESTE_EMAIL:
        logger.info("MODO_TESTE_EMAIL=True — salvando HTML em preview_email.html")
        with open('preview_email.html', 'w', encoding='utf-8') as f:
            f.write(html)
        logger.info("  → Arquivo salvo: preview_email.html")
        return

    modo = getattr(config, 'EMAIL_MODO', 'outlook').lower()
    if modo == 'smtp':
        _enviar_com_smtp(html, config.EMAIL_DESTINATARIO, config.ASSUNTO_EMAIL)
    else:
        _enviar_com_win32(html, config.EMAIL_DESTINATARIO, config.ASSUNTO_EMAIL)
