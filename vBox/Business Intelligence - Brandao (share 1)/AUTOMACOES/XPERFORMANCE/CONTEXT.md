# Projeto XPerformance - Web Scraping de Relatórios PDF

## Visão Geral

Sistema automatizado de web scraping desenvolvido para realizar download em massa de relatórios PDF da plataforma XPerformance através do portal hub.xpi.com.br. O projeto utiliza Selenium para automação de navegador e processa aproximadamente 4.000 PDFs mensalmente.

## Objetivos

- Automatizar o download mensal de relatórios XPerformance
- Processar downloads em lotes de 50 PDFs (limitação da plataforma)
- Extrair e organizar PDFs de arquivos ZIP
- Fornecer sistema robusto de checkpoint para retomada em caso de falhas
- Exibir progresso detalhado no terminal durante execução

## Especificações Técnicas

### Portal Alvo
- **URL:** https://hub.xpi.com.br/
- **Tipo:** Portal web com autenticação obrigatória
- **Frequência de uso:** Mensal

### Volume de Dados
- **Total de PDFs:** ~4.000 relatórios por execução
- **Limitação da plataforma:** Downloads em lotes de 50 PDFs
- **Iterações necessárias:** ~80 ciclos de download
- **Tempo estimado:** 90-120 minutos por execução completa

### Padrão de Nomenclatura
- **Arquivo ZIP baixado:** `Lote - XPerformance - Ref.DD.MM.zip`
- **PDFs individuais:** `XPerformance - COD - Ref.DD.MM.pdf`
  - `COD` = Código único do cliente
  - `DD.MM` = Data no formato dia.mês (ex: 15.01)

## Stack Tecnológico

### Linguagem e Framework
- **Python 3.x** - Linguagem principal
- **Selenium WebDriver** - Automação de navegador
- **ChromeDriver** - Driver para Google Chrome

### Bibliotecas Principais
- `selenium` - Automação web
- `webdriver-manager` - Gerenciamento automático de drivers
- `python-dotenv` - Gerenciamento de variáveis de ambiente
- `tqdm` - Barra de progresso visual
- `rich` - Output formatado e colorido no terminal
- `zipfile` (built-in) - Extração de arquivos ZIP
- `json` (built-in) - Manipulação de configurações e checkpoints
- `logging` (built-in) - Sistema de logs

## Arquitetura do Sistema

### Módulos Principais

#### 1. **auth.py** - Autenticação
- Gerencia login no portal hub.xpi.com.br
- Armazena e valida credenciais
- Mantém sessão ativa durante execução
- Tratamento de erros de autenticação

#### 2. **downloader.py** - Download de Lotes
- Controla iterações de download (80 ciclos)
- Gerencia seleção de lotes de 50 PDFs
- Aguarda conclusão de downloads
- Valida integridade dos arquivos ZIP

#### 3. **extractor.py** - Extração de ZIPs
- Descompacta arquivos ZIP automaticamente
- Valida integridade dos PDFs extraídos
- Organiza arquivos por data/cliente
- Opção de manter ou deletar ZIPs após extração

#### 4. **progress.py** - Sistema de Checkpoint
- Salva estado atual do download
- Permite retomada em caso de falha
- Evita re-download de lotes já processados
- Persiste informações em JSON

#### 5. **utils.py** - Funções Auxiliares
- Validação de arquivos
- Formatação de datas
- Funções de logging customizadas
- Helpers para manipulação de paths

#### 6. **scraper.py** - Scraper Principal
- Orquestra todos os módulos
- Controla fluxo de execução
- Gerencia estado do navegador
- Implementa lógica de retry

## Estrutura de Diretórios

```
XPERFORMANCE/
├── src/
│   ├── __init__.py           # Inicialização do pacote
│   ├── scraper.py            # Classe principal do scraper
│   ├── auth.py               # Autenticação no hub.xpi.com.br
│   ├── downloader.py         # Download de lotes (50 PDFs)
│   ├── extractor.py          # Extração de ZIPs
│   ├── progress.py           # Sistema de checkpoint
│   └── utils.py              # Funções auxiliares
├── config/
│   ├── config.json           # Configurações do projeto
│   └── .env.example          # Template para credenciais XPI
├── downloads/
│   ├── zips/                 # Arquivos ZIP baixados
│   └── pdfs/                 # PDFs extraídos organizados
│       ├── 2026-01/          # Organizado por mês
│       ├── 2026-02/
│       └── ...
├── logs/                     # Arquivos de log detalhados
│   ├── scraper_YYYY-MM-DD.log
│   └── errors_YYYY-MM-DD.log
├── checkpoints/              # Estado do progresso
│   └── download_state.json
├── tests/                    # Testes unitários
├── requirements.txt          # Dependências Python
├── README.md                 # Documentação do projeto
├── CONTEXT.md               # Este arquivo
└── main.py                   # Script principal de execução
```

## Fluxo de Execução

### 1. Inicialização
- Carrega configurações do `config.json`
- Lê credenciais do arquivo `.env`
- Verifica checkpoint anterior (se existir)
- Inicializa sistema de logging

### 2. Autenticação
- Abre navegador (Chrome)
- Acessa hub.xpi.com.br
- Realiza login com credenciais
- Valida autenticação bem-sucedida

### 3. Navegação
- Acessa seção de relatórios XPerformance
- Identifica total de relatórios disponíveis
- Calcula número de lotes necessários

### 4. Loop de Download (~80 iterações)
Para cada lote:
- Seleciona próximos 50 PDFs
- Inicia download do arquivo ZIP
- Aguarda conclusão (polling do diretório)
- Valida arquivo baixado
- Salva checkpoint
- Atualiza barra de progresso no terminal
- Aplica delay de segurança (evitar sobrecarga)

### 5. Pós-processamento
- Extrai todos os ZIPs baixados
- Organiza PDFs por data de referência
- Valida integridade dos arquivos
- Remove ZIPs (opcional, configurável)

### 6. Relatório Final
Exibe no terminal:
- Total de PDFs baixados
- Número de lotes processados
- Erros encontrados (se houver)
- Tempo total de execução
- Localização dos arquivos

## Configurações

### config.json
```json
{
  "portal_url": "https://hub.xpi.com.br/",
  "batch_size": 50,
  "download_timeout": 300,
  "retry_attempts": 3,
  "delay_between_batches": 5,
  "headless_mode": false,
  "keep_zip_files": false,
  "organize_by_month": true,
  "download_dir": "downloads/zips",
  "extract_dir": "downloads/pdfs",
  "checkpoint_file": "checkpoints/download_state.json"
}
```

## Sistema de Checkpoint

### Estrutura do download_state.json
```json
{
  "last_execution": "2026-02-19T12:00:00",
  "total_batches": 80,
  "completed_batches": 45,
  "last_batch_processed": 45,
  "downloaded_files": [
    "Lote - XPerformance - Ref.15.01.zip",
    "Lote - XPerformance - Ref.15.02.zip"
  ],
  "status": "in_progress",
  "errors": []
}
```

### Funcionalidades
- Salva estado após cada lote baixado
- Permite retomar execução do último ponto
- Evita re-download de arquivos já processados
- Registra erros para análise posterior

## Tratamento de Erros

### Cenários Cobertos
1. **Timeout de Conexão** - Retry automático com backoff exponencial
2. **Falha de Autenticação** - Notificação clara e parada segura
3. **Download Incompleto** - Validação de tamanho e re-tentativa
4. **ZIP Corrompido** - Log de erro e continuação
5. **Sessão Expirada** - Re-autenticação automática
6. **Limite de Taxa** - Delays adaptativos

### Estratégia de Retry
- Máximo de 3 tentativas por operação
- Backoff exponencial: 5s, 15s, 45s
- Log detalhado de cada tentativa
- Falha definitiva após esgotamento

## Sistema de Logging

### Níveis de Log
- **DEBUG** - Informações detalhadas para debugging
- **INFO** - Progresso normal da execução
- **WARNING** - Situações anormais mas recuperáveis
- **ERROR** - Erros que impedem operação específica
- **CRITICAL** - Falhas que impedem continuação

### Arquivos de Log
- `scraper_YYYY-MM-DD.log` - Log completo da execução
- `errors_YYYY-MM-DD.log` - Apenas erros e warnings
- Rotação automática por data
- Formato: `[TIMESTAMP] [LEVEL] [MODULE] - Message`

## Notificações no Terminal

### Informações Exibidas
- Barra de progresso visual (tqdm)
- Lote atual / Total de lotes
- Quantidade de PDFs baixados
- Tempo decorrido / Tempo estimado restante
- Erros e avisos em tempo real
- Resumo final colorido (rich)

### Exemplo de Output
```
[12:00:00] Iniciando download de relatórios XPerformance
[12:00:05] Autenticação bem-sucedida
[12:00:10] Total de lotes a processar: 80

Downloading: |████████░░░░░░░░░░░░| 45/80 [56%] ETA: 45min
Lote 45/80 | PDFs: 2,250/4,000 | Tempo: 67min

[13:07:15] ✓ Download concluído com sucesso!
Total: 4,000 PDFs | Tempo: 107min | Erros: 0
```

## Segurança e Boas Práticas

### Credenciais
- Nunca commitar arquivo `.env` no repositório
- Usar `.gitignore` para arquivos sensíveis
- Validar credenciais antes de iniciar scraping
- Opção de criptografia para armazenamento local

### Web Scraping Ético
- Respeitar robots.txt (se aplicável)
- Implementar delays entre requisições
- User-agent apropriado
- Não sobrecarregar servidor
- Uso apenas para fins autorizados

### Gerenciamento de Recursos
- Fechar navegador adequadamente
- Liberar memória após processamento
- Limpar arquivos temporários
- Monitorar uso de disco

## Desafios Técnicos e Soluções

### 1. Download em Lotes
**Desafio:** Plataforma limita downloads a 50 PDFs por vez  
**Solução:** Loop automatizado com 80 iterações e checkpoint

### 2. Gerenciamento de ZIPs
**Desafio:** Múltiplos arquivos ZIP para processar  
**Solução:** Extração automática e organização por data

### 3. Resiliência
**Desafio:** Execução longa pode falhar  
**Solução:** Sistema de checkpoint para retomar do ponto de parada

### 4. Performance
**Desafio:** 4.000 arquivos para processar  
**Solução:** Otimização de delays e possível paralelização de extração

## Melhorias Futuras

### Curto Prazo
- [ ] Modo headless configurável
- [ ] Notificações por email ao concluir
- [ ] Dashboard web para monitoramento
- [ ] Testes unitários completos

### Médio Prazo
- [ ] Suporte a múltiplos usuários/contas
- [ ] Agendamento automático (cron/task scheduler)
- [ ] API REST para controle remoto
- [ ] Integração com banco de dados

### Longo Prazo
- [ ] Interface gráfica (GUI)
- [ ] Análise automática de PDFs
- [ ] Machine learning para detecção de anomalias
- [ ] Containerização (Docker)

## Manutenção

### Atualizações Regulares
- Verificar compatibilidade com mudanças no portal
- Atualizar seletores CSS/XPath se necessário
- Manter dependências atualizadas
- Revisar logs mensalmente

### Monitoramento
- Verificar taxa de sucesso dos downloads
- Analisar logs de erro
- Validar integridade dos PDFs
- Monitorar tempo de execução

## Contato e Suporte

Para questões técnicas ou melhorias, consulte a documentação no README.md ou os logs de execução.

---

**Última atualização:** 19/02/2026  
**Versão:** 1.0.0  
**Status:** Em desenvolvimento
