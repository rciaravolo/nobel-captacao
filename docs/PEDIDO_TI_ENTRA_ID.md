# Pedido para TI — Registrar App no Entra ID para envio automatizado de email

**Contexto:** o robô do Relatório de Captação Diário da Nobel Capital roda no GitHub Actions e envia email às 17h para o time. O envio via SMTP básico foi bloqueado pela política padrão de segurança do M365 (SmtpClientAuthentication desabilitado no tenant), então precisamos migrar para **Microsoft Graph API** — método recomendado pela Microsoft, mais seguro (sem senha, apenas certificado/secret).

**O que preciso da TI:** registrar uma aplicação no Entra ID com permissão de envio de email restrita a uma única mailbox (a do bot). Segue passo a passo.

---

## Passo 1 — Registrar a aplicação

1. Portal do Azure → **Microsoft Entra ID** → **App registrations** → **New registration**
2. Preencher:
   - **Name:** `Nobel Captacao Bot`
   - **Supported account types:** *Accounts in this organizational directory only (Single tenant)*
   - **Redirect URI:** deixar em branco
3. Clicar **Register**
4. Na tela seguinte, **copiar e me enviar**:
   - **Application (client) ID** → vira `GRAPH_CLIENT_ID`
   - **Directory (tenant) ID** → vira `GRAPH_TENANT_ID`

---

## Passo 2 — Criar client secret

1. Na app registrada → **Certificates & secrets** → **Client secrets** → **New client secret**
2. Preencher:
   - **Description:** `github-actions-relatorio-captacao`
   - **Expires:** 24 meses (ou o máximo permitido pela política interna)
3. Clicar **Add**
4. **Copiar imediatamente o campo `Value`** (só aparece uma vez, depois some) → vira `GRAPH_CLIENT_SECRET`

---

## Passo 3 — Dar permissão de envio de email

1. Na app → **API permissions** → **Add a permission**
2. Escolher **Microsoft Graph** → **Application permissions** (não Delegated)
3. Procurar **`Mail.Send`** → marcar → **Add permissions**
4. De volta na lista de permissões, clicar **Grant admin consent for [tenant]** (botão azul no topo)
   - ⚠️ Este passo requer **admin consent** — só um Global Admin (ou Application Admin) consegue clicar aqui

---

## Passo 4 (recomendado — segurança) — Restringir a app a UMA mailbox

Sem esta restrição, a app teoricamente pode enviar email como QUALQUER usuário do tenant. Para restringir à mailbox do bot apenas, rodar no **Exchange Online PowerShell**:

```powershell
# 1. Conectar
Connect-ExchangeOnline

# 2. Criar um mail-enabled security group com a mailbox do bot
New-DistributionGroup -Name "GraphAPI-BotSenders" -Type "Security" `
    -Members "bi@nobelcapital.com.br"

# 3. Aplicar a policy — só permite enviar como membros do grupo
New-ApplicationAccessPolicy `
    -AppId "<COLAR_AQUI_O_CLIENT_ID_DO_PASSO_1>" `
    -PolicyScopeGroupId "GraphAPI-BotSenders@nobelcapital.com.br" `
    -AccessRight RestrictAccess `
    -Description "Restringe app Nobel Captacao Bot a enviar apenas pela mailbox do BI"

# 4. Testar (opcional)
Test-ApplicationAccessPolicy `
    -Identity "bi@nobelcapital.com.br" `
    -AppId "<CLIENT_ID>"
# Deve retornar: AccessCheckResult = Granted
```

> Se essa restrição não for feita agora, a integração ainda funciona — só fica com escopo mais amplo do que o necessário.

---

## Passo 5 — Retornar para mim

Preciso de 4 informações para configurar os secrets do GitHub Actions:

| Chave | Onde obter |
|-------|------------|
| `GRAPH_CLIENT_ID` | Passo 1 — Application (client) ID |
| `GRAPH_TENANT_ID` | Passo 1 — Directory (tenant) ID |
| `GRAPH_CLIENT_SECRET` | Passo 2 — o campo `Value` do secret |
| `GRAPH_FROM` (mailbox remetente) | ex: `bi@nobelcapital.com.br` |

**Como enviar com segurança:** por favor, **NÃO** mandar por email/Teams em texto plano. Preferência: cofre de senhas corporativo (1Password / Bitwarden / KeePass compartilhado) ou entrega presencial. Se não houver, mandar por canal com E2E (WhatsApp com mensagem que se apaga, Signal).

---

## Referências oficiais Microsoft

- Registrar app: https://learn.microsoft.com/en-us/entra/identity-platform/quickstart-register-app
- Enviar email via Graph: https://learn.microsoft.com/en-us/graph/api/user-sendmail
- ApplicationAccessPolicy: https://learn.microsoft.com/en-us/graph/auth-limit-mailbox-access

---

**Prazo desejado:** o quanto antes — enquanto o registro não sai, o relatório continua sendo enviado pelo PC local via Outlook (Task Scheduler), então não há urgência crítica, mas a migração destrava o robô rodar 100% na nuvem, sem depender do PC estar ligado.

Obrigado!
