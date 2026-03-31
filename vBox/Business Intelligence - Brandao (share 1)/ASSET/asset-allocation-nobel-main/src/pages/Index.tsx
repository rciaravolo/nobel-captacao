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
      <header className="relative border-b border-border/60 bg-card/90 backdrop-blur-sm sticky top-0 z-50">
        <div className="gold-line absolute inset-x-0 bottom-0" />

        <div className="max-w-7xl mx-auto px-4 py-3">
          {/* Mobile */}
          <div className="flex items-center justify-between md:hidden">
            <MobileMenu />
            <div className="flex-1 flex justify-center">
              <img src={nobelLogo} alt="Nobel Capital" className="h-9 w-auto" width="173" height="48" />
            </div>
            <div className="w-10" />
          </div>

          {/* Desktop */}
          <div className="hidden md:grid grid-cols-3 items-center gap-4">
            <div>
              <img src={nobelLogo} alt="Nobel Capital" className="h-11 w-auto" width="173" height="48" />
            </div>
            <div className="text-center space-y-0.5">
              <h1 className="font-serif text-[1.7rem] font-light tracking-wide text-foreground leading-none">
                Portfolio Advisor
              </h1>
              <p className="text-[10px] tracking-[0.22em] uppercase text-muted-foreground font-medium">
                Nobel Capital · Alocação de Carteiras
              </p>
            </div>
            <div className="flex justify-end items-center gap-2">
              <ThemeToggle />
              <Link to="/materiais">
                <Button variant="outline" size="sm" className="gap-1.5 text-xs h-8 px-3">
                  <BarChart3 className="w-3.5 h-3.5" />
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
            <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 px-1 animate-fade-up">
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-[0.22em] text-muted-foreground mb-1">
                  Perfil Selecionado
                </p>
                <h2 className="font-serif text-3xl font-light text-foreground leading-none">
                  {selectedScenario.name}
                </h2>
                <p className="text-sm text-muted-foreground mt-1.5">
                  Retorno esperado: <span className="font-semibold text-success">{selectedScenario.expected_return}</span>
                  {' · '}
                  Volatilidade: <span className="font-semibold">{selectedScenario.target_vol}%</span>
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
          <div className="flex flex-col items-center justify-center py-16 text-center animate-fade-in animate-delay-200">
            <div className="w-px h-12 gold-line mb-8" style={{ background: 'linear-gradient(to bottom, transparent, hsl(42 78% 52% / 0.4))' }} />
            <p className="text-[10px] font-semibold uppercase tracking-[0.25em] text-muted-foreground mb-3">
              Preencha os campos acima
            </p>
            <h3 className="font-serif text-2xl font-light text-foreground mb-2">
              Configure sua carteira
            </h3>
            <p className="text-sm text-muted-foreground max-w-xs leading-relaxed">
              Selecione o perfil e o valor para calcular a alocação ideal e projeção de retornos.
            </p>
            <div className="w-px h-12 mt-8" style={{ background: 'linear-gradient(to bottom, hsl(42 78% 52% / 0.4), transparent)' }} />
          </div>
        )}
      </main>

      <footer className="relative border-t border-border/60 bg-card/60 mt-16">
        <div className="gold-line absolute inset-x-0 top-0" />
        <div className="max-w-7xl mx-auto px-4 py-5">
          <div className="flex items-center justify-between text-[11px] text-muted-foreground">
            <p className="tracking-wide">© 2026 Nobel Capital · Portfolio Advisor</p>
            <p className="tracking-wide">Rafael Brandão — Dados & Performance</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;
