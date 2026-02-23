# 📦 Guia de Instalação - XPerformance Scraper

## Pré-requisitos

### Software Necessário
- ✅ **Python 3.8+** - [Download](https://www.python.org/downloads/)
- ✅ **Google Chrome** - Navegador (instalado no sistema)
- ✅ **Git** (opcional) - Para controle de versão

### Verificar Instalações

```bash
# Verificar Python
python --version

# Verificar pip
pip --version

# Verificar Chrome
# Abra o Chrome e vá em: chrome://version/
```

## 🚀 Instalação Passo a Passo

### Passo 1: Preparar Ambiente

```bash
# Navegar até o diretório do projeto
cd "c:\Users\Usuário\vBox\Business Intelligence - Brandao\AUTOMACOES\XPERFORMANCE"

# Criar ambiente virtual (RECOMENDADO)
python -m venv venv

# Ativar ambiente virtual
venv\Scripts\activate
```

### Passo 2: Instalar Dependências

```bash
# Instalar todas as dependências
pip install -r requirements.txt

# Verificar instalação
pip list
```

**Dependências instaladas:**
- selenium (automação web)
- webdriver-manager (gerenciamento de drivers)
- python-dotenv (variáveis de ambiente)
- tqdm (barra de progresso)
- rich (output formatado)
- requests (requisições HTTP)

### Passo 3: Verificar Configurações

**Revisar `config/config.json`:**
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
  "checkpoint_file": "checkpoints/download_state.json",
  "log_dir": "logs",
  "max_wait_download": 60,
  "page_load_timeout": 30
}
```

### Passo 4: Teste de Instalação

```bash
# Testar importações
python -c "import selenium; import tqdm; import rich; print('✓ Todas as dependências OK!')"
```

## ✅ Primeira Execução

```bash
# Executar scraper
python main.py
```

**O que esperar:**
1. Navegador Chrome abrirá automaticamente
2. **Sistema aguardará 5 minutos para você fazer login manualmente**
3. Detecção automática do login concluído
4. Navegação até relatórios XPerformance
5. Início dos downloads (80 lotes)
6. Barra de progresso no terminal
7. Extração automática dos ZIPs
8. Resumo final da execução

**⚠️ ATENÇÃO**: Tenha suas credenciais XPI em mãos antes de executar!

## 🔧 Solução de Problemas na Instalação

### Erro: "pip não é reconhecido"

```bash
# Adicionar Python ao PATH ou usar:
python -m pip install -r requirements.txt
```

### Erro: "Microsoft Visual C++ 14.0 is required"

**Windows:**
1. Baixe: [Visual C++ Build Tools](https://visualstudio.microsoft.com/downloads/)
2. Instale "Desktop development with C++"
3. Reinstale dependências

### Erro: "ChromeDriver incompatível"

```bash
# Atualizar webdriver-manager
pip install --upgrade webdriver-manager

# Limpar cache
pip cache purge
```

### Erro: "Permission denied" ao criar diretórios

```bash
# Executar como administrador ou verificar permissões
icacls "c:\Users\Usuário\vBox\Business Intelligence - Brandao\AUTOMACOES\XPERFORMANCE" /grant %username%:F /t
```

## 📁 Estrutura Criada Automaticamente

Ao executar pela primeira vez, o sistema cria:

```
XPERFORMANCE/
├── downloads/
│   ├── zips/          # Criado automaticamente
│   └── pdfs/          # Criado automaticamente
├── logs/              # Criado automaticamente
└── checkpoints/       # Criado automaticamente
```

## 🔐 Segurança

### Segurança do Login

- **Login manual**: Suas credenciais nunca são armazenadas no código
- **Sem arquivos .env**: Não há risco de vazamento de credenciais
- **Sessão temporária**: Credenciais existem apenas durante a execução

O arquivo `.gitignore` protege:
- `downloads/` (arquivos baixados)
- `logs/` (logs de execução)
- `checkpoints/` (estado do progresso)

## 📊 Requisitos de Sistema

### Mínimo
- **RAM**: 4 GB
- **Disco**: 5 GB livres (para PDFs)
- **Internet**: Conexão estável (10 Mbps+)
- **OS**: Windows 10+, Linux, macOS

### Recomendado
- **RAM**: 8 GB+
- **Disco**: 10 GB+ livres
- **Internet**: 50 Mbps+
- **Processador**: Quad-core

## 🌐 Configuração de Proxy (Opcional)

Se sua rede usa proxy, edite `src/scraper.py`:

```python
chrome_options.add_argument('--proxy-server=http://proxy:porta')
```

## 📝 Checklist Final

Antes de executar pela primeira vez:

- [ ] Python 3.8+ instalado
- [ ] Google Chrome instalado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Ambiente virtual ativado (recomendado)
- [ ] Credenciais XPI em mãos (para login manual)
- [ ] Conexão com internet estável
- [ ] Espaço em disco suficiente (5+ GB)
- [ ] Permissões de escrita no diretório

## 🎯 Próximos Passos

Após instalação bem-sucedida:

1. **Leia**: `QUICK_START.md` para uso rápido
2. **Consulte**: `README.md` para documentação completa
3. **Entenda**: `CONTEXT.md` para detalhes técnicos
4. **Execute**: `python main.py` para iniciar

## 💡 Dicas de Instalação

1. **Use ambiente virtual** para isolar dependências
2. **Mantenha Chrome atualizado** para compatibilidade
3. **Tenha credenciais em mãos** antes de executar
4. **Faça login em até 5 minutos** quando o navegador abrir
5. **Verifique logs** em caso de problemas

## 📞 Suporte

Em caso de problemas:
1. Verifique logs em `logs/`
2. Consulte seção de troubleshooting no `README.md`
3. Revise configurações em `config/config.json`
4. Certifique-se de fazer login em até 5 minutos

---

**Instalação concluída?** Execute: `python main.py`
