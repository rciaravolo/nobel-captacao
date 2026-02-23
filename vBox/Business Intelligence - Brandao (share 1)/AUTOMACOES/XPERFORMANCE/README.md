# XPerformance PDF Scraper

Sistema automatizado de web scraping para download em massa de relatórios PDF da plataforma XPerformance através do portal hub.xpi.com.br.

## 📋 Visão Geral

Este projeto automatiza o download mensal de aproximadamente 4.000 relatórios PDF do portal XPI Hub, processando downloads em lotes de 50 PDFs por vez (limitação da plataforma), totalizando cerca de 80 iterações por execução.

## ✨ Funcionalidades

- ✅ Autenticação automática no portal hub.xpi.com.br
- ✅ Download em lotes de 50 PDFs (80+ iterações)
- ✅ Extração automática de arquivos ZIP
- ✅ Organização de PDFs por mês
- ✅ Sistema de checkpoint para retomar downloads
- ✅ Barra de progresso visual no terminal
- ✅ Logging detalhado de todas as operações
- ✅ Tratamento robusto de erros com retry automático
- ✅ Notificações formatadas no terminal

## 🛠️ Tecnologias

- **Python 3.x**
- **Selenium WebDriver** - Automação de navegador
- **ChromeDriver** - Driver do Google Chrome
- **tqdm** - Barra de progresso
- **rich** - Output formatado no terminal
- **python-dotenv** - Gerenciamento de variáveis de ambiente

## 📦 Instalação

### 1. Clone ou baixe o projeto

```bash
cd XPERFORMANCE
```

### 2. Crie um ambiente virtual (recomendado)

```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configuração (Opcional)

O sistema não requer configuração de credenciais. O login é feito **manualmente pelo usuário** no navegador que será aberto automaticamente.

## 🚀 Uso

### Execução Básica

```bash
python main.py
```

### Primeira Execução

Na primeira execução, o scraper irá:
1. Abrir o navegador Chrome no portal XPI Hub
2. **Aguardar 5 minutos para você fazer login manualmente**
3. Detectar automaticamente quando o login for concluído
4. Navegar até a seção de relatórios XPerformance
5. Baixar todos os lotes (80 iterações)
6. Extrair os ZIPs automaticamente
7. Organizar PDFs por mês
8. Exibir resumo final

**⚠️ IMPORTANTE**: Você tem **5 minutos** para fazer login no navegador. Se não fizer login neste tempo, o sistema será encerrado com a mensagem "Usuário não efetuou o login, recomeçar automação."

### Retomando Execução

Se a execução for interrompida, basta executar novamente:
```bash
python main.py
```

O sistema automaticamente retomará do último lote processado usando o checkpoint salvo.

## ⚙️ Configuração

Edite `config/config.json` para personalizar:

```json
{
  "portal_url": "https://hub.xpi.com.br/",
  "batch_size": 50,
  "download_timeout": 300,
  "retry_attempts": 3,
  "delay_between_batches": 5,
  "headless_mode": false,
  "keep_zip_files": false,
  "organize_by_month": true
}
```

### Parâmetros Principais

- **batch_size**: Tamanho do lote (padrão: 50)
- **download_timeout**: Timeout para download em segundos
- **retry_attempts**: Número de tentativas em caso de falha
- **delay_between_batches**: Delay entre lotes em segundos
- **headless_mode**: Executar navegador em modo invisível
- **keep_zip_files**: Manter arquivos ZIP após extração
- **organize_by_month**: Organizar PDFs por mês

## 📁 Estrutura de Diretórios

```
XPERFORMANCE/
├── src/                      # Código fonte
│   ├── auth.py              # Autenticação
│   ├── downloader.py        # Download de lotes
│   ├── extractor.py         # Extração de ZIPs
│   ├── progress.py          # Sistema de checkpoint
│   ├── scraper.py           # Scraper principal
│   └── utils.py             # Funções auxiliares
├── config/                   # Configurações
│   ├── config.json          # Configurações do projeto
│   ├── .env                 # Credenciais (não commitar!)
│   └── .env.example         # Template de credenciais
├── downloads/
│   ├── zips/                # ZIPs baixados
│   └── pdfs/                # PDFs extraídos
│       ├── 2026-01/         # Organizados por mês
│       └── 2026-02/
├── logs/                     # Arquivos de log
├── checkpoints/              # Estado do progresso
├── main.py                   # Script principal
├── requirements.txt          # Dependências
├── CONTEXT.md               # Contexto detalhado
└── README.md                # Este arquivo
```

## 📊 Exemplo de Saída

```
[12:00:00] Iniciando download de relatórios XPerformance
[12:00:02] Acessando portal: https://hub.xpi.com.br/
[12:00:05] ============================================================
[12:00:05] AGUARDANDO LOGIN MANUAL DO USUÁRIO
[12:00:05] Você tem 5 minutos para fazer login no navegador
[12:00:05] ============================================================
[12:00:35] Tempo restante: 4min 25s
[12:01:05] Tempo restante: 3min 55s
[12:01:23] ============================================================
[12:01:23] ✓ Login detectado! Autenticação bem-sucedida!
[12:01:23] ============================================================
[12:01:25] Total de lotes a processar: 80

Downloading: |████████████░░░░░░░░| 45/80 [56%] 00:45<00:35, 1.2s/lote

[13:07:15] Iniciando pós-processamento...
[13:07:45] ✓ Total de 4,000 PDFs extraídos de 80 ZIPs

╭─────────────── Resumo da Execução ───────────────╮
│ Métrica              │ Valor                     │
├──────────────────────┼───────────────────────────┤
│ Lotes Processados    │ 80/80                     │
│ Progresso            │ 100.0%                    │
│ ZIPs Baixados        │ 80                        │
│ PDFs Extraídos       │ 4,000                     │
│ Tamanho Total        │ 1,234.56 MB               │
│ Erros                │ 0                         │
│ Tempo Total          │ 1h 7min 45s               │
│ Status               │ COMPLETED                 │
╰──────────────────────────────────────────────────╯

✓ Execução concluída com sucesso!
```

## 🔧 Solução de Problemas

### Timeout de Login (5 minutos)

- Se você não fizer login em 5 minutos, o sistema será encerrado
- Execute novamente: `python main.py`
- Certifique-se de que suas credenciais estão corretas
- Verifique se sua conta tem acesso ao portal

### Download Não Inicia

- Verifique sua conexão com a internet
- Aumente o `download_timeout` em `config.json`
- Execute com `headless_mode: false` para visualizar o navegador

### ChromeDriver Não Encontrado

- O `webdriver-manager` instala automaticamente
- Se houver problemas, baixe manualmente de: https://chromedriver.chromium.org/

### Sessão Expira Durante Execução

- O sistema re-autentica automaticamente
- Verifique os logs em `logs/` para detalhes

## 📝 Logs

Logs são salvos em `logs/` com os seguintes arquivos:

- `scraper_YYYY-MM-DD.log` - Log completo da execução
- `errors_YYYY-MM-DD.log` - Apenas erros e warnings

## 🔒 Segurança

- Login manual garante que suas credenciais nunca sejam armazenadas no código
- O sistema não salva ou registra suas credenciais
- Sessão é mantida apenas durante a execução

## 🤝 Contribuindo

Para melhorias ou correções:

1. Documente mudanças no código
2. Teste completamente antes de usar em produção
3. Atualize este README se necessário

## 📄 Licença

Uso interno - Business Intelligence Brandao

## 📞 Suporte

Para questões técnicas, consulte:
- `CONTEXT.md` - Documentação técnica detalhada
- `logs/` - Arquivos de log para debugging
- Código fonte em `src/` - Bem documentado

## 🎯 Roadmap

- [ ] Interface gráfica (GUI)
- [ ] Notificações por email
- [ ] Dashboard web de monitoramento
- [ ] Suporte a múltiplas contas
- [ ] Agendamento automático (cron)
- [ ] API REST para controle remoto

---

**Versão:** 1.0.0  
**Última Atualização:** 19/02/2026  
**Desenvolvido por:** Business Intelligence - Brandao
