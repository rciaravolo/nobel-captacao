import { AllocationInput, AllocationResult, Scenario } from '@/types/portfolio';
import { SupabaseAllocationService } from './supabase-allocation';
import { defaultScenarios } from '@/data/scenarios';

export class AllocationService {
  private static scenarios: Scenario[] | null = null;

  static async getScenarios(): Promise<Scenario[]> {
    if (!this.scenarios) {
      try {
        const supabaseScenarios = await SupabaseAllocationService.buildScenariosFromSupabase();
        // Use Supabase data only if subclasses were actually loaded
        const hasData = supabaseScenarios.some(s => s.subclasses.length > 0);
        this.scenarios = hasData ? supabaseScenarios : defaultScenarios;
      } catch (error) {
        console.warn('Supabase unavailable, using default scenarios:', error);
        this.scenarios = defaultScenarios;
      }
    }
    return this.scenarios;
  }

  static validateWeights(scenario: Scenario): boolean {
    const totalWeight = scenario.subclasses.reduce((sum, sub) => sum + sub.weight, 0);
    return Math.abs(totalWeight - 1.0) < 0.1; // More tolerance for rounding differences
  }

  static getFixedStructure(): { classe: string; subclass: string }[] {
    return [
      { classe: 'RENDA FIXA BRASIL', subclass: 'Pós-fixado' },
      { classe: 'RENDA FIXA BRASIL', subclass: 'Inflação' },
      { classe: 'RENDA FIXA BRASIL', subclass: 'Prefixado' },
      { classe: 'MULTIMERCADOS', subclass: '-' },
      { classe: 'RENDA VARIÁVEL BRASIL', subclass: '-' },
      { classe: 'FUNDOS LISTADOS', subclass: '-' },
      { classe: 'ALTERNATIVOS', subclass: '-' },
      { classe: 'GLOBAL', subclass: 'Renda Fixa' },
      { classe: 'GLOBAL', subclass: 'Renda Variável' }
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

    // Use dynamic structure directly from Supabase scenario data
    if (scenario.subclasses.length > 0) {
      return scenario.subclasses.map(subclass => {
        // Parse "CLASSE - SUBCLASSE" key back into parts
        const dashIndex = subclass.name.lastIndexOf(' - ');
        let classe: string;
        let sub: string;
        if (dashIndex !== -1) {
          classe = subclass.name.substring(0, dashIndex);
          sub = subclass.name.substring(dashIndex + 3);
        } else {
          classe = subclass.name;
          sub = '-';
        }
        return {
          classe,
          subclass: sub,
          percentage: subclass.weight * 100,
          value: input.valor_captado * subclass.weight
        };
      });
    }

    // Fallback to fixed structure if no Supabase data
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