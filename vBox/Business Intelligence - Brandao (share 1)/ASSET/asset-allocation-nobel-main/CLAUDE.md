# Portfolio Advisor — Nobel Capital

Projeto React/TypeScript de alocação de ativos para assessores da Nobel Capital. Criado originalmente no Lovable.dev, migrado para desenvolvimento local com Claude Code.

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
│   ├── Index.tsx              # Página principal — formulário + resultados
│   ├── Materiais.tsx          # Upload/download de PDFs
│   └── NotFound.tsx
├── components/
│   ├── PortfolioForm.tsx      # Formulário de entrada (valor, perfil)
│   ├── AllocationResults.tsx  # Tabela de alocação com barras
│   ├── ProjectionChart.tsx    # Gráfico recharts 24 meses
│   └── MarketReturnsTable.tsx # Tabela de retornos de mercado
├── services/
│   ├── allocation.ts          # Lógica principal — getFixedStructure + allocate
│   ├── projection.ts          # Cálculo de projeções por cenário
│   └── supabase-allocation.ts # Fetch + parsing dos dados do Supabase
├── data/
│   └── scenarios.ts           # Cenários default (fallback local)
└── integrations/supabase/
    ├── client.ts              # createClient (URL + anon key hardcoded)
    └── types.ts               # Tipos gerados do schema Supabase
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

**IMPORTANTE**: Os nomes de CLASSE e SUB-CLASSE são case-sensitive. `getFixedStructure()` em `allocation.ts` deve bater exatamente com esses valores.

## Perfis de Investimento

| ID | Nome | Retorno | Volatilidade |
|---|---|---|---|
| `conservative` | Conservadora | CDI + 1% | 1.25% |
| `moderate` | Moderada | CDI + 2% | 4.0% |
| `sophisticated` | Sofisticada | CDI + 3% | 8.0% |

## Design System — Obsidian Vault

- **Fundo**: `hsl(25 8% 6%)` — quase preto quente
- **Ouro Nobel**: `hsl(42 78% 52%)` — cor primária e acento
- **Creme**: `hsl(36 40% 92%)` — texto principal
- **Tipografia**: Cormorant Garamond (display/headers) + Outfit (corpo)
- **Cards**: `vault-card` class — borda superior dourada sutil
- **Animações**: `animate-fade-up` com `animate-delay-100/200/300/400`

## Regras de Desenvolvimento

1. **`handleFormSubmit` deve estar em `useCallback`** — evita loop infinito de re-renders
2. **`getFixedStructure()` case-sensitive** com os nomes do Supabase
3. **Percentuais como decimal** — `parsePercentage("60,00%")` → `0.60`
4. **Projeções usam `defaultScenarios` local** — não dependem do Supabase
5. **Tipagem TypeScript** — evitar `any`, tipar corretamente

## Git

- Repositório: `rciaravolo/xperform` (GitHub)
- Branch: `master`
- **Root do git está em `C:/Users/Usuário`** — não dentro do projeto
- Para commitar:
  ```bash
  cd "C:/Users/Usuário"
  git add "vBox/Business Intelligence - Brandao (share 1)/ASSET/asset-allocation-nobel-main/<arquivo>"
  git commit -m "..."
  git push origin master
  ```

## Comandos Úteis

```bash
npm run dev      # dev server (Vite)
npm run build    # build produção
npm run preview  # preview do build
```
