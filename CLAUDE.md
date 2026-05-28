# CLAUDE.md — Relatório de Captação Nobel Capital

## O que este projeto faz

Gera e envia **automaticamente por e-mail** o relatório diário de captação e custódia da Nobel Capital. O e-mail é enviado às 17h para `timenobel@nobelcapital.com.br` com:

- Resumo de captação do dia (escritório + equipes)
- Rankings de times e assessores (positivos/negativos)
- Gráfico de captação diária do mês
- **Seção de Movimentação de Base**: Ativação, Habilitação e Evasão de contas por faixa patrimonial
- Rankings e resumo de custódia

## Repositório GitHub

`rciaravolo/nobel-captacao` (privado)

## Arquitetura — Pipeline (main.py)

```
1️⃣  ETL Captação       → etl_bases.py   (lê BASES ONE PAGE + ONE PAGE ATUAL_V2)
2️⃣  Resumo escritório  → consolidacao.py
3️⃣  Rankings captação  → ranking_generator.py
4️⃣  Gráfico captação   → chart_generator.py  (barras diárias do mês)
5️⃣  Contas (mov. base) → contas_etl.py  (ativacao/evasao/habilitacao/positivador)
    └─ Gráfico contas   → chart_generator.gerar_grafico_contas()
6️⃣  ETL Custódia       → etl_bases.py   (TB_POSITIVADOR)
7️⃣  Envio e-mail       → email_sender.py (Outlook ou SMTP)
```

## Arquivos principais

| Arquivo | Função |
|---------|--------|
| `main.py` | Orquestrador do pipeline |
| `config.py` | Todas as configurações centralizadas |
| `etl_bases.py` | Leitura e merge das bases Excel |
| `consolidacao.py` | Cálculo de resumos |
| `ranking_generator.py` | Geração de rankings |
| `chart_generator.py` | Gráficos (captação diária e movimentação de contas) |
| `email_sender.py` | Montagem do HTML e envio do e-mail |
| `contas_etl.py` | ETL de Ativação / Habilitação / Evasão de contas |
| `cloudflare_d1.py` | Cliente da API Cloudflare D1 |
| `push_cloudflare_d1.py` | Push local → Cloudflare D1 |
| `push_para_postgres.py` | Push local → PostgreSQL VPS |
| `assessor.json` | Lista de assessores ativos por equipe |
| `consolidacao.py` | Cálculo de totais e resumos |

## Caminhos críticos (config.py)

```python
CAMINHO_BASE = r'C:\Users\Usuário\vBox\ONE PAGE'
# Base 1: arquivo *BASES ONE PAGE*.xlsx    sheet=TB_CAP
# Base 2: arquivo ONE PAGE - ATUAL_V2.xlsm sheet=CAPTAÇÃO ATUAL, HISTÓRICO CAP, TB_POSITIVADOR
```

### Movimentação de Contas (contas_etl.py)

```python
_CONTAS_DIR = r'C:\Users\Usuário\vBox\ONE PAGE\TESTE'
```

> ⚠️ **ATENÇÃO — NÃO ALTERAR ESTE CAMINHO:** O diretório correto é `ONE PAGE\TESTE`.
> A pasta `3. DIARIO DE BASE` **não deve ser usada** aqui — houve tentativas de "correção" que quebraram o pipeline.
> Arquivos necessários dentro de `TESTE\`: `ativacao.xlsx`, `evasao.xlsx`, `habilitacao.xlsx`, `Relatório Positivador.xlsx`

### Assessores

```python
ARQUIVO_ASSESSORES = r'...\relatorio-captacao\assessor.json'
```

> O `assessor.json` fica **dentro** do repositório (pasta `relatorio-captacao`), não na raiz de CAPTACAO.

## Modos de execução

### Fonte de dados (`FONTE_DADOS`)
| Valor | Quando usar |
|-------|-------------|
| `excel` | Local — lê diretamente do vBox (padrão) |
| `d1` | GitHub Actions — lê do Cloudflare D1 |
| `postgres` | Container Docker / VPS — lê do PostgreSQL |

### Modo e-mail (`EMAIL_MODO`)
| Valor | Quando usar |
|-------|-------------|
| `outlook` | Local/Windows com Outlook aberto (padrão) |
| `smtp` | Nuvem / GitHub Actions (sem Outlook) |

## Como rodar localmente

```bat
:: Opção 1 — bat simples
rodar_relatorio.bat

:: Opção 2 — bat com log
executar_relatorio.bat

:: Opção 3 — direto
python main.py
```

## Automação em nuvem (GitHub Actions)

**Fluxo completo:**
```
16:45 → push_excel_github.bat  (PC envia Excel para o GitHub, se ligado)
              ↓ (alternativa: push_para_cloudflare.bat envia p/ Cloudflare D1)
17:00 → GitHub Actions roda main.py com FONTE_DADOS=d1
              └─ Envia e-mail via SMTP
```

**Workflow:** `.github/workflows/relatorio_captacao.yml`
- Agenda: `cron: '0 20 * * 1-5'` (20h UTC = 17h BRT)
- Secrets necessários: `CF_ACCOUNT_ID`, `CF_API_KEY`, `CF_API_EMAIL`, `CF_D1_DATABASE_ID`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`

## Scripts de deploy

```
deploy/
├── deploy_vps.sh       # Script de setup do servidor VPS
├── crontab             # Crontab para execução no VPS
└── init_captacao.sql   # Schema inicial do PostgreSQL
```

```
Dockerfile              # Container para rodar o relatório
push_para_postgres.bat  # Envia dados locais → PostgreSQL VPS (porta 5433)
push_para_cloudflare.bat # Envia dados locais → Cloudflare D1
```

## Equipes ativas

`PRIVATE`, `BRAVO`, `RIO PRETO`, `SMART-GLOBAL`, `SMART-UNIQUE`, `SMART-ALFA`

Limite custódia: `>=50MM` (grandes) vs `<50MM` (pequenos)

## Variáveis de ambiente relevantes

```env
CAMINHO_BASE         # Raiz do vBox ONE PAGE (default local)
CONTAS_DIR           # Diretório com planilhas de contas (default: ONE PAGE\TESTE) ← NÃO MUDAR
FONTE_DADOS          # excel | d1 | postgres
EMAIL_MODO           # outlook | smtp
EMAIL_DESTINATARIO   # Override do destinatário (modo teste)
ARQUIVO_ASSESSORES   # Path do assessor.json
PG_HOST / PG_PORT / PG_DB / PG_USER / PG_PASSWORD / PG_SSLMODE
CF_ACCOUNT_ID / CF_API_KEY / CF_API_EMAIL / CF_D1_DATABASE_ID
SMTP_HOST / SMTP_PORT / SMTP_USER / SMTP_PASSWORD / SMTP_FROM
```

## Convenções de desenvolvimento

- Sempre criar branch + PR antes de mergear no master
- Nunca commitar direto no master
- Scripts de diagnóstico/verificação pontual ficam em `_arquivo_morto/diagnostico/`
- Scripts de setup do agendador Windows ficam em `_arquivo_morto/setup_agendador/`
- `preview_*.html` são gerados e ignorados pelo .gitignore (não commitar)

## Histórico de decisões relevantes

| Decisão | Motivo |
|---------|--------|
| `_CONTAS_DIR` → `ONE PAGE\TESTE` | Esta é a pasta correta com os arquivos atualizados de contas |
| `assessor.json` dentro do repo (`relatorio-captacao/`) | Antes apontava para pasta pai incorreta |
| GitHub Actions com FONTE_DADOS=d1 | Não depende de o PC estar ligado às 17h |
| SMTP_PORT tolerante a string vazia | Secrets do GitHub Actions podem retornar vazio |
