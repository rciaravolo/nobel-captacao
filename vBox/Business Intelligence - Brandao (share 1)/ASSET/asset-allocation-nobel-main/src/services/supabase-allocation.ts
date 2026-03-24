import { supabase } from '@/integrations/supabase/client';
import { Scenario, Subclass } from '@/types/portfolio';

interface AssetAllocationRow {
  CLASSE: string;
  SUBCLASSE: string;
  CONSERVADORA: string;
  MODERADA: string;
  SOFISTICADA: string;
}

export class SupabaseAllocationService {
  private static _latestMonth: string | null = null;

  /** Retorna o mês mais recente com dados em recommended_products (com cache). */
  static async getCurrentMonth(): Promise<string> {
    if (this._latestMonth) return this._latestMonth;

    try {
      const { data } = await supabase
        .from('recommended_products')
        .select('month_year')
        .order('month_year', { ascending: false })
        .limit(1);

      if (data && data.length > 0) {
        this._latestMonth = data[0].month_year;
        return this._latestMonth;
      }
    } catch (e) {
      console.warn('Não foi possível buscar mês mais recente:', e);
    }

    // Fallback: primeiro dia do mês atual
    const now = new Date();
    this._latestMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-01`;
    return this._latestMonth;
  }

  static async fetchAllocationData(): Promise<AssetAllocationRow[]> {
    const { data, error } = await supabase
      .from('Asset Allocation' as any)
      .select('*');

    if (error) {
      console.error('Error fetching allocation data:', error);
      throw new Error('Erro ao buscar dados de alocação');
    }

    return (data as any) || [];
  }

  static parsePercentage(percentageStr: string): number {
    // Convert "70,00%" to 0.70
    if (!percentageStr || percentageStr === '-' || percentageStr === '0,00%') {
      return 0;
    }
    const cleaned = percentageStr.replace('%', '').replace(',', '.');
    const parsed = parseFloat(cleaned) / 100;
    console.log(`Parsing ${percentageStr} -> ${cleaned} -> ${parsed}`);
    return parsed;
  }

  static async buildScenariosFromSupabase(): Promise<Scenario[]> {
    const allocationData = await this.fetchAllocationData();
    
    const scenarios: Scenario[] = [
      {
        id: 'conservative',
        name: 'Conservadora', 
        description: 'Perfil focado em preservação de capital e baixa volatilidade',
        expected_return: 'CDI + 1%',
        target_vol: 1.25,
        spread: 0.01,
        subclasses: []
      },
      {
        id: 'moderate',
        name: 'Moderada',
        description: 'Perfil balanceado entre segurança e crescimento', 
        expected_return: 'CDI + 2%',
        target_vol: 4.0,
        spread: 0.02,
        subclasses: []
      },
      {
        id: 'sophisticated',
        name: 'Sofisticada',
        description: 'Perfil agressivo com foco em crescimento de longo prazo',
        expected_return: 'CDI + 3%',
        target_vol: 8.0,
        spread: 0.03,
        subclasses: []
      }
    ];

    // Build subclasses for each scenario
    console.log('Fetched allocation data:', allocationData);
    allocationData.forEach(row => {
      const subClasse = (row as any)['SUB-CLASSE'] ?? row.SUBCLASSE ?? '-';
      const subclassName = subClasse === '-'
        ? row.CLASSE
        : `${row.CLASSE} - ${subClasse}`;

      // Conservative scenario
      const conservativeWeight = this.parsePercentage(row.CONSERVADORA);
      if (conservativeWeight > 0) {
        scenarios[0].subclasses.push({
          name: subclassName,
          weight: conservativeWeight
        });
      }

      // Moderate scenario
      const moderateWeight = this.parsePercentage(row.MODERADA);
      if (moderateWeight > 0) {
        scenarios[1].subclasses.push({
          name: subclassName,
          weight: moderateWeight
        });
      }

      // Sophisticated scenario
      const sophisticatedWeight = this.parsePercentage(row.SOFISTICADA);
      if (sophisticatedWeight > 0) {
        scenarios[2].subclasses.push({
          name: subclassName,
          weight: sophisticatedWeight
        });
      }
    });

    return scenarios;
  }
}