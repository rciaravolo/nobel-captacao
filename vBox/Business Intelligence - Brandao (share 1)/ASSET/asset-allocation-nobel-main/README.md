# Portfolio Advisor — Nobel Capital

Ferramenta de alocação de ativos para assessores da Nobel Capital. Desenvolvida com React + TypeScript, integrada ao Supabase, e mantida via **Claude Code**.

## Stack

- **Frontend**: React 18 + TypeScript + Vite
- **Styling**: Tailwind CSS + shadcn/ui
- **Charts**: Recharts
- **Backend/DB**: Supabase
- **Deploy**: GitHub (`rciaravolo/xperform`, branch `master`)

## Como rodar localmente

```sh
# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento
npm run dev

# Build de produção
npm run build
```

## Desenvolvimento

Este projeto é mantido localmente com **Claude Code** (CLI da Anthropic).

```sh
# Abrir Claude Code na raiz do projeto
claude
```

Todas as alterações são versionadas via Git e publicadas no repositório `rciaravolo/xperform`.

## Estrutura

```
src/
├── pages/
│   ├── Index.tsx              # Página principal
│   └── Materiais.tsx          # Upload/download de PDFs
├── components/
│   ├── PortfolioForm.tsx      # Formulário de entrada
│   ├── AllocationResults.tsx  # Tabela de alocação
│   └── ProjectionChart.tsx    # Gráfico de projeção (24 meses)
├── services/
│   ├── allocation.ts          # Lógica de alocação
│   ├── projection.ts          # Cálculo de cenários
│   └── supabase-allocation.ts # Integração Supabase
└── data/
    └── scenarios.ts           # Cenários default (fallback local)
```

## Perfis de Investimento

| Perfil | Retorno Esperado | Volatilidade |
|---|---|---|
| Conservadora | CDI + 1% | 1,25% |
| Moderada | CDI + 2% | 4,0% |
| Sofisticada | CDI + 3% | 8,0% |
