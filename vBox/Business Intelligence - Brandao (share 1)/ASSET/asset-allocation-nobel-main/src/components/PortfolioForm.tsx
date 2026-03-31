import { useState, useEffect, useRef } from 'react';
import { AllocationInput, Scenario } from '@/types/portfolio';
import { AllocationService } from '@/services/allocation';
import { z } from 'zod';
import { toast } from 'sonner';

const CDI_ANUAL = 0.1315;

const portfolioSchema = z.object({
  valor_captado: z.number()
    .positive({ message: "Valor deve ser positivo" })
    .min(5000, { message: "Valor mínimo: R$ 5.000" })
    .max(50000000, { message: "Valor máximo: R$ 50.000.000" }),
  cdi_anual: z.number()
    .min(0, { message: "CDI não pode ser negativo" })
    .max(1, { message: "CDI deve ser menor que 100%" }),
  perfil: z.string().min(1, { message: "Selecione um perfil" })
});

interface PortfolioFormProps {
  onSubmit: (data: AllocationInput) => void;
  loading?: boolean;
}

const PROFILE_CONFIG: Record<string, { dots: number; color: string; dimColor: string; label: string }> = {
  conservative: {
    dots: 1,
    color: '#34d399',
    dimColor: 'rgba(52,211,153,0.15)',
    label: 'Baixo risco',
  },
  moderate: {
    dots: 2,
    color: '#fbbf24',
    dimColor: 'rgba(251,191,36,0.15)',
    label: 'Médio risco',
  },
  sophisticated: {
    dots: 3,
    color: '#fb7185',
    dimColor: 'rgba(251,113,133,0.15)',
    label: 'Alto risco',
  },
};

export const PortfolioForm = ({ onSubmit, loading }: PortfolioFormProps) => {
  const [formData, setFormData] = useState<AllocationInput>({
    valor_captado: 100000,
    perfil: '',
    cdi_anual: CDI_ANUAL,
  });
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [loadingScenarios, setLoadingScenarios] = useState(true);
  const lastSubmitted = useRef<string>('');

  useEffect(() => {
    const loadScenarios = async () => {
      try {
        const scenariosData = await AllocationService.getAllScenarios();
        setScenarios(scenariosData);
      } catch (error) {
        console.error('Error loading scenarios:', error);
      } finally {
        setLoadingScenarios(false);
      }
    };
    loadScenarios();
  }, []);

  useEffect(() => {
    if (loadingScenarios) return;
    if (formData.valor_captado <= 0 || !formData.perfil) return;
    const key = `${formData.valor_captado}-${formData.perfil}-${formData.cdi_anual}`;
    if (key === lastSubmitted.current) return;
    const validation = portfolioSchema.safeParse(formData);
    if (validation.success) {
      lastSubmitted.current = key;
      onSubmit(formData);
    } else {
      toast.error(validation.error.errors[0].message);
    }
  }, [formData, onSubmit, loadingScenarios]);

  const formatCurrency = (value: string) => {
    const numericValue = value.replace(/\D/g, '');
    return Number(numericValue).toLocaleString('pt-BR');
  };

  const handleValueChange = (value: string) => {
    const numericValue = Number(value.replace(/\D/g, ''));
    const valueValidation = z.number()
      .positive({ message: "Valor deve ser positivo" })
      .min(5000, { message: "Valor mínimo: R$ 5.000" })
      .max(50000000, { message: "Valor máximo: R$ 50.000.000" })
      .safeParse(numericValue);
    if (!valueValidation.success && numericValue > 0) {
      toast.error(valueValidation.error.errors[0].message);
    }
    setFormData(prev => ({ ...prev, valor_captado: numericValue }));
  };

  return (
    <div className="vault-card w-full max-w-2xl mx-auto p-6 md:p-8 animate-fade-up">
      <div className="space-y-8">

        {/* ── Valor Captado ── */}
        <div className="space-y-3">
          <p className="text-[10px] font-semibold uppercase tracking-[0.22em] text-muted-foreground">
            Valor Captado
          </p>
          <div className="border-b-2 border-border focus-within:border-primary transition-colors duration-200 pb-2">
            <div className="flex items-baseline gap-2">
              <span className="text-muted-foreground font-medium text-base flex-shrink-0 leading-none">R$</span>
              <input
                type="text"
                inputMode="numeric"
                value={formatCurrency(formData.valor_captado.toString())}
                onChange={e => handleValueChange(e.target.value)}
                placeholder="100.000"
                className="flex-1 bg-transparent border-0 outline-none text-right text-2xl sm:text-[2rem] font-light tabular-nums text-foreground placeholder:text-muted-foreground/30 font-sans min-w-0"
              />
            </div>
            <p className="text-[10px] text-muted-foreground/60 text-right mt-1 pr-0.5">
              mín R$ 5.000 · máx R$ 50.000.000
            </p>
          </div>
        </div>

        {/* ── Perfil de Investimento ── */}
        <div className="space-y-3">
          <p className="text-[10px] font-semibold uppercase tracking-[0.22em] text-muted-foreground">
            Perfil de Investimento
          </p>

          {loadingScenarios ? (
            <div className="grid grid-cols-3 gap-3">
              {[1, 2, 3].map(i => (
                <div key={i} className="h-[88px] rounded-lg bg-muted/30 animate-pulse" />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {scenarios.map(scenario => {
                const cfg = PROFILE_CONFIG[scenario.id] || PROFILE_CONFIG.moderate;
                const isSelected = formData.perfil === scenario.id;

                return (
                  <button
                    key={scenario.id}
                    type="button"
                    onClick={() => setFormData(prev => ({ ...prev, perfil: scenario.id }))}
                    className="relative p-4 rounded-lg border text-left transition-all duration-200 cursor-pointer group"
                    style={{
                      borderColor: isSelected ? cfg.color + '55' : 'hsl(var(--border))',
                      background: isSelected ? cfg.dimColor : 'hsl(var(--card))',
                    }}
                  >
                    {/* Gold top accent when selected */}
                    {isSelected && (
                      <div
                        className="absolute inset-x-0 top-0 h-px rounded-t-lg"
                        style={{
                          background: `linear-gradient(90deg, transparent, ${cfg.color}99, transparent)`,
                        }}
                      />
                    )}

                    <div className="space-y-2">
                      <p className="font-serif text-[1.05rem] font-medium text-foreground leading-none">
                        {scenario.name}
                      </p>
                      <p className="text-[11px] font-semibold" style={{ color: cfg.color }}>
                        {scenario.expected_return}
                      </p>
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] text-muted-foreground">{cfg.label}</span>
                        <div className="flex gap-1">
                          {[1, 2, 3].map(i => (
                            <div
                              key={i}
                              className="w-1.5 h-1.5 rounded-full transition-all duration-200"
                              style={{
                                background: i <= cfg.dots ? cfg.color : 'hsl(var(--border))',
                                boxShadow: i <= cfg.dots && isSelected ? `0 0 4px ${cfg.color}` : 'none',
                              }}
                            />
                          ))}
                        </div>
                      </div>
                    </div>
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
