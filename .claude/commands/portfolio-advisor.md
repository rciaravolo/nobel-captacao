---
description: Contexto completo do projeto Portfolio Advisor (Nobel Capital) — alocação de ativos e projeções de carteira
---

# Portfolio Advisor — Nobel Capital

Projeto React/TypeScript de alocação de ativos para assessores da Nobel Capital. Criado originalmente no Lovable.dev, migrado para desenvolvimento local com Claude Code.

## Localização
`C:\Users\Usuário\vBox\Business Intelligence - Brandao (share 1)\ASSET\asset-allocation-nobel-main`

## Stack
- **Frontend**: React 18 + TypeScript + Vite
- **Styling**: Tailwind CSS + shadcn/ui + CSS variables (HSL)
- **Routing**: React Router v6
- **Charts**: Recharts
- **Backend/DB**: Supabase (tabela `Asset Allocation`)
- **Deploy**: GitHub → `rciaravolo/xperform` (branch master)

## Arquitetura

```
src/
├── pages/
│   ├── Index.tsx          # Página principal — formulário + resultados
│   ├── Materiais.tsx      # Upload/download de PDFs
│   └── NotFound.tsx
├── components/
│   ├── PortfolioForm.tsx  # Formulário de entrada (valor, perfil, CDI)
│   ├── AllocationResults.tsx  # Tabela de alocação
│   ├── ProjectionChart.tsx    # Gráfico recharts (24 meses)
│   └── MarketReturnsTable.tsx # Tabela de retornos de mercado
├── services/
│   ├── allocation.ts          # Lógica de alocação (getFixedStructure + allocate)
│   ├── projection.ts          # Cálculo de projeções por cenário
│   └── supabase-allocation.ts # Fetch + parsing dos dados do Supabase
├── data/
│   └── scenarios.ts           # Cenários default (fallback local)
└── integrations/supabase/
    ├── client.ts              # createClient com URL + anon key
    └── types.ts               # Tipos gerados do schema
```

## Supabase — Tabela `Asset Allocation`

| CLASSE | SUB-CLASSE | CONSERVADORA | MODERADA | SOFISTICADA |
|---|---|---|---|---|
| Renda Fixa | Renda Fixa Pós-fixada | 60% | 40% | 20% |
| Renda Fixa | Renda Fixa Pré-fixada | 25% | 20% | 7% |
| Renda Fixa | Renda Fixa Inflação | 10% | 15% | 3% |
| Ações | Ações Brasil | 3% | 15% | 30% |
| Ações | Ações Internacional | 2% | 5% | 25% |
| Imobiliário | REITs | 0% | 3% | 8% |
| Commodities | Commodities | 0% | 2% | 5% |
| Criptomoedas | Criptomoedas | 0% | 0% | 2% |

## Perfis de Investimento

- **Conservadora** — CDI + 1%, vol 1.25%
- **Moderada** — CDI + 2%, vol 4.0%
- **Sofisticada** — CDI + 3%, vol 8.0%

## Design System

Nobel Capital brand:
- **Gold**: `hsl(48 100% 50%)` — cor primária
- **Dark**: `#0F0E0D` — fundo Obsidian
- **Cream**: `#F5F0E8` — texto principal
- Tipografia: Cormorant Garamond (display) + Outfit (corpo)

## Regras de Desenvolvimento

1. **Não usar `any` no TypeScript** — tipar corretamente
2. **`handleFormSubmit` deve estar em `useCallback`** — evita loop de re-render
3. **`getFixedStructure()` deve bater exatamente com os nomes do Supabase** — CLASSE e SUB-CLASSE case-sensitive
4. **Percentuais como decimal no Supabase** — `parsePercentage("60,00%")` → `0.60`
5. **Projeções usam `defaultScenarios` local** — não dependem do Supabase

## Git

- Repositório: `rciaravolo/xperform` (GitHub)
- Branch: `master`
- Root do git: `C:/Users/Usuário` (o repo cobre todo o BI de Brandao)
- Para commitar: `cd C:/Users/Usuário && git add <path> && git commit`
