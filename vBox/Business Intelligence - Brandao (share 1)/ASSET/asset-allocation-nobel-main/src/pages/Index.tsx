import { useState, useEffect, useCallback } from 'react';
import { PortfolioForm } from '@/components/PortfolioForm';
import { AllocationResults } from '@/components/AllocationResults';
import { ProjectionChart } from '@/components/ProjectionChart';
import { AllocationInput, AllocationResult, ProjectionPoint } from '@/types/portfolio';
import { AllocationService } from '@/services/allocation';
import { ProjectionService } from '@/services/projection';
import { Link } from 'react-router-dom';
import { BookOpen, TrendingUp, Loader2 } from 'lucide-react';
import nobelLogo from '@/assets/nobel-logo.png';

const Index = () => {
  const [results, setResults] = useState<AllocationResult[] | null>(null);
  const [projections, setProjections] = useState<ProjectionPoint[] | null>(null);
  const [currentInput, setCurrentInput] = useState<AllocationInput | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedScenario, setSelectedScenario] = useState<any>(null);

  const handleFormSubmit = useCallback(async (data: AllocationInput) => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 600));
      const allocationResults = await AllocationService.allocate(data);
      setResults(allocationResults);
      const allProjections = ProjectionService.projectAllScenarios(
        data.valor_captado,
        data.cdi_anual,
        24
      );
      setProjections(allProjections);
      setCurrentInput(data);
    } catch (error) {
      console.error('Erro ao calcular alocação:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const load = async () => {
      if (currentInput) {
        const scenario = await AllocationService.getScenario(currentInput.perfil);
        setSelectedScenario(scenario);
      }
    };
    load();
  }, [currentInput]);

  return (
    <div className="min-h-screen bg-background relative overflow-x-hidden">

      {/* Background subtle radial glow */}
      <div
        className="pointer-events-none fixed inset-0 z-0"
        style={{
          background: 'radial-gradient(ellipse 80% 40% at 50% -10%, hsl(42 78% 52% / 0.07) 0%, transparent 70%)',
        }}
      />

      {/* ── Header ── */}
      <header className="relative z-10 border-b border-border/60">
        <div
          className="absolute inset-0"
          style={{ background: 'hsl(25 8% 7% / 0.95)', backdropFilter: 'blur(12px)' }}
        />
        <div className="relative max-w-6xl mx-auto px-6 py-4 flex items-center justify-between gap-6">

          {/* Logo */}
          <div className="flex items-center gap-3 shrink-0">
            <img src={nobelLogo} alt="Nobel Capital" className="h-9 w-auto opacity-95" />
          </div>

          {/* Title */}
          <div className="text-center flex-1">
            <h1
              className="text-2xl font-medium tracking-tight"
              style={{ fontFamily: "'Cormorant Garamond', serif", color: 'hsl(36 40% 92%)' }}
            >
              Portfolio <span className="gold-shimmer">Advisor</span>
            </h1>
            <p className="text-xs text-muted-foreground mt-0.5 tracking-wide uppercase" style={{ fontSize: '0.65rem', letterSpacing: '0.1em' }}>
              Alocação inteligente · Nobel Capital
            </p>
          </div>

          {/* Nav */}
          <div className="shrink-0">
            <Link
              to="/materiais"
              className="flex items-center gap-2 px-4 py-2 rounded border border-border/80 text-muted-foreground hover:text-primary hover:border-primary/40 transition-all duration-200 text-sm font-medium"
            >
              <BookOpen className="w-3.5 h-3.5" />
              Materiais
            </Link>
          </div>
        </div>
      </header>

      {/* ── Main ── */}
      <main className="relative z-10 max-w-6xl mx-auto px-6 py-10 space-y-10">

        {/* Form */}
        <div className="animate-fade-up">
          <PortfolioForm onSubmit={handleFormSubmit} loading={loading} />
        </div>

        {/* Loading state */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-20 gap-4 animate-fade-in">
            <div className="relative">
              <Loader2
                className="w-8 h-8 animate-spin"
                style={{ color: 'hsl(42 78% 52%)' }}
              />
              <div
                className="absolute inset-0 rounded-full blur-lg opacity-40"
                style={{ background: 'hsl(42 78% 52% / 0.3)' }}
              />
            </div>
            <p className="text-sm text-muted-foreground tracking-wide">Calculando alocação…</p>
          </div>
        )}

        {/* Results */}
        {!loading && results && currentInput && selectedScenario && (
          <div className="space-y-8 animate-fade-up animate-delay-100">

            {/* Scenario banner */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-6 border-b border-border/50">
              <div>
                <p className="label-caps mb-1">Perfil selecionado</p>
                <h2
                  className="text-3xl font-light"
                  style={{ fontFamily: "'Cormorant Garamond', serif", color: 'hsl(36 40% 92%)' }}
                >
                  {selectedScenario.name}
                </h2>
              </div>
              <div className="flex gap-6">
                <div className="text-right">
                  <p className="label-caps mb-1">Retorno esperado</p>
                  <p className="text-base font-medium" style={{ color: 'hsl(42 78% 52%)' }}>
                    {selectedScenario.expected_return}
                  </p>
                </div>
                <div className="text-right">
                  <p className="label-caps mb-1">Volatilidade alvo</p>
                  <p className="text-base font-medium text-foreground">
                    {selectedScenario.target_vol}%
                  </p>
                </div>
              </div>
            </div>

            <AllocationResults
              results={results}
              totalValue={currentInput.valor_captado}
              scenario={selectedScenario.name}
            />

            {projections && (
              <ProjectionChart
                data={projections}
                highlightScenario={selectedScenario.name}
              />
            )}
          </div>
        )}

        {/* Empty state */}
        {!results && !loading && (
          <div className="flex flex-col items-center justify-center py-24 gap-6 animate-fade-in">
            <div
              className="w-16 h-16 rounded-full flex items-center justify-center"
              style={{
                background: 'hsl(42 78% 52% / 0.08)',
                border: '1px solid hsl(42 78% 52% / 0.2)',
                boxShadow: '0 0 30px hsl(42 78% 52% / 0.08)',
              }}
            >
              <TrendingUp className="w-7 h-7" style={{ color: 'hsl(42 78% 52%)' }} />
            </div>
            <div className="text-center space-y-2">
              <h3
                className="text-xl font-light"
                style={{ fontFamily: "'Cormorant Garamond', serif", color: 'hsl(36 40% 92%)' }}
              >
                Configure sua carteira
              </h3>
              <p className="text-sm text-muted-foreground max-w-xs leading-relaxed">
                Selecione o perfil e o valor captado para calcular a alocação ideal e visualizar as projeções.
              </p>
            </div>
          </div>
        )}
      </main>

      {/* ── Footer ── */}
      <footer className="relative z-10 border-t border-border/40 mt-20">
        <div className="max-w-6xl mx-auto px-6 py-5 flex items-center justify-between">
          <p className="text-xs text-muted-foreground">
            © {new Date().getFullYear()} Nobel Capital · Portfolio Advisor
          </p>
          <div className="gold-rule" />
        </div>
      </footer>
    </div>
  );
};

export default Index;
