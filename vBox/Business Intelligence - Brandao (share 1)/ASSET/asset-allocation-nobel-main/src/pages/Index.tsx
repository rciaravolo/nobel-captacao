import { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { PortfolioForm } from '@/components/PortfolioForm';
import { AllocationResults } from '@/components/AllocationResults';
import { AllocationChart } from '@/components/AllocationChart';
import { ThemeToggle } from '@/components/ThemeToggle';
import { MobileMenu } from '@/components/MobileMenu';
import { ProductsAvailabilityDialog } from '@/components/ProductsAvailabilityDialog';
import { AllocationInput, AllocationResult } from '@/types/portfolio';
import { AllocationService } from '@/services/allocation';
import { PDFExportService } from '@/services/pdf-export';
import { RecommendationsService, RecommendedProduct } from '@/services/recommendations';
import { SupabaseAllocationService } from '@/services/supabase-allocation';
import { Link } from 'react-router-dom';
import { BarChart3, TrendingUp, Download } from 'lucide-react';
import nobelLogo from '@/assets/nobel-logo.png';

const Index = () => {
  const [results, setResults] = useState<AllocationResult[] | null>(null);
  const [currentInput, setCurrentInput] = useState<AllocationInput | null>(null);
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState<RecommendedProduct[]>([]);
  const [selectedScenario, setSelectedScenario] = useState<any>(null);
  const [exportingPDF, setExportingPDF] = useState(false);

  const handleFormSubmit = useCallback(async (data: AllocationInput) => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 800));
      const allocationResults = await AllocationService.allocate(data);
      setResults(allocationResults);
      setCurrentInput(data);
    } catch (error) {
      console.error('Error calculating allocation:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const loadSelectedScenario = async () => {
      if (!currentInput) return;
      const scenario = await AllocationService.getScenario(currentInput.perfil);
      setSelectedScenario(scenario);

      const profileMap: Record<string, string> = {
        'Conservadora': 'conservative',
        'Moderada': 'moderate',
        'Sofisticada': 'sophisticated'
      };
      const profile = profileMap[scenario?.name || ''] || 'moderate';
      const monthYear = await SupabaseAllocationService.getCurrentMonth();
      const allRecs = await RecommendationsService.getAllRecommendationsForProfile(profile, monthYear);
      setRecommendations(allRecs);
    };
    loadSelectedScenario();
  }, [currentInput]);

  const handleExportPDF = async () => {
    if (!results || !currentInput || !selectedScenario) return;
    setExportingPDF(true);
    try {
      await PDFExportService.exportProposal(results, currentInput.valor_captado, selectedScenario.name, recommendations);
    } catch (error) {
      console.error('Error exporting PDF:', error);
    } finally {
      setExportingPDF(false);
    }
  };

  const handleExportProductsList = async () => {
    if (!selectedScenario || !recommendations.length) return;
    setExportingPDF(true);
    try {
      await PDFExportService.exportProductsList(recommendations, selectedScenario.name);
    } catch (error) {
      console.error('Error exporting products list:', error);
    } finally {
      setExportingPDF(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <ProductsAvailabilityDialog />

      {/* Header */}
      <header className="border-b border-border bg-card shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          {/* Mobile */}
          <div className="flex items-center justify-between md:hidden">
            <MobileMenu />
            <div className="flex-1 flex justify-center">
              <img src={nobelLogo} alt="Nobel Capital" className="h-10 w-auto" width="173" height="48" />
            </div>
            <div className="w-10" />
          </div>

          {/* Desktop */}
          <div className="hidden md:grid grid-cols-3 items-center">
            <div className="flex items-center gap-4">
              <img src={nobelLogo} alt="Nobel Capital" className="h-12 w-auto" width="173" height="48" />
            </div>
            <div className="text-center">
              <h1 className="text-2xl font-bold text-foreground">Portfolio Advisor</h1>
              <p className="text-sm text-muted-foreground">Alocação de carteiras para assessores Nobel Capital</p>
            </div>
            <div className="flex justify-end gap-2">
              <ThemeToggle />
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
        {/* Form */}
        <PortfolioForm onSubmit={handleFormSubmit} loading={loading} />

        {/* Results */}
        {results && currentInput && selectedScenario && (
          <div className="space-y-6">
            {/* Resumo do perfil + botões de export */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 px-1">
              <div>
                <h2 className="text-lg font-bold text-foreground">
                  Perfil <span className="text-primary">{selectedScenario.name}</span>
                </h2>
                <p className="text-sm text-muted-foreground">
                  Retorno esperado: <span className="font-semibold text-success">{selectedScenario.expected_return}</span>
                  {' · '}
                  Volatilidade alvo: <span className="font-semibold">{selectedScenario.target_vol}%</span>
                </p>
              </div>

              <div className="flex gap-2">
                <Button
                  onClick={handleExportProductsList}
                  disabled={exportingPDF || !recommendations.length}
                  variant="outline"
                  size="sm"
                  className="gap-2"
                >
                  <Download className="w-4 h-4" />
                  Lista de Produtos
                </Button>
                <Button
                  onClick={handleExportPDF}
                  disabled={exportingPDF}
                  size="sm"
                  className="gap-2 bg-primary text-primary-foreground hover:bg-primary/90"
                >
                  <Download className="w-4 h-4" />
                  {exportingPDF ? 'Gerando...' : 'Exportar PDF'}
                </Button>
              </div>
            </div>

            <AllocationChart results={results} totalValue={currentInput.valor_captado} />
            <AllocationResults results={results} totalValue={currentInput.valor_captado} scenario={selectedScenario.name} />
          </div>
        )}

        {/* Empty state */}
        {!results && !loading && (
          <div className="text-center py-20">
            <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
              <TrendingUp className="w-8 h-8 text-primary" />
            </div>
            <h3 className="text-lg font-semibold mb-2 text-foreground">Configure sua carteira</h3>
            <p className="text-muted-foreground max-w-sm mx-auto text-sm">
              Selecione o valor e o perfil de investimento para calcular a alocação ideal.
            </p>
          </div>
        )}
      </main>

      <footer className="border-t border-border bg-card mt-16">
        <div className="max-w-7xl mx-auto px-4 py-5">
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <p>© 2026 Nobel Capital · Portfolio Advisor</p>
            <p>Rafael Brandão — Dados & Performance</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;
