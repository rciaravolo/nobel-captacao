# Como fazer o relatório rodar mesmo com o computador desligado

## O problema

O **Agendador de Tarefas do Windows** não consegue executar nada quando o computador está desligado. Para resolver isso de forma definitiva, usamos o **GitHub Actions** — um serviço gratuito da GitHub que roda código na nuvem automaticamente no horário certo.

**Como funciona a solução:**
1. Um script no seu computador copia o Excel para o GitHub às **16:45** (antes das 17h)
2. O **GitHub Actions** roda o relatório às **17:00** automaticamente na nuvem
3. O e-mail é enviado via SMTP (sem precisar do Outlook aberto)

---

## Passo 1 — Criar repositório privado no GitHub

1. Acesse [github.com](https://github.com) e faça login (ou crie uma conta gratuita)
2. Clique em **New repository**
3. Nome: `relatorio-captacao-nobel` (ou outro de sua preferência)
4. Marque **Private** (repositório privado — seus dados ficam protegidos)
5. Clique em **Create repository**
6. Copie a URL do repositório (ex: `https://github.com/SEU_USUARIO/relatorio-captacao-nobel.git`)

---

## Passo 2 — Conectar a pasta ao GitHub

Abra o **Prompt de Comando** como Administrador e execute:

```cmd
cd "C:\Users\Usuário\vBox\Business Intelligence - Brandao (share 1)\AUTOMACOES\CAPTACAO\relatorio-captacao"

git remote add origin https://github.com/SEU_USUARIO/relatorio-captacao-nobel.git
git branch -M main
git push -u origin main
```

> Se pedir usuário/senha, use seu login do GitHub.
> Recomendado: configure um **Personal Access Token** no GitHub (Settings > Developer settings > Tokens).

---

## Passo 3 — Criar pasta `data/` e adicionar ao .gitignore correto

```cmd
mkdir data
echo # pasta de dados > data\.gitkeep
```

Adicione ao `.gitignore` (para não versionar arquivos grandes acidentalmente):
```
# NÃO ignorar a pasta data (necessária para o GitHub Actions)
!data/
```

---

## Passo 4 — Configurar credenciais de e-mail SMTP no GitHub

Você vai precisar de uma senha de app para enviar e-mails sem usar o Outlook.

### Office 365 (Nobel Capital)
1. Acesse [myaccount.microsoft.com](https://myaccount.microsoft.com)
2. Vá em **Segurança** > **Verificação em duas etapas**
3. Crie uma **Senha de aplicativo** específica para este relatório

### Configurar os Secrets no GitHub
1. No repositório do GitHub, vá em **Settings > Secrets and variables > Actions**
2. Clique em **New repository secret** e adicione um a um:

| Nome do Secret | Valor |
|----------------|-------|
| `SMTP_HOST` | `smtp.office365.com` |
| `SMTP_PORT` | `587` |
| `SMTP_USER` | `seu.email@nobelcapital.com.br` |
| `SMTP_PASSWORD` | *(a senha de app criada acima)* |
| `SMTP_FROM` | `seu.email@nobelcapital.com.br` |

---

## Passo 5 — Agendar o push do Excel às 16:45

O arquivo `push_excel_github.bat` copia o Excel para o GitHub antes das 17h.

### Agendar no Windows:
1. Abra o **Agendador de Tarefas** (`taskschd.msc`)
2. Clique em **Criar Tarefa Básica**
3. Nome: `Nobel - Push Excel GitHub`
4. Disparador: **Diariamente** às **16:45**, Seg a Sex (desmarque Sáb/Dom)
5. Ação: **Iniciar um programa**
   - Programa: `C:\Users\Usuário\vBox\Business Intelligence - Brandao (share 1)\AUTOMACOES\CAPTACAO\relatorio-captacao\push_excel_github.bat`
6. Marque **Abrir caixa de diálogo avançada...**
7. Na aba **Condições**: desmarque "Iniciar a tarefa somente se o computador estiver conectado à rede AC"
8. Na aba **Configurações**: marque "Executar tarefa o mais cedo possível se uma execução agendada for perdida"

> **Nota:** Este script só precisa rodar quando o computador estiver ligado para atualizar os dados. O relatório em si (17h) vai rodar no GitHub Actions independentemente.

---

## Passo 6 — Testar o workflow manualmente

1. Acesse o repositório no GitHub
2. Clique em **Actions** > **Relatório Captação Diário - Nobel Capital**
3. Clique em **Run workflow** > **Run workflow**
4. Aguarde ~30 segundos e verifique se o e-mail chegou

---

## Resumo do fluxo final

```
16:45 (seu computador, se ligado)
  └─ push_excel_github.bat
       ├─ Copia Excel atualizado → data/BASES_ONE_PAGE.xlsx
       └─ git push → envia para o GitHub

17:00 (GitHub Actions — nuvem — sempre roda)
  └─ relatorio_captacao.yml
       ├─ Lê Excel da pasta data/
       ├─ Gera relatório HTML
       └─ Envia e-mail via SMTP para timenobel@nobelcapital.com.br
```

---

## Solução de problemas

| Sintoma | Causa provável | Solução |
|---------|----------------|---------|
| E-mail não chegou | Credenciais SMTP erradas | Verifique os Secrets no GitHub |
| "Arquivo Excel não encontrado" | Excel não foi enviado para o GitHub | Execute `push_excel_github.bat` manualmente |
| GitHub Actions não aparece | Workflow não foi enviado | Execute `git push` e verifique a aba Actions |
| Push falha às 16:45 | Computador estava desligado | Normal — o Actions usará o Excel do dia anterior |

---

## Agendamento atual (Windows Task Scheduler — backup local)

O agendamento no Windows foi mantido e corrigido. Ele continua rodando como backup quando o computador está ligado:

- **Tarefa:** `Nobel_Relatorio_Captacao`
- **Horário:** 17:00, Segunda a Sexta
- **Comportamento:** Se o PC estava desligado às 17h, executa ao religar

Para recriar a tarefa caso necessário:
```cmd
:: Executar como Administrador
powershell -ExecutionPolicy Bypass -File reconfigurar_tarefa.ps1
```
