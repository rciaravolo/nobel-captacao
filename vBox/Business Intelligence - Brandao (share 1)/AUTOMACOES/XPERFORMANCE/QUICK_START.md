# 🚀 Guia Rápido - XPerformance Scraper

## Instalação Rápida

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Executar
```bash
python main.py
```

## ⚡ Comandos Úteis

### Primeira Execução
```bash
python main.py
```

### Retomar Download Interrompido
```bash
# Apenas execute novamente - retoma automaticamente
python main.py
```

### Resetar Checkpoint (Começar do Zero)
```python
# Deletar arquivo de checkpoint
del checkpoints\download_state.json
python main.py
```

## 📋 Checklist Pré-Execução

- [ ] Python 3.x instalado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Google Chrome instalado
- [ ] Credenciais XPI Hub em mãos (para login manual)
- [ ] Conexão com internet estável

## 🔐 Como Funciona o Login

1. Execute `python main.py`
2. O navegador Chrome abrirá automaticamente
3. **Você tem 5 minutos para fazer login manualmente**
4. O sistema detecta automaticamente quando você faz login
5. O download inicia automaticamente após o login

**⚠️ Se não fizer login em 5 minutos**: O sistema fecha e exibe "Usuário não efetuou o login, recomeçar automação."

## ⚙️ Configurações Rápidas

### Modo Headless (Navegador Invisível)
Edite `config/config.json`:
```json
{
  "headless_mode": true
}
```

### Manter Arquivos ZIP
```json
{
  "keep_zip_files": true
}
```

### Aumentar Timeout
```json
{
  "download_timeout": 600
}
```

## 🔍 Verificar Progresso

### Durante Execução
- Barra de progresso no terminal mostra lote atual
- Logs em tempo real exibem cada operação

### Após Execução
```bash
# Ver logs
type logs\scraper_2026-02-19.log

# Ver apenas erros
type logs\errors_2026-02-19.log

# Ver checkpoint
type checkpoints\download_state.json
```

## 📊 Onde Encontrar os PDFs

```
downloads/pdfs/
├── 2026-01/          # PDFs de janeiro
├── 2026-02/          # PDFs de fevereiro
└── outros/           # PDFs sem data identificável
```

## ❌ Solução Rápida de Problemas

### Timeout de Login
- Execute novamente: `python main.py`
- Faça login mais rapidamente (você tem 5 minutos)
- Verifique se suas credenciais estão corretas

### Erro: "ChromeDriver não encontrado"
```bash
# Reinstalar webdriver-manager
pip install --upgrade webdriver-manager
```

### Download Travado
1. Pressione `Ctrl+C` para interromper
2. Execute novamente - retomará do checkpoint

### Sessão Expirada
- O sistema re-autentica automaticamente
- Se persistir, verifique credenciais em `config/.env`

## 📞 Arquivos Importantes

| Arquivo | Descrição |
|---------|-----------|
| `main.py` | Script principal |
| `config/config.json` | Configurações |
| `config/config.json` | Configurações gerais |
| `CONTEXT.md` | Documentação técnica completa |
| `README.md` | Documentação detalhada |
| `logs/` | Arquivos de log |
| `checkpoints/` | Estado do progresso |

## 💡 Dicas

1. **Primeira execução**: O navegador sempre abre visível para login manual
2. **Login rápido**: Tenha suas credenciais em mãos antes de executar
3. **Execuções mensais**: Mantenha o checkpoint para histórico
4. **Backup**: Faça backup da pasta `downloads/pdfs/` após cada execução
5. **Logs**: Revise logs após execução para identificar possíveis problemas

## 🎯 Fluxo Típico

```
1. python main.py
   ↓
2. Fazer login manual no navegador (5 min)
   ↓
3. Aguardar conclusão (~90-120 minutos)
   ↓
4. Verificar resumo no terminal
   ↓
5. PDFs disponíveis em downloads/pdfs/
```

## 📈 Estimativas

- **Tempo total**: 90-120 minutos
- **Lotes**: ~80 iterações
- **PDFs**: ~4.000 arquivos
- **Tamanho**: ~1-2 GB

---

**Precisa de mais detalhes?** Consulte `README.md` ou `CONTEXT.md`
