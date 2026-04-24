# Sistema de Reembolsos Nobel Capital

Plataforma web para submissão e aprovação de pedidos de reembolso.

## Stack

| Camada | Tecnologia |
|--------|-----------|
| Frontend | Cloudflare Pages (HTML/CSS/JS vanilla) |
| Backend API | Cloudflare Worker + Hono.js (TypeScript) |
| Banco de dados | Cloudflare D1 (SQLite serverless) |
| Armazenamento | Cloudflare R2 (anexos PDF/imagens) |
| Auth | JWT (HMAC-SHA256) + PBKDF2 (senhas) |
| Email | Resend API |

## Estrutura

```
REEMBOLSOS/
├── api/                    # Worker (Hono.js)
│   ├── src/
│   │   ├── index.ts        # Router principal
│   │   ├── middleware/auth.ts  # JWT + hash de senha
│   │   └── routes/
│   │       ├── auth.ts     # /api/auth/login, /me, /setup
│   │       ├── reimbursements.ts  # CRUD + R2 upload + email
│   │       └── users.ts    # Gestão de usuários
│   └── wrangler.toml
├── frontend/               # Cloudflare Pages
│   ├── login.html
│   ├── form.html           # Assessor: nova solicitação
│   ├── minhas-solicitacoes.html
│   ├── admin.html          # Financeiro: pendentes
│   ├── admin-historico.html
│   ├── admin-usuarios.html
│   ├── js/
│   │   ├── config.js       # API_BASE_URL
│   │   ├── auth.js         # helpers compartilhados
│   │   ├── form.js
│   │   ├── solicitacoes.js
│   │   └── admin.js
│   └── css/style.css
├── migrations/
│   └── 001_initial.sql
└── scripts/
    ├── hash-password.js    # Gera hash PBKDF2 para seed manual
    └── seed.js             # Cria primeiro usuário via API
```

## Setup inicial (passo a passo)

### 1. Pré-requisitos

```bash
npm install -g wrangler
wrangler login
```

### 2. Criar recursos Cloudflare

```bash
# Banco D1
wrangler d1 create reembolsos
# Copie o database_id gerado e cole em api/wrangler.toml

# Bucket R2
wrangler r2 bucket create reembolsos-anexos
```

### 3. Rodar migration

```bash
cd api
npm install

# Local (preview)
npm run db:migrate

# Produção
npm run db:migrate:prod
```

### 4. Configurar secrets

```bash
wrangler secret put JWT_SECRET       # string aleatória longa (ex: openssl rand -hex 32)
wrangler secret put RESEND_API_KEY   # chave da Resend API (resend.com)
wrangler secret put FINANCE_EMAIL    # email do financeiro para notificações
```

Editar `api/wrangler.toml`:
```toml
[vars]
FRONTEND_URL = "https://reembolsos.pages.dev"  # URL do Pages após deploy
```

### 5. Deploy da API (Worker)

```bash
cd api
npm run deploy
# Anote a URL: https://reembolsos-api.SEU_SUBDOMINIO.workers.dev
```

### 6. Configurar URL da API no frontend

Editar `frontend/js/config.js`:
```js
return 'https://reembolsos-api.SEU_SUBDOMINIO.workers.dev';
```

### 7. Deploy do frontend (Pages)

```bash
# Via Cloudflare Dashboard > Pages > Create project > upload pasta frontend/
# OU via CLI:
wrangler pages deploy frontend --project-name=reembolsos
```

### 8. Criar primeiro usuário (financeiro)

```bash
node scripts/seed.js https://reembolsos-api.SEU_SUBDOMINIO.workers.dev
```

Isso chama `POST /api/auth/setup` (só funciona com banco vazio).

Após o setup, crie os assessores em `admin-usuarios.html`.

## Endpoints da API

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| POST | `/api/auth/login` | — | Login |
| GET | `/api/auth/me` | JWT | Dados do usuário |
| POST | `/api/auth/setup` | — | Cria 1º admin (banco vazio) |
| GET | `/api/reimbursements` | JWT | Lista pedidos |
| POST | `/api/reimbursements` | JWT | Cria pedido (multipart) |
| GET | `/api/reimbursements/:id` | JWT | Detalhe |
| PATCH | `/api/reimbursements/:id/review` | JWT (financeiro) | Aprovar/recusar |
| GET | `/api/reimbursements/:id/attachment` | JWT | Serve arquivo do R2 |
| GET | `/api/users` | JWT (financeiro) | Lista usuários |
| POST | `/api/users` | JWT (financeiro) | Cria usuário |
| PATCH | `/api/users/:id/toggle` | JWT (financeiro) | Ativa/desativa |
| PATCH | `/api/users/:id/password` | JWT (financeiro) | Redefine senha |

## Adicionar usuário manualmente via SQL

```bash
# 1. Gera o hash da senha
node scripts/hash-password.js "SenhaDoAssessor@123"

# 2. Insere no D1 (produção)
wrangler d1 execute reembolsos --remote --command="
  INSERT INTO users (name, email, password_hash, role, team)
  VALUES ('João Silva', 'joao@nobelcapital.com.br', 'pbkdf2:100000:SALT:HASH', 'assessor', 'PRIVATE');
"
```

## Desenvolvimento local

```bash
# Terminal 1: Worker com D1 e R2 locais
cd api && npm run dev   # http://localhost:8787

# Terminal 2: servir frontend
cd frontend && npx serve .  # ou qualquer servidor estático
# Editar js/config.js para apontar para http://localhost:8787
```

## Variáveis de ambiente obrigatórias

| Var | Onde definir | Descrição |
|-----|-------------|-----------|
| `JWT_SECRET` | `wrangler secret` | Chave HMAC para tokens JWT |
| `RESEND_API_KEY` | `wrangler secret` | API key da Resend (email) |
| `FINANCE_EMAIL` | `wrangler secret` | Email do financeiro p/ notificações |
| `FRONTEND_URL` | `wrangler.toml [vars]` | URL base do Pages |

## Hash de senhas

Algoritmo: **PBKDF2-HMAC-SHA256**, 100.000 iterações, salt de 16 bytes, output de 32 bytes.
Formato: `pbkdf2:100000:<salt_hex>:<hash_hex>`

O Worker usa Web Crypto API nativa. O script `hash-password.js` usa `crypto.pbkdf2` do Node.js — produzem hashes idênticos.

## Email (Resend)

- Free tier: 100 emails/dia
- Domínio remetente: `reembolsos@nobelcapital.com.br` (verificar no Resend dashboard)
- Emails enviados de forma assíncrona via `c.executionCtx.waitUntil()`
- Se `RESEND_API_KEY` não estiver definida, emails são silenciosamente ignorados
