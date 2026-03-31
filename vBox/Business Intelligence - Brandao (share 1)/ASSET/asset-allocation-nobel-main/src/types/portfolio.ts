export interface Subclass {
  name: string;
  weight: number; // Peso em decimal (0.1 = 10%)
}

export interface Scenario {
  id: string;
  name: string;
  description: string;
  expected_return: string;
  target_vol: number;
  spread: number; // Spread sobre o CDI
  subclasses: Subclass[];
}

export interface AllocationInput {
  valor_captado: number;
  perfil: string;
  cdi_anual: number;
}

export interface AllocationResult {
  classe: string;
  subclass: string;
  percentage: number;
  value: number;
}

export interface ProjectionPoint {
  month: number;
  value: number;
  scenario: string;
}

export interface MarketReturn {
  classe: string;
  indice: string;
  mes_atual: number;
  no_ano: number;
  em_12m: number;
  em_36m: number;
  em_60m: number;
}