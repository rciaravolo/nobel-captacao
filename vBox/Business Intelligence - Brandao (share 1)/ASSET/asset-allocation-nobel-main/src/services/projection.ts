import { ProjectionPoint, Scenario } from '@/types/portfolio';
import { defaultScenarios } from '@/data/scenarios';

export class ProjectionService {
  static project(valor: number, perfil: string, cdiAnual: number, meses: number): ProjectionPoint[] {
    const scenario = defaultScenarios.find(s => s.id === perfil);
    
    if (!scenario) {
      throw new Error(`Perfil não encontrado: ${perfil}`);
    }

    // Taxa anual real = CDI + spread do perfil
    const taxaAnualReal = cdiAnual + scenario.spread;
    const taxaMensalReal = Math.pow(1 + taxaAnualReal, 1/12) - 1;

    const points: ProjectionPoint[] = [];
    
    for (let month = 0; month <= meses; month++) {
      const value = valor * Math.pow(1 + taxaMensalReal, month);
      points.push({
        month,
        value,
        scenario: scenario.name
      });
    }

    return points;
  }

  static projectAllScenarios(valor: number, cdiAnual: number, meses: number): ProjectionPoint[] {
    const allPoints: ProjectionPoint[] = [];
    
    for (const scenario of defaultScenarios) {
      const taxaAnualReal = cdiAnual + scenario.spread;
      const taxaMensalReal = Math.pow(1 + taxaAnualReal, 1/12) - 1;
      
      for (let month = 0; month <= meses; month++) {
        const value = valor * Math.pow(1 + taxaMensalReal, month);
        allPoints.push({
          month,
          value,
          scenario: scenario.name
        });
      }
    }

    return allPoints;
  }

  static calculateMonthlyReturn(taxaAnual: number): number {
    return Math.pow(1 + taxaAnual, 1/12) - 1;
  }

  static calculateFinalValue(valorInicial: number, taxaAnual: number, meses: number): number {
    const taxaMensal = this.calculateMonthlyReturn(taxaAnual);
    return valorInicial * Math.pow(1 + taxaMensal, meses);
  }
}