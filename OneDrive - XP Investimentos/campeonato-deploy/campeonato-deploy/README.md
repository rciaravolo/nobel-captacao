# Campeonato da Soneca

Site estático de um campeonato de palpites. Arquivo único em HTML com persistência via `localStorage`.

## Deploy na Vercel

### Opção 1 — Pelo painel da Vercel (mais fácil)

1. Acesse https://vercel.com/new
2. Clique em **"Import Git Repository"** ou em **"Deploy"** sem repositório
3. Arraste a pasta inteira (ou suba um zip dela)
4. **Framework Preset:** "Other" (ou deixa Vercel detectar)
5. **Root Directory:** `./`
6. Clique em **Deploy**

Em ~30 segundos o site está no ar com URL tipo `campeonato-soneca.vercel.app`.

### Opção 2 — Via CLI (terminal)

```bash
npm i -g vercel
cd campeonato-deploy
vercel
```

Vai pedir login (faz pelo navegador) e algumas confirmações. Aceita os defaults.

Depois, pra publicar em produção:
```bash
vercel --prod
```

### Opção 3 — Via GitHub

1. Cria um repo novo no GitHub
2. Sobe os arquivos desta pasta
3. Em https://vercel.com/new conecta o repo
4. Deploy automático a cada push

## Estrutura

```
campeonato-deploy/
├── index.html        ← o site inteiro (HTML + CSS + JS)
└── vercel.json       ← configuração da Vercel
```

## Importante: dados ficam no navegador

O campeonato usa `localStorage`, então:
- Cada navegador/dispositivo guarda os próprios dados
- Os 6 participantes não compartilham um estado em tempo real
- Use o botão **Exportar dados** pra fazer backup periódico
- Pra continuar de outro dispositivo, **Importar dados** do JSON exportado

Se quiser que todos vejam o mesmo ranking ao mesmo tempo (sincronizado), precisa de backend — fala comigo que adapto.
