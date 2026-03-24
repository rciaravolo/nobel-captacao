import { supabase } from '@/integrations/supabase/client';

export interface RecommendedProduct {
  id: string;
  month_year: string;
  asset_class: string;
  asset_subclass: string;
  profile: string;
  product_name: string;
  percentage: number | null;
  expected_return: string | null;
  eligibility: string | null;
  product_type: string | null;
}

/**
 * Normaliza os nomes de classe que vêm da tabela de alocação (Asset Allocation / defaultScenarios)
 * para os valores padronizados usados na tabela recommended_products (gerados pelo AI).
 *
 * Necessário porque o fallback defaultScenarios usa nomes em português (ex: "Ações Brasil"),
 * enquanto a extração AI usa os nomes em caps (ex: "RENDA VARIÁVEL BRASIL").
 */
const CLASS_MAP: Record<string, { asset_class: string; asset_subclass: string }> = {
  // defaultScenarios fallback → recommended_products
  'Ações Brasil':          { asset_class: 'RENDA VARIÁVEL BRASIL', asset_subclass: 'Ações Brasil' },
  'Ações Internacional':   { asset_class: 'RENDA VARIÁVEL GLOBAL', asset_subclass: 'Ações Internacional' },
  'Renda Fixa Pós-fixada': { asset_class: 'RENDA FIXA BRASIL',    asset_subclass: 'Pós-fixado' },
  'Renda Fixa Pré-fixada': { asset_class: 'RENDA FIXA BRASIL',    asset_subclass: 'Prefixado' },
  'Renda Fixa Inflação':   { asset_class: 'RENDA FIXA BRASIL',    asset_subclass: 'Inflação' },
  'REITs':                 { asset_class: 'FUNDOS LISTADOS',       asset_subclass: 'FII' },
  'Commodities':           { asset_class: 'ALTERNATIVOS',          asset_subclass: 'Commodities' },
  'Criptomoedas':          { asset_class: 'ALTERNATIVOS',          asset_subclass: 'Cripto' },
};

function normalize(classe: string, subclasse: string): { asset_class: string; asset_subclass: string } {
  // Se o nome da classe já é o padrão caps (dados reais do Supabase), usa direto
  if (classe === classe.toUpperCase() || CLASS_MAP[classe] === undefined) {
    return {
      asset_class: classe,
      asset_subclass: subclasse === '-' ? classe : subclasse,
    };
  }
  // Caso contrário, aplica o mapeamento do fallback
  return CLASS_MAP[classe] ?? { asset_class: classe, asset_subclass: subclasse };
}

export class RecommendationsService {
  static async getRecommendationsForAllocation(
    profile: string,
    assetClass: string,
    assetSubclass: string,
    monthYear?: string
  ): Promise<RecommendedProduct[]> {
    try {
      const { asset_class, asset_subclass } = normalize(assetClass, assetSubclass);
      const month = monthYear || new Date().toISOString().slice(0, 10);

      // Quando a linha de alocação não tem subclasse específica ('-'),
      // busca todos os produtos da classe sem filtrar por subclasse
      let query = supabase
        .from('recommended_products')
        .select('*')
        .eq('profile', profile)
        .eq('asset_class', asset_class)
        .eq('month_year', month);

      if (assetSubclass !== '-') {
        query = query.eq('asset_subclass', asset_subclass);
      }

      const { data, error } = await query.order('percentage', { ascending: false, nullsFirst: false });

      if (error) {
        console.error('Error fetching recommendations:', error);
        return [];
      }

      return data || [];
    } catch (error) {
      console.error('Error in getRecommendationsForAllocation:', error);
      return [];
    }
  }

  static async getAllRecommendationsForProfile(
    profile: string,
    monthYear?: string
  ): Promise<RecommendedProduct[]> {
    try {
      const { data, error } = await supabase
        .from('recommended_products')
        .select('*')
        .eq('profile', profile)
        .eq('month_year', monthYear || new Date().toISOString().slice(0, 10))
        .order('asset_class', { ascending: true })
        .order('asset_subclass', { ascending: true })
        .order('percentage', { ascending: false, nullsFirst: false });

      if (error) {
        console.error('Error fetching all recommendations:', error);
        return [];
      }

      return data || [];
    } catch (error) {
      console.error('Error in getAllRecommendationsForProfile:', error);
      return [];
    }
  }
}
