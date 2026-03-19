import { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { PortfolioForm } from '@/components/PortfolioForm';
import { AllocationResults } from '@/components/AllocationResults';
import { ProjectionChart } from '@/components/ProjectionChart';
import { AllocationInput, AllocationResult, ProjectionPoint } from '@/types/portfolio';
import { AllocationService } from '@/services/allocation';
import { ProjectionService } from '@/services/projection';
import { Link } from 'react-router-dom';
import { BarChart3, TrendingUp } from 'lucide-react';
import nobelLogo from '@/assets/nobel-logo.png';

const Index = () => {
  const [results, setResults] = useState<AllocationResult[] | null>(null);
  const [projections, setProjections] = useState<ProjectionPoint[] | null>(null);
  const [currentInput, setCurrentInput] = useState<AllocationInput | null>(null);
  const [loading, setLoading] = useState(false);

  const handleFormSubmit = useCallback(async (data: AllocationInput) => {
    setLoading(true);
    
    try {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Calculate allocation using Supabase data
      const allocationResults = await AllocationService.allocate(data);
      setResults(allocationResults);
      
      // Calculate projections for all scenarios (using 24 months as default)
      const allProjections = ProjectionService.projectAllScenarios(
        data.valor_captado,
        data.cdi_anual,
        24
      );
      setProjections(allProjections);
      setCurrentInput(data);
      
    } catch (error) {
      console.error('Error calculating allocation:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  const [selectedScenario, setSelectedScenario] = useState<any>(null);

  useEffect(() => {
    const loadSelectedScenario = async () => {
      if (currentInput) {
        const scenario = await AllocationService.getScenario(currentInput.perfil);
        setSelectedScenario(scenario);
      }
    };

    loadSelectedScenario();
  }, [currentInput]);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="grid grid-cols-3 items-center">
            {/* Logo - Left */}
            <div className="flex items-center gap-4">
              <img 
                src={nobelLogo} 
                alt="Nobel Capital" 
                className="h-12 w-auto"
              />
            </div>
            
            {/* Title - Center */}
            <div className="text-center">
              <h1 className="text-2xl font-bold" style={{color: '#202020'}}>Portfolio Advisor</h1>
              <p className="text-sm text-muted-foreground">
                Alocação inteligente e projeção de carteiras
              </p>
            </div>
            
            {/* Button - Right */}
            <div className="flex justify-end">
              <Link to="/materiais">
                <Button variant="outline" className="gap-2">
                  <BarChart3 className="w-4 h-4" />
                  Materiais
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8 space-y-8">
        {/* Form Section */}
        <PortfolioForm onSubmit={handleFormSubmit} loading={loading} />

        {/* Results Section */}
        {results && currentInput && selectedScenario && (
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold mb-2" style={{color: '#202020'}}>
                Resultados da Alocação
              </h2>
              <p className="text-muted-foreground">
                Perfil <span className="font-semibold text-primary">{selectedScenario.name}</span> • 
                Retorno Esperado: <span className="font-semibold text-success">{selectedScenario.expected_return}</span> • 
                Volatilidade Alvo: <span className="font-semibold">{selectedScenario.target_vol}%</span>
              </p>
            </div>

            <div className="w-full">
              <AllocationResults 
                results={results} 
                totalValue={currentInput.valor_captado}
                scenario={selectedScenario.name}
              />
            </div>

            {projections && (
              <ProjectionChart 
                data={projections} 
                highlightScenario={selectedScenario.name}
              />
            )}
          </div>
        )}

        {/* Empty State */}
        {!results && !loading && (
          <div className="text-center py-16">
            <div className="w-16 h-16 bg-gradient-to-br from-primary/20 to-primary-light/20 rounded-full flex items-center justify-center mx-auto mb-4">
              <TrendingUp className="w-8 h-8 text-primary" />
            </div>
            <h3 className="text-lg font-semibold mb-2" style={{color: '#202020'}}>
              Configure sua carteira
            </h3>
            <p className="text-muted-foreground max-w-md mx-auto">
              Preencha o formulário acima para calcular a alocação ideal baseada no seu perfil 
              de investimento e visualizar as projeções de retorno.
            </p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-border bg-card mt-16">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <p>© 2024 Portfolio Advisor. Ferramenta para alocação e projeção de carteiras.</p>
            <p>Desenvolvido com React + TypeScript</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;