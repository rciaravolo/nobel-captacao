import { useState, useEffect } from 'react';
import { AllocationInput, Scenario } from '@/types/portfolio';
import { AllocationService } from '@/services/allocation';

interface PortfolioFormProps {
  onSubmit: (data: AllocationInput) => void;
  loading?: boolean;
}

const profileColors: Record<string, { border: string; glow: string; label: string }> = {
  conservative: {
    border: 'hsl(152 45% 42%)',
    glow:   'hsl(152 45% 42% / 0.15)',
    label:  'Baixo risco',
  },
  moderate: {
    border: 'hsl(42 78% 52%)',
    glow:   'hsl(42 78% 52% / 0.15)',
    label:  'Risco moderado',
  },
  sophisticated: {
    border: 'hsl(4 68% 52%)',
    glow:   'hsl(4 68% 52% / 0.15)',
    label:  'Alto risco',
  },
};

export const PortfolioForm = ({ onSubmit, loading }: PortfolioFormProps) => {
  const [formData, setFormData] = useState<AllocationInput>({
    valor_captado: 1000000,
    perfil: 'conservative',
    cdi_anual: 0.1075,
  });
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [loadingScenarios, setLoadingScenarios] = useState(true);
  const [rawValue, setRawValue] = useState('1.000.000');

  useEffect(() => {
    AllocationService.getAllScenarios()
      .then(setScenarios)
      .catch(console.error)
      .finally(() => setLoadingScenarios(false));
  }, []);

  useEffect(() => {
    if (formData.valor_captado > 0 && formData.perfil && !loading && !loadingScenarios) {
      onSubmit(formData);
    }
  }, [formData, onSubmit, loading, loadingScenarios]);

  const handleValueChange = (raw: string) => {
    const digits = raw.replace(/\D/g, '');
    const num = Number(digits);
    setRawValue(num.toLocaleString('pt-BR'));
    setFormData(prev => ({ ...prev, valor_captado: num }));
  };

  return (
    <div
      className="vault-card rounded-lg p-8 max-w-2xl mx-auto animate-fade-up"
      style={{ background: 'hsl(25 8% 9%)' }}
    >
      {/* Header */}
      <div className="mb-8">
        <p className="label-caps mb-2">Parâmetros</p>
        <h2
          className="text-2xl font-light"
          style={{ fontFamily: "'Cormorant Garamond', serif", color: 'hsl(36 40% 92%)' }}
        >
          Alocação de Carteira
        </h2>
        <div className="gold-rule mt-3" />
      </div>

      <div className="space-y-8">
        {/* Valor Captado */}
        <div className="space-y-2">
          <label className="label-caps block">Valor Captado (R$)</label>
          <div className="relative">
            <span
              className="absolute left-4 top-1/2 -translate-y-1/2 text-sm font-medium pointer-events-none"
              style={{ color: 'hsl(42 78% 52%)' }}
            >
              R$
            </span>
            <input
              type="text"
              value={rawValue}
              onChange={e => handleValueChange(e.target.value)}
              className="w-full pl-10 pr-4 py-3.5 rounded bg-transparent text-right text-lg font-medium tracking-wide transition-all duration-200 outline-none"
              style={{
                border: '1px solid hsl(var(--border))',
                color: 'hsl(36 40% 92%)',
                fontFamily: "'Cormorant Garamond', serif",
              }}
              onFocus={e => (e.currentTarget.style.borderColor = 'hsl(42 78% 52% / 0.6)')}
              onBlur={e => (e.currentTarget.style.borderColor = 'hsl(var(--border))')}
            />
          </div>
        </div>

        {/* Perfil */}
        <div className="space-y-3">
          <label className="label-caps block">Perfil de Investimento</label>

          {loadingScenarios ? (
            <div className="flex gap-3">
              {[0, 1, 2].map(i => (
                <div
                  key={i}
                  className="flex-1 h-24 rounded animate-pulse"
                  style={{ background: 'hsl(25 6% 12%)' }}
                />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-3 gap-3">
              {scenarios.map(scenario => {
                const colors = profileColors[scenario.id] ?? {
                  border: 'hsl(42 78% 52%)',
                  glow:   'hsl(42 78% 52% / 0.15)',
                  label:  '',
                };
                const isActive = formData.perfil === scenario.id;

                return (
                  <button
                    key={scenario.id}
                    type="button"
                    onClick={() => setFormData(prev => ({ ...prev, perfil: scenario.id }))}
                    className="relative flex flex-col items-center justify-center gap-1.5 py-5 px-3 rounded transition-all duration-200 text-center group"
                    style={{
                      border: `1px solid ${isActive ? colors.border : 'hsl(var(--border))'}`,
                      background: isActive ? colors.glow : 'transparent',
                      boxShadow: isActive ? `0 0 20px ${colors.glow}` : 'none',
                    }}
                    onMouseEnter={e => {
                      if (!isActive) {
                        e.currentTarget.style.borderColor = `${colors.border}80`;
                        e.currentTarget.style.background = `${colors.glow.replace('0.15', '0.06')}`;
                      }
                    }}
                    onMouseLeave={e => {
                      if (!isActive) {
                        e.currentTarget.style.borderColor = 'hsl(var(--border))';
                        e.currentTarget.style.background = 'transparent';
                      }
                    }}
                  >
                    <span
                      className="text-base font-medium"
                      style={{
                        fontFamily: "'Cormorant Garamond', serif",
                        color: isActive ? colors.border : 'hsl(36 40% 92%)',
                        transition: 'color 0.2s',
                      }}
                    >
                      {scenario.name}
                    </span>
                    <span className="label-caps" style={{ color: isActive ? colors.border : undefined, opacity: isActive ? 0.8 : 1 }}>
                      {colors.label}
                    </span>
                    <span
                      className="text-xs mt-0.5"
                      style={{ color: isActive ? colors.border : 'hsl(var(--muted-foreground))', fontWeight: 500 }}
                    >
                      {scenario.expected_return}
                    </span>
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
