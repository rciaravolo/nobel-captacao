import { AllocationInput, AllocationResult, Scenario } from '@/types/portfolio';
import { SupabaseAllocationService } from './supabase-allocation';

export class AllocationService {
  private static scenarios: Scenario[] | null = null;

  static async getScenarios(): Promise<Scenario[]> {
    if (!this.scenarios) {
      this.scenarios = await SupabaseAllocationService.buildScenariosFromSupabase();
    }
    return this.scenarios;
  }

  static validateWeights(scenario: Scenario): boolean {
    const totalWeight = scenario.subclasses.reduce((sum, sub) => sum + sub.weight, 0);
    return Math.abs(totalWeight - 1.0) < 0.1; // More tolerance for rounding differences
  }

  static getFixedStructure(): { classe: string; subclass: string }[] {
    return [
      { classe: 'Renda Fixa', subclass: 'Renda Fixa Pós-fixada' },
      { classe: 'Renda Fixa', subclass: 'Renda Fixa Pré-fixada' },
      { classe: 'Renda Fixa', subclass: 'Renda Fixa Inflação' },
      { classe: 'Ações', subclass: 'Ações Brasil' },
      { classe: 'Ações', subclass: 'Ações Internacional' },
      { classe: 'Imobiliário', subclass: 'REITs' },
      { classe: 'Commodities', subclass: 'Commodities' },
      { classe: 'Criptomoedas', subclass: 'Criptomoedas' },
    ];
  }

  static async allocate(input: AllocationInput): Promise<AllocationResult[]> {
    const scenarios = await this.getScenarios();
    const scenario = scenarios.find(s => s.id === input.perfil);
    
    if (!scenario) {
      throw new Error(`Perfil não encontrado: ${input.perfil}`);
    }

    if (!this.validateWeights(scenario)) {
      console.warn('Pesos do cenário não somam exatamente 100%', {
        total: scenario.subclasses.reduce((sum, sub) => sum + sub.weight, 0),
        scenario: scenario.name
      });
    }

    // Get fixed structure
    const fixedStructure = this.getFixedStructure();
    
    // Create a map of scenario weights for quick lookup
    const scenarioWeights = new Map<string, number>();
    scenario.subclasses.forEach(subclass => {
      scenarioWeights.set(subclass.name, subclass.weight);
    });

    // Map fixed structure to allocation results
    return fixedStructure.map(item => {
      // Try to find matching weight from scenario
      let weight = 0;
      
      // Check for exact match with full name format
      const fullNameKey = item.subclass === '-' ? item.classe : `${item.classe} - ${item.subclass}`;
      if (scenarioWeights.has(fullNameKey)) {
        weight = scenarioWeights.get(fullNameKey) || 0;
      }
      // Also check for class-only match if no subclass
      else if (item.subclass === '-' && scenarioWeights.has(item.classe)) {
        weight = scenarioWeights.get(item.classe) || 0;
      }
      
      return {
        classe: item.classe,
        subclass: item.subclass,
        percentage: weight * 100,
        value: input.valor_captado * weight
      };
    });
  }

  static async getScenario(perfilId: string): Promise<Scenario | undefined> {
    const scenarios = await this.getScenarios();
    return scenarios.find(s => s.id === perfilId);
  }

  static async getAllScenarios(): Promise<Scenario[]> {
    return this.getScenarios();
  }
}