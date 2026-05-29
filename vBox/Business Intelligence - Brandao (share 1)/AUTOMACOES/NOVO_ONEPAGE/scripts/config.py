"""
config.py
Configurações do projeto NOVO_ONEPAGE — pipeline Excel → Cloudflare D1.

Cada tabela define:
  *_RENAME  : {coluna_excel_normalizada → coluna_d1}
  *_COLUMNS : lista de colunas D1 na ordem do INSERT

Normalização de colunas Excel: NFKD sem combining chars, strip.
Ex: "Capitação Líquida" → "Capitacao Liquida"
    "Núcleo"            → "Nucleo"
"""
import glob
import os

# ── CAMINHOS ─────────────────────────────────────────────────────────────────
CAMINHO_BASE = os.environ.get('CAMINHO_BASE', r'C:\Users\Usuário\vBox\ONE PAGE')


def _glob_arquivo(pasta, padrao):
    res = [
        f for f in glob.glob(os.path.join(pasta, padrao))
        if not os.path.basename(f).startswith('~$')
        and 'Copia' not in os.path.basename(f)
    ]
    return res[0] if res else None


ARQUIVO_1 = _glob_arquivo(CAMINHO_BASE, '*BASES ONE PAGE*.xlsx')
ARQUIVO_2 = _glob_arquivo(CAMINHO_BASE, 'ONE PAGE - ATUAL_V2.xlsm')
ARQUIVO_METAS = os.environ.get(
    'ARQUIVO_METAS',
    r'C:\Users\Usuário\vBox\Business Intelligence - Brandao (share 1)\metas_times.xlsx',
)
_script_dir = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_ASSESSORES = next(
    (p for p in [
        os.path.join(_script_dir, 'assessor.json'),
        os.path.join(_script_dir, '..', 'assessor.json'),
    ] if os.path.exists(p)),
    os.path.join(_script_dir, 'assessor.json'),
)
ARQUIVO_CUSTODIA_LD  = os.path.join(CAMINHO_BASE, 'TESTE', 'Custódia em LD.xlsx')
ARQUIVO_HOTLIST_LD   = os.path.join(CAMINHO_BASE, 'TESTE', 'Hotlist - concentração LD.xlsx')
ARQUIVO_POSICAO_COE  = os.path.join(CAMINHO_BASE, 'TESTE', 'p_coe.xlsx')
ARQUIVO_RENTAB       = os.path.join(CAMINHO_BASE, 'TESTE', 'Rentabilidade.xlsx')
ARQUIVO_ANALITICO_RF = os.path.join(CAMINHO_BASE, 'TESTE', 'analitico_rf.xlsx')
ARQUIVO_ANALITICO_RV = os.path.join(CAMINHO_BASE, 'TESTE', 'analitico_rv.xlsx')
SHEET_NOVOS          = 'Export'

ARQUIVO_BASE_CLIENTES = os.environ.get(
    'ARQUIVO_BASE_CLIENTES',
    os.path.join(CAMINHO_BASE, 'TESTE', 'Base de Clientes e Assessores.xlsx'),
)
SHEET_BASE_CLIENTES = os.environ.get('SHEET_BASE_CLIENTES', 'Base')

# ── SHEETS ───────────────────────────────────────────────────────────────────
SHEET_TB_CAP            = 'TB_CAP'
SHEET_TB_POSITIVADOR    = 'TB_POSITIVADOR'
SHEET_HISTORICO_CAP     = 'HISTÓRICO CAP'
SHEET_HISTORICO_ROA     = 'HISTÓRICO ROA'
SHEET_HISTORICO_CUSTODIA = 'HISTORICO CUSTODIA'
SHEET_RECEITA           = 'RECEITA PROJETADA'

# ─────────────────────────────────────────────────────────────────────────────
# TB_CAP
# Fonte: ATUALIZAÇÃO - BASES ONE PAGE.xlsx → TB_CAP
# ─────────────────────────────────────────────────────────────────────────────
TB_CAP_RENAME = {
    'Escritorio':       'escritorio',      # Escritório
    'Data':             'data',
    'Codigo Real':      'id_assessor',
    'Assessor':         'nome_assessor',
    'Nucleo':           'equipe',          # Núcleo
    'Cod do Cliente':   'id_cliente',      # Cód do Cliente
    'Tipo de Captacao': 'tipo',            # Tipo de Captação
    'Aux':              'aux',
    'Captacao':         'captacao',        # Captação
    'Data Atualizacao': 'data_atualizacao',# Data Atualização
}
TB_CAP_COLUMNS = [
    'escritorio', 'data', 'id_assessor', 'nome_assessor', 'equipe',
    'id_cliente', 'tipo', 'aux', 'captacao', 'data_atualizacao',
]

# ─────────────────────────────────────────────────────────────────────────────
# TB_POSITIVADOR
# Fonte: ATUALIZAÇÃO - BASES ONE PAGE.xlsx → TB_POSITIVADOR
# ─────────────────────────────────────────────────────────────────────────────
TB_POS_RENAME = {
    'Codigo Real':  'id_assessor',          # Código Real
    'Assessor':     'nome_assessor',
    'Nucleo':       'equipe',               # Núcleo
    'Cliente':      'id_cliente',
    'Status':       'status',
    'Ativou em M?': 'ativou_em_m',
    'Net Em M':     'net_em_m',
    'Tipo Pessoa':  'tipo_pessoa',
    'Aplicacao Financeira Declarada Ajustada': 'afd_ajustada',  # Aplicação...
    'Data Posicao': 'data_posicao',         # Data Posição
    'Data Atualizacao': 'data_atualizacao', # Data Atualização
}
TB_POS_COLUMNS = [
    'id_assessor', 'nome_assessor', 'equipe', 'id_cliente', 'status',
    'ativou_em_m', 'net_em_m', 'tipo_pessoa', 'afd_ajustada',
    'data_posicao', 'data_atualizacao',
]

# ─────────────────────────────────────────────────────────────────────────────
# TB_DIVERSIFICADOR
# Fonte: ATUALIZAÇÃO - BASES ONE PAGE.xlsx → TB_DIVERSIFICADOR
# ─────────────────────────────────────────────────────────────────────────────
TB_DIV_RENAME = {
    # Colunas normalizadas (NFKD sem combining chars, strip)
    # Ex: "Núcleo" → "Nucleo", "Posição" → "Posicao"
    'Codigo_Real':         'id_assessor',
    'Assessor':            'nome_assessor',
    'Nucleo':              'equipe',
    'Cliente':             'id_cliente',
    'Produto_Novo1':       'produto',
    'Sub Produto':         'sub_produto',
    'Produto em Garantia': 'produto_garantia',
    'CNPJ Fundo':          'cnpj_fundo',
    'Ativo':               'ativo',
    'Emissor':             'emissor',
    'Data de Vencimento':  'data_vencimento',
    'Quantidade':          'quantidade',
    'NET':                 'net',
    'Data Posicao':        'data_posicao',
    'Data Atualizacao':    'data_atualizacao',
    'Codigo Cliente BR':   'id_cliente_br',
}
TB_DIV_COLUMNS = [
    'id_assessor', 'nome_assessor', 'equipe', 'id_cliente',
    'produto', 'sub_produto', 'produto_garantia', 'cnpj_fundo',
    'ativo', 'emissor', 'data_vencimento', 'quantidade',
    'net', 'data_posicao', 'data_atualizacao', 'id_cliente_br',
]

# ─────────────────────────────────────────────────────────────────────────────
# CAP_HISTORICA
# Fonte: ONE PAGE - ATUAL_V2.xlsm → HISTÓRICO CAP
# ─────────────────────────────────────────────────────────────────────────────
CAPTACAO_RENAME = {
    'Cod. Assessor':    'id_assessor',    # Cód. Assessor
    'Nome Assessor':    'nome_assessor',
    'Nucleo':           'equipe',         # Núcleo
    'Capitacao Liquida':'captacao',       # Capitação Líquida
    'Periodo':          'data',           # Período
}
CAPTACAO_COLUMNS = ['id_assessor', 'nome_assessor', 'equipe', 'captacao', 'data']

# ─────────────────────────────────────────────────────────────────────────────
# ROA_HISTORICO
# Fonte: ONE PAGE - ATUAL_V2.xlsm → HISTÓRICO ROA
# Nota: "Assessor" (nome) descartado; id_assessor vem de "Id_Assessor"
# ─────────────────────────────────────────────────────────────────────────────
ROA_RENAME = {
    'Id_Assessor':                    'id_assessor',
    'Nucleo':                         'equipe',           # Núcleo
    'Periodo':                        'data',             # Período
    'sum(grp.receita)':               'receita',
    'Media de Receita':               'media_receita',    # Média de Receita
    'Media Receita AUM(ate periodo)': 'media_receita_aum',
    'roa':                            'roa',
    'Roa Anualizado':                 'roa_anualizado',
}
ROA_COLUMNS = [
    'id_assessor', 'equipe', 'data', 'receita',
    'media_receita', 'media_receita_aum', 'roa', 'roa_anualizado',
]

# ─────────────────────────────────────────────────────────────────────────────
# CUST_HISTORICA
# Fonte: ONE PAGE - ATUAL_V2.xlsm → HISTORICO CUSTODIA
# ─────────────────────────────────────────────────────────────────────────────
CUSTODIA_RENAME = {
    'Cliente':    'id_cliente',
    'Assessor':   'id_assessor',   # código do assessor
    'Assessor2':  'nome_assessor',
    'Total':      'total',
    'Produto':    'produto',
    'Cli':        'cli',
    'SubProduto': 'sub_produto',
    'periodo':    'data',          # período
    'Nucleo':     'equipe',        # Núcleo
}
CUSTODIA_COLUMNS = [
    'id_cliente', 'id_assessor', 'nome_assessor', 'total',
    'produto', 'cli', 'sub_produto', 'data', 'equipe',
]

# ─────────────────────────────────────────────────────────────────────────────
# RECEITA PROJETADA — blocos horizontais
# A sheet tem todos os blocos lado a lado. Linha 0 = títulos dos blocos,
# linha 1 = cabeçalhos, linha 2+ = dados.
#
# col_start / col_end : faixa de colunas (Python slice, end exclusive)
# rename              : {excel_col_normalizado → coluna_d1}
# columns             : lista de colunas D1 na ordem do INSERT
# ─────────────────────────────────────────────────────────────────────────────
RECEITA_BLOCOS = {

    'rv': {
        'col_start': 0,
        'col_end':   7,
        'rename': {
            'Conta':            'id_cliente',
            'Total':            'total',
            'Cod A':            'id_assessor',
            'Tipo Corretagem':  'tipo_corretagem',
            'Canal':            'canal',
            'Receita':          'receita',
            'Nucleo':           'cliente',   # conforme mapeamento solicitado
        },
        'columns': [
            'id_cliente', 'total', 'id_assessor', 'tipo_corretagem',
            'canal', 'receita', 'cliente', 'nucleo2',
        ],
    },

    'rf': {
        'col_start': 8,
        'col_end':   16,
        'rename': {
            'Receita a Dividir': 'receita_a_dividir',
            'Receita':           'receita',
            'Nucleo2':           'nucleo2',
            'Tipo':              'tipo',
            'Oferta':            'oferta',
        },
        'columns': [
            'id_cliente', 'id_assessor', 'receita_a_dividir', 'receita',
            'equipe', 'nucleo2', 'tipo', 'oferta',
        ],
    },

    'coe': {
        'col_start': 16,
        'col_end':   21,
        'rename': {
            'Receita': 'receita',
            'data':    'data_ref',
        },
        'columns': ['id_assessor', 'receita', 'equipe', 'data_ref', 'id_cliente'],
    },

    'cambio': {
        'col_start': 35,
        'col_end':   39,
        'rename': {
            'id_cliente':  'id_cliente',
            'id_assessor': 'id_assessor',
            'receita':     'receita',
            'equipe':      'equipe',
        },
        'columns': ['id_cliente', 'id_assessor', 'receita', 'equipe'],
    },

    'seguros': {
        'col_start': 22,
        'col_end':   32,
        'rename': {
            'Cliente':     'id_cliente',
            'Cod Assessor':'id_assessor',
            'Assessor':    'nome_assessor',
            'Apolice':     'apolice',
            'Data Apolice':'data_apolice',   # Data Apólice
            'Periodo':     'data',
            'Valor Parcela':'valor_parcela',
            'Data Fim':    'data_fim',
            'Receita':     'receita',
        },
        'columns': [
            'id_cliente', 'id_assessor', 'nome_assessor', 'apolice',
            'data_apolice', 'data', 'valor_parcela', 'data_fim', 'receita',
        ],
    },

    'dominion': {
        'col_start': 72,
        'col_end':   83,
        # col 81 = "5,7" (fórmula) → não está no rename, será descartada
        'rename': {
            'Numero de transacao / Cliente': 'num_transacao',
            'Status':                        'status',
            'EPIs':                          'epis',
            'Tipo de transacao':             'tipo_transacao',
            'id_cliente':                    'conta',
            'Consultor':                     'consultor',
            'Atualizado em':                 'data_atualizacao',
        },
        'columns': [
            'num_transacao', 'status', 'epis', 'tipo_transacao',
            'conta', 'consultor', 'data_atualizacao', 'id_assessor',
            'receita', 'equipe',
        ],
    },

    'oferta_fundos': {
        'col_start': 88,
        'col_end':   98,
        'dropna_key': 'id_assessor',
        'rename': {
            'Codigo':       'id_assessor',
            'nome':         'nome_assessor',
            'time':         'equipe',
            'time2':        'nucleo2',
            'Cliente':      'id_cliente',
            'Valor':        'valor',
            'Comissao Fee': 'comissao_fee',   # Comissão Fee
            'Comissao Real':'receita',         # Comissão Real
            'Oferta Fundo': 'ativo',
            'FEE':          'fee',
        },
        'columns': [
            'id_assessor', 'nome_assessor', 'equipe', 'nucleo2',
            'id_cliente', 'valor', 'comissao_fee', 'receita', 'ativo', 'fee',
        ],
    },

    'consorcio': {
        'col_start': 98,
        'col_end':   110,
        'rename': {
            'Data':              'data_ref',
            'nome_cliente':      'id_cliente',
            'Nucleo2':           'nucleo2',
            'Empresa':           'empresa',
            'Produto':           'produto',
            'Valor da Venda':    'valor_venda',
            'Comissao':          'comissao',
            'Parcelas':          'parcelas',
        },
        'columns': [
            'data_ref', 'id_cliente', 'equipe', 'nucleo2',
            'id_assessor', 'nome_assessor', 'empresa', 'produto',
            'valor_venda', 'comissao', 'parcelas', 'receita',
        ],
    },

    'feefixo': {
        'col_start': 110,
        'col_end':   118,
        'rename': {
            'Divisao Receita (Total)': 'divisao_receita',
            'Classificacao':           'classificacao',
            'Nucleo2':                 'nucleo2',
        },
        'columns': [
            'divisao_receita', 'classificacao', 'id_cliente', 'id_assessor',
            'nome_assessor', 'equipe', 'nucleo2', 'receita',
        ],
    },

    'parceiros': {
        'col_start':  66,
        'col_end':    71,
        'header_row': 2,
        'dropna_key': 'id_assessor',
        'rename': {
            'id_assessor':   'id_assessor',
            'nome_assessor': 'nome_assessor',
            'id_cliente':    'id_cliente',
            'equipe':        'equipe',
            'receita':       'receita',
        },
        'columns': ['id_assessor', 'nome_assessor', 'id_cliente', 'equipe', 'receita'],
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# CUSTODIA_LD
# Fonte: ONE PAGE\TESTE\Custódia em LD.xlsx → Export
# ─────────────────────────────────────────────────────────────────────────────
CUSTODIA_LD_RENAME = {
    'cod_assessor': 'id_assessor',
    'Cod. conta':   'id_cliente',
    'Ticker':       'ticker',
    'Nome papel':   'nome_papel',
    'Custodia':     'custodia',
    'Vencimento':   'vencimento',
    'indexador':    'indexador',
    'Taxa cliente': 'taxa_cliente',
}
CUSTODIA_LD_COLUMNS = [
    'id_assessor', 'id_cliente', 'ticker', 'nome_papel',
    'custodia', 'vencimento', 'indexador', 'taxa_cliente',
]

# ─────────────────────────────────────────────────────────────────────────────
# HOTLIST_LD
# Fonte: ONE PAGE\TESTE\Hotlist - concentração LD.xlsx → Export
# ─────────────────────────────────────────────────────────────────────────────
HOTLIST_LD_RENAME = {
    'cod_assessor':           'id_assessor',
    'Cod. conta':             'id_cliente',
    'Custodia':               'custodia',
    'Custodia (EB LD + LFT)': 'custodia_eb_ld',
    '% Liquidez':             'pct_liquidez',
}
HOTLIST_LD_COLUMNS = [
    'id_assessor', 'id_cliente', 'custodia', 'custodia_eb_ld', 'pct_liquidez',
]

# ─────────────────────────────────────────────────────────────────────────────
# POSICAO_COE
# Fonte: ONE PAGE\TESTE\p_coe.xlsx → Export
# ─────────────────────────────────────────────────────────────────────────────
POSICAO_COE_RENAME = {
    'CD_CLIENTE':          'id_cliente',
    'NOME':                'nome_cliente',
    'DATA_COMPRA':         'data_compra',
    'VALOR_COMPRA':        'valor_compra',
    'POSICAO_ATUAL':       'posicao_atual',
    'CUPOM_RECEBIDO':      'cupom_recebido',
    'DT_VENCIMENTO':       'vencimento',
    'TIPO':                'tipo',
    'PU_INICIAL_BOND':     'pu_inicial',
    'PU_ATUAL_BOND':       'pu_atual',
    'BARREIRA_VENC_OBRIG': 'barreira_venc',
    'COD_ASSESSOR':        'id_assessor',
}
POSICAO_COE_COLUMNS = [
    'id_cliente', 'nome_cliente', 'data_compra', 'valor_compra',
    'posicao_atual', 'cupom_recebido', 'vencimento', 'tipo',
    'pu_inicial', 'pu_atual', 'barreira_venc', 'id_assessor',
]

# ─────────────────────────────────────────────────────────────────────────────
# RENTABILIDADE
# Fonte: ONE PAGE\TESTE\Rentabilidade.xlsx → Export
# ─────────────────────────────────────────────────────────────────────────────
RENTABILIDADE_RENAME = {
    'Ano Mes':                      'ano_mes',
    'Cod. Assessor':                'id_assessor',
    'Cod Conta':                    'id_cliente',
    'Data Calculo Rentabilidade':   'data_calculo',
    'Rent. Bruta Mensal':           'rent_bruta_mensal',
    'Rent. Liquida Mensal':         'rent_liquida_mensal',
    'Rent. Relativa Bruta Mensal':  'rent_rel_bruta_mensal',
    'Rent. Relativa Liquida':       'rent_rel_liquida_mensal',
    'Rent. Bruta Anual':            'rent_bruta_anual',
    'Rent. Liquida Anual':          'rent_liquida_anual',
    'Rent. Relativa Bruta Anual':   'rent_rel_bruta_anual',
    'Rent. Relativa Liquida Anual': 'rent_rel_liquida_anual',
}
RENTABILIDADE_COLUMNS = [
    'ano_mes', 'id_assessor', 'id_cliente', 'data_calculo',
    'rent_bruta_mensal', 'rent_liquida_mensal',
    'rent_rel_bruta_mensal', 'rent_rel_liquida_mensal',
    'rent_bruta_anual', 'rent_liquida_anual',
    'rent_rel_bruta_anual', 'rent_rel_liquida_anual',
]

# ─────────────────────────────────────────────────────────────────────────────
# ANALITICO_RF
# Fonte: ONE PAGE\TESTE\analitico_rf.xlsx → Export
# ─────────────────────────────────────────────────────────────────────────────
ANALITICO_RF_RENAME = {
    'cod_assessor':          'id_assessor',
    'Cod. conta':            'id_cliente',
    'Suitabilty':            'suitability',   # typo preservado da fonte
    'Tipo Pessoa':           'tipo_pessoa',
    'Flag marcacao':         'flag_marcacao',
    'Tipo ativo':            'tipo_ativo',
    'flag_liquidez':         'flag_liquidez',
    'indexador':             'indexador',
    'Nome ativo':            'nome_ativo',
    'Vencimento':            'vencimento',
    'Valor aplicado':        'valor_aplicado',
    'Posicao atual':         'posicao_atual',
    'Taxa de compra':        'taxa_compra',
    'Quantidade':            'quantidade',
    'Ticker':                'ticker',
    'Data aplicacao':        'data_aplicacao',
    'Total pago em eventos': 'total_eventos',
}
ANALITICO_RF_COLUMNS = [
    'id_assessor', 'id_cliente', 'suitability', 'tipo_pessoa',
    'flag_marcacao', 'tipo_ativo', 'flag_liquidez', 'indexador',
    'nome_ativo', 'vencimento', 'valor_aplicado', 'posicao_atual',
    'taxa_compra', 'quantidade', 'ticker', 'data_aplicacao', 'total_eventos',
]

# ─────────────────────────────────────────────────────────────────────────────
# ANALITICO_RV
# Fonte: ONE PAGE\TESTE\analitico_rv.xlsx → Export
# ─────────────────────────────────────────────────────────────────────────────
ANALITICO_RV_RENAME = {
    'Conta':        'id_cliente',
    'Suitability':  'suitability',
    'Cod Assessor': 'id_assessor',
    'Cod Matriz':   'cod_matriz',
    'Matriz':       'matriz',
    'Ativo':        'ativo',
    'Qtde':         'quantidade',
    'AUC':          'auc',
    'Preco Medio':  'preco_medio',
    'Val Abertura': 'val_abertura',
    'Variacao':     'variacao',
    'Produto':      'produto',
    'Setor':        'setor',
    'Subsetor':     'subsetor',
}
ANALITICO_RV_COLUMNS = [
    'id_cliente', 'suitability', 'id_assessor', 'cod_matriz', 'matriz',
    'ativo', 'quantidade', 'auc', 'preco_medio', 'val_abertura',
    'variacao', 'produto', 'setor', 'subsetor',
]

# ─────────────────────────────────────────────────────────────────────────────
# BASE_CLIENTES
# Fonte: ONE PAGE\TESTE\Base de Clientes e Assessores.xlsx → Base
# Upsert por id_cliente (INSERT OR REPLACE — sem DROP da tabela)
# ─────────────────────────────────────────────────────────────────────────────
BASE_CLIENTES_RENAME = {
    'id_cliente':            'id_cliente',
    'nome_cliente':          'nome_cliente',
    'id_assessor':           'id_assessor',
    'nome_assessor':         'nome_assessor',
    'equipe':                'equipe',
    'email_cliente':         'email_cliente',
    'email_assessor':        'email_assessor',
    'Perfil do Suitability': 'suitability',
    'Cliente Nobel?':        'cliente_nobel',
    'status':                'status',
    'Tipo Pessoa':           'tipo_pessoa',
    'patrimonio':            'patrimonio',    # pode vir como 'Patrimonio' após NFKD
    'Patrimonio':            'patrimonio',
    'CPF / CNPJ':            'cpf_cnpj',
    'Nascimento':            'nascimento',
    'Telefone':              'telefone',
}
BASE_CLIENTES_COLUMNS = [
    'id_cliente', 'nome_cliente', 'id_assessor', 'nome_assessor', 'equipe',
    'email_cliente', 'email_assessor', 'suitability', 'cliente_nobel',
    'status', 'tipo_pessoa', 'patrimonio', 'cpf_cnpj', 'nascimento', 'telefone',
]
