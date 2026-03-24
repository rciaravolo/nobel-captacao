import { Scenario } from '@/types/portfolio';

export const defaultScenarios: Scenario[] = [
  {
    id: 'conservative',
    name: 'Conservadora',
    description: 'Perfil focado em preservação de capital e baixa volatilidade',
    expected_return: 'CDI + 1%',
    target_vol: 1.25,
    spread: 0.01,
    subclasses: [
      { name: 'RENDA FIXA BRASIL - Pós-fixado',    weight: 0.70 },
      { name: 'RENDA FIXA BRASIL - Inflação',       weight: 0.125 },
      { name: 'RENDA FIXA BRASIL - Prefixado',      weight: 0.05 },
      { name: 'MULTIMERCADOS',                      weight: 0.05 },
      { name: 'FUNDOS LISTADOS',                    weight: 0.025 },
      { name: 'GLOBAL - Renda Fixa',                weight: 0.025 },
      { name: 'GLOBAL - Renda Variável',            weight: 0.025 },
    ]
  },
  {
    id: 'moderate',
    name: 'Moderada',
    description: 'Perfil balanceado entre segurança e crescimento',
    expected_return: 'CDI + 2%',
    target_vol: 4.0,
    spread: 0.02,
    subclasses: [
      { name: 'RENDA FIXA BRASIL - Pós-fixado',    weight: 0.325 },
      { name: 'RENDA FIXA BRASIL - Inflação',       weight: 0.225 },
      { name: 'MULTIMERCADOS',                      weight: 0.165 },
      { name: 'RENDA FIXA BRASIL - Prefixado',      weight: 0.10 },
      { name: 'RENDA VARIÁVEL BRASIL',              weight: 0.075 },
      { name: 'ALTERNATIVOS',                       weight: 0.03 },
      { name: 'GLOBAL - Renda Variável',            weight: 0.035 },
      { name: 'GLOBAL - Renda Fixa',                weight: 0.025 },
      { name: 'FUNDOS LISTADOS',                    weight: 0.02 },
    ]
  },
  {
    id: 'sophisticated',
    name: 'Sofisticada',
    description: 'Perfil agressivo com foco em crescimento de longo prazo',
    expected_return: 'CDI + 3%',
    target_vol: 8.0,
    spread: 0.03,
    subclasses: [
      { name: 'RENDA FIXA BRASIL - Inflação',       weight: 0.275 },
      { name: 'RENDA VARIÁVEL BRASIL',              weight: 0.175 },
      { name: 'RENDA FIXA BRASIL - Pós-fixado',    weight: 0.125 },
      { name: 'MULTIMERCADOS',                      weight: 0.125 },
      { name: 'FUNDOS LISTADOS',                    weight: 0.08 },
      { name: 'ALTERNATIVOS',                       weight: 0.07 },
      { name: 'GLOBAL - Renda Variável',            weight: 0.05 },
      { name: 'RENDA FIXA BRASIL - Prefixado',      weight: 0.075 },
      { name: 'GLOBAL - Renda Fixa',                weight: 0.025 },
    ]
  }
];
