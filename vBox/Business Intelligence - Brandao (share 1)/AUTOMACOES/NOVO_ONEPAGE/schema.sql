-- schema.sql
-- Cloudflare D1 — nobel-performance-db
-- Nobel Capital — pipeline de performance
-- Recria todas as tabelas com schema atualizado (DROP + CREATE)

DROP TABLE IF EXISTS tb_cap;
CREATE TABLE tb_cap (
  escritorio       TEXT,
  data             TEXT,
  id_assessor      TEXT,
  nome_assessor    TEXT,
  equipe           TEXT,
  id_cliente       TEXT,
  tipo             TEXT,
  aux              TEXT,
  captacao         REAL,
  data_atualizacao TEXT
);

DROP TABLE IF EXISTS tb_positivador;
CREATE TABLE tb_positivador (
  id_assessor      TEXT,
  nome_assessor    TEXT,
  equipe           TEXT,
  id_cliente       INTEGER,
  status           TEXT,
  ativou_em_m      TEXT,
  net_em_m         REAL,
  tipo_pessoa      TEXT,
  afd_ajustada     REAL,
  data_posicao     TEXT,
  data_atualizacao TEXT
);

DROP TABLE IF EXISTS cap_historica;
CREATE TABLE cap_historica (
  id_assessor   TEXT,
  nome_assessor TEXT,
  equipe        TEXT,
  captacao      REAL,
  data          TEXT
);

DROP TABLE IF EXISTS roa_historico;
CREATE TABLE roa_historico (
  id_assessor       TEXT,
  equipe            TEXT,
  data              TEXT,
  receita           REAL,
  media_receita     REAL,
  media_receita_aum REAL,
  roa               REAL,
  roa_anualizado    REAL
);

DROP TABLE IF EXISTS cust_historica;
CREATE TABLE cust_historica (
  id_cliente    INTEGER,
  id_assessor   TEXT,
  nome_assessor TEXT,
  total         REAL,
  produto       TEXT,
  cli           REAL,
  sub_produto   TEXT,
  data          TEXT,
  equipe        TEXT
);

DROP TABLE IF EXISTS tb_diversificador;
CREATE TABLE tb_diversificador (
  id_assessor      TEXT,
  nome_assessor    TEXT,
  equipe           TEXT,
  id_cliente       TEXT,
  produto          TEXT,
  sub_produto      TEXT,
  produto_garantia TEXT,
  cnpj_fundo       TEXT,
  ativo            TEXT,
  emissor          TEXT,
  data_vencimento  TEXT,
  quantidade       REAL,
  net              REAL,
  data_posicao     TEXT,
  data_atualizacao TEXT,
  id_cliente_br    TEXT
);

DROP TABLE IF EXISTS receita_rv;
CREATE TABLE receita_rv (
  id_cliente      INTEGER,
  total           REAL,
  id_assessor     TEXT,
  tipo_corretagem TEXT,
  canal           TEXT,
  receita         REAL,
  cliente         TEXT,
  nucleo2         TEXT
);

DROP TABLE IF EXISTS receita_rf;
CREATE TABLE receita_rf (
  id_cliente        INTEGER,
  id_assessor       TEXT,
  receita_a_dividir REAL,
  receita           REAL,
  equipe            TEXT,
  nucleo2           TEXT,
  tipo              TEXT,
  oferta            TEXT
);

DROP TABLE IF EXISTS receita_coe;
CREATE TABLE receita_coe (
  id_assessor TEXT,
  receita     REAL,
  equipe      TEXT,
  data_ref    TEXT,
  id_cliente  INTEGER
);

DROP TABLE IF EXISTS receita_seguros;
CREATE TABLE receita_seguros (
  id_cliente    TEXT,
  id_assessor   TEXT,
  nome_assessor TEXT,
  apolice       REAL,
  data_apolice  TEXT,
  data          TEXT,
  valor_parcela REAL,
  data_fim      TEXT,
  receita       REAL
);

DROP TABLE IF EXISTS receita_dominion;
CREATE TABLE receita_dominion (
  num_transacao    TEXT,
  status           TEXT,
  epis             TEXT,
  tipo_transacao   TEXT,
  conta            TEXT,
  consultor        TEXT,
  data_atualizacao TEXT,
  id_assessor      TEXT,
  receita          REAL,
  equipe           TEXT
);

DROP TABLE IF EXISTS receita_oferta_fundos;
CREATE TABLE receita_oferta_fundos (
  id_assessor   TEXT,
  nome_assessor TEXT,
  equipe        TEXT,
  nucleo2       TEXT,
  id_cliente    TEXT,
  valor         REAL,
  comissao_fee  REAL,
  receita       REAL,
  ativo         TEXT,
  fee           REAL
);

DROP TABLE IF EXISTS receita_consorcio;
CREATE TABLE receita_consorcio (
  data_ref      TEXT,
  id_cliente    TEXT,
  equipe        TEXT,
  nucleo2       TEXT,
  id_assessor   TEXT,
  nome_assessor TEXT,
  empresa       TEXT,
  produto       TEXT,
  valor_venda   REAL,
  comissao      REAL,
  parcelas      INTEGER,
  receita       REAL
);

DROP TABLE IF EXISTS receita_cambio;
CREATE TABLE receita_cambio (
  id_cliente  TEXT,
  id_assessor TEXT,
  receita     REAL,
  equipe      TEXT
);

DROP TABLE IF EXISTS receita_feefixo;
CREATE TABLE receita_feefixo (
  divisao_receita REAL,
  classificacao   TEXT,
  id_cliente      TEXT,
  id_assessor     TEXT,
  nome_assessor   TEXT,
  equipe          TEXT,
  nucleo2         TEXT,
  receita         REAL
);

DROP TABLE IF EXISTS receita_parceiros;
CREATE TABLE receita_parceiros (
  id_assessor   TEXT,
  nome_assessor TEXT,
  id_cliente    TEXT,
  equipe        TEXT,
  receita       REAL
);

DROP TABLE IF EXISTS custodia_ld;
CREATE TABLE custodia_ld (
  id_assessor  TEXT,
  id_cliente   TEXT,
  ticker       TEXT,
  nome_papel   TEXT,
  custodia     REAL,
  vencimento   TEXT,
  indexador    TEXT,
  taxa_cliente REAL
);

DROP TABLE IF EXISTS hotlist_ld;
CREATE TABLE hotlist_ld (
  id_assessor    TEXT,
  id_cliente     TEXT,
  custodia       REAL,
  custodia_eb_ld REAL,
  pct_liquidez   REAL
);

DROP TABLE IF EXISTS posicao_coe;
CREATE TABLE posicao_coe (
  id_cliente     TEXT,
  nome_cliente   TEXT,
  data_compra    TEXT,
  valor_compra   REAL,
  posicao_atual  REAL,
  cupom_recebido REAL,
  vencimento     TEXT,
  tipo           TEXT,
  pu_inicial     REAL,
  pu_atual       REAL,
  barreira_venc  TEXT,
  id_assessor    TEXT
);

DROP TABLE IF EXISTS rentabilidade;
CREATE TABLE rentabilidade (
  ano_mes                 TEXT,
  id_assessor             TEXT,
  id_cliente              TEXT,
  data_calculo            TEXT,
  rent_bruta_mensal       REAL,
  rent_liquida_mensal     REAL,
  rent_rel_bruta_mensal   REAL,
  rent_rel_liquida_mensal REAL,
  rent_bruta_anual        REAL,
  rent_liquida_anual      REAL,
  rent_rel_bruta_anual    REAL,
  rent_rel_liquida_anual  REAL
);

DROP TABLE IF EXISTS analitico_rf;
CREATE TABLE analitico_rf (
  id_assessor    TEXT,
  id_cliente     TEXT,
  suitability    TEXT,
  tipo_pessoa    TEXT,
  flag_marcacao  TEXT,
  tipo_ativo     TEXT,
  flag_liquidez  TEXT,
  indexador      TEXT,
  nome_ativo     TEXT,
  vencimento     TEXT,
  valor_aplicado REAL,
  posicao_atual  REAL,
  taxa_compra    REAL,
  quantidade     REAL,
  ticker         TEXT,
  data_aplicacao TEXT,
  total_eventos  REAL
);

DROP TABLE IF EXISTS analitico_rv;
CREATE TABLE analitico_rv (
  id_cliente   TEXT,
  suitability  TEXT,
  id_assessor  TEXT,
  cod_matriz   TEXT,
  matriz       TEXT,
  ativo        TEXT,
  quantidade   REAL,
  auc          REAL,
  preco_medio  REAL,
  val_abertura REAL,
  variacao     REAL,
  produto      TEXT,
  setor        TEXT,
  subsetor     TEXT
);

-- receita_fundos / receita_prev: views calculadas sobre tb_diversificador
-- repasse: 0,020% = 0.0002 sobre NET do produto
DROP VIEW IF EXISTS receita_fundos;
CREATE VIEW receita_fundos AS
SELECT
  id_assessor,
  nome_assessor,
  equipe,
  id_cliente,
  data_posicao                 AS data,
  SUM(net)                     AS net_total,
  ROUND(SUM(net) * 0.0002, 2)  AS receita
FROM tb_diversificador
WHERE produto = 'Fundos'
GROUP BY id_assessor, nome_assessor, equipe, id_cliente, data_posicao;

DROP VIEW IF EXISTS receita_prev;
CREATE VIEW receita_prev AS
SELECT
  id_assessor,
  nome_assessor,
  equipe,
  id_cliente,
  data_posicao                 AS data,
  SUM(net)                     AS net_total,
  ROUND(SUM(net) * 0.0002, 2)  AS receita
FROM tb_diversificador
WHERE produto = 'Previdência'
GROUP BY id_assessor, nome_assessor, equipe, id_cliente, data_posicao;

-- assessores: mantida via assessor.json (sem DROP para preservar dados)
CREATE TABLE IF NOT EXISTS assessores (
  id_assessor   TEXT PRIMARY KEY,
  nome_assessor TEXT,
  equipe        TEXT,
  status        TEXT,
  mail_assessor TEXT
);

-- base_clientes: mantida via upsert (sem DROP para preservar dados)
CREATE TABLE IF NOT EXISTS base_clientes (
  id_cliente     INTEGER PRIMARY KEY,
  nome_cliente   TEXT,
  id_assessor    TEXT,
  nome_assessor  TEXT,
  equipe         TEXT,
  email_cliente  TEXT,
  email_assessor TEXT,
  suitability    TEXT,
  cliente_nobel  TEXT,
  status         TEXT,
  tipo_pessoa    TEXT,
  patrimonio     REAL,
  cpf_cnpj       TEXT,
  nascimento     TEXT,
  telefone       TEXT
);

DROP TABLE IF EXISTS tb_metas_times;
CREATE TABLE tb_metas_times (
  equipe    TEXT,
  janeiro   REAL,
  fevereiro REAL,
  marco     REAL,
  abril     REAL,
  maio      REAL,
  junho     REAL,
  julho     REAL,
  agosto    REAL,
  setembro  REAL,
  outubro   REAL,
  novembro  REAL,
  dezembro  REAL
);

DROP TABLE IF EXISTS meta_captacao;
CREATE TABLE meta_captacao (
  id_assessor    TEXT,
  nome_assessor  TEXT,
  equipe         TEXT,
  status         TEXT,
  email_assessor TEXT,
  janeiro        REAL,
  fevereiro      REAL,
  marco          REAL,
  abril          REAL,
  maio           REAL,
  junho          REAL,
  julho          REAL,
  agosto         REAL,
  setembro       REAL,
  outubro        REAL,
  novembro       REAL,
  dezembro       REAL
);

DROP TABLE IF EXISTS meta_receita;
CREATE TABLE meta_receita (
  id_assessor    TEXT,
  nome_assessor  TEXT,
  equipe         TEXT,
  status         TEXT,
  email_assessor TEXT,
  janeiro        REAL,
  fevereiro      REAL,
  marco          REAL,
  abril          REAL,
  maio           REAL,
  junho          REAL,
  julho          REAL,
  agosto         REAL,
  setembro       REAL,
  outubro        REAL,
  novembro       REAL,
  dezembro       REAL
);

CREATE TABLE IF NOT EXISTS metadata (
  chave      TEXT PRIMARY KEY,
  valor      TEXT,
  updated_at TEXT
);
