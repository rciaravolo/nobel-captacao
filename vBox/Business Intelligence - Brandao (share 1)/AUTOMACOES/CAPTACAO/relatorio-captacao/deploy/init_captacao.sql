-- ============================================================
-- init_captacao.sql  — Schema captacao no Nobel PostgreSQL
-- Executar uma vez na VPS:
--   docker exec -i postgres_nobel_v2 psql -U nobel_adm -d nobel_db < init_captacao.sql
-- ============================================================

CREATE SCHEMA IF NOT EXISTS captacao;

CREATE TABLE IF NOT EXISTS captacao.tb_cap (
    id              SERIAL PRIMARY KEY,
    codigo_real     TEXT,
    captacao        NUMERIC,
    nucleo          TEXT,
    assessor        TEXT,
    data_transacao  TIMESTAMP,
    status          TEXT,
    atualizado_em   TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS captacao.tb_positivador (
    id              SERIAL PRIMARY KEY,
    assessor        TEXT,
    nucleo          TEXT,
    net_em_m        NUMERIC,
    status          TEXT,
    atualizado_em   TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS captacao.metadata (
    chave       TEXT PRIMARY KEY,
    valor       TEXT,
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

GRANT ALL ON SCHEMA captacao TO app_user;
GRANT ALL ON ALL TABLES IN SCHEMA captacao TO app_user;
GRANT ALL ON ALL SEQUENCES IN SCHEMA captacao TO app_user;

-- Default do future GRANT para tabelas criadas depois
ALTER DEFAULT PRIVILEGES IN SCHEMA captacao
    GRANT ALL ON TABLES TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA captacao
    GRANT ALL ON SEQUENCES TO app_user;
