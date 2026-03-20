import { AllocationResult } from '@/types/portfolio';

interface AllocationResultsProps {
  results: AllocationResult[];
  totalValue: number;
  scenario: string;
}

const classColors: Record<string, string> = {
  'Renda Fixa':    'hsl(42 78% 52%)',
  'Ações':         'hsl(152 45% 42%)',
  'Imobiliário':   'hsl(200 70% 52%)',
  'Commodities':   'hsl(30 85% 52%)',
  'Criptomoedas':  'hsl(260 70% 62%)',
};

const formatCurrency = (value: number) =>
  new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 2,
  }).format(value);

export const AllocationResults = ({ results, totalValue, scenario }: AllocationResultsProps) => {
  const activeResults = results.filter(r => r.percentage > 0);
  const zeroResults   = results.filter(r => r.percentage === 0);

  return (
    <div className="vault-card rounded-lg overflow-hidden animate-fade-up animate-delay-200">
      {/* Header */}
      <div className="px-8 py-6 border-b border-border/50 flex items-center justify-between">
        <div>
          <p className="label-caps mb-1">Resultado</p>
          <h3
            className="text-xl font-light"
            style={{ fontFamily: "'Cormorant Garamond', serif", color: 'hsl(36 40% 92%)' }}
          >
            Alocação de Portfólio
          </h3>
        </div>
        <div
          className="px-3 py-1 rounded text-xs font-medium tracking-wide uppercase"
          style={{
            background: 'hsl(42 78% 52% / 0.1)',
            border: '1px solid hsl(42 78% 52% / 0.25)',
            color: 'hsl(42 78% 52%)',
          }}
        >
          {scenario}
        </div>
      </div>

      {/* Table */}
      <div className="px-8 py-2">
        {/* Column headers */}
        <div className="grid grid-cols-12 gap-4 py-3 border-b border-border/30">
          <span className="col-span-4 label-caps">Classe</span>
          <span className="col-span-4 label-caps">Subclasse</span>
          <span className="col-span-2 label-caps text-right">%</span>
          <span className="col-span-2 label-caps text-right">Valor</span>
        </div>

        {/* Active rows */}
        {activeResults.map((result, i) => {
          const color = classColors[result.classe] ?? 'hsl(42 78% 52%)';
          const barWidth = Math.min(result.percentage, 100);

          return (
            <div
              key={i}
              className="group grid grid-cols-12 gap-4 py-4 border-b border-border/20 last:border-b-0 hover:bg-white/[0.02] transition-colors duration-150"
            >
              {/* Classe com dot */}
              <div className="col-span-4 flex items-center gap-2.5">
                <span
                  className="w-2 h-2 rounded-full shrink-0"
                  style={{ background: color, boxShadow: `0 0 6px ${color}60` }}
                />
                <span className="text-sm font-medium text-foreground truncate">{result.classe}</span>
              </div>

              {/* Subclasse */}
              <div className="col-span-4 flex items-center">
                <span className="text-sm text-muted-foreground truncate">{result.subclass}</span>
              </div>

              {/* Percentual + barra */}
              <div className="col-span-2 flex flex-col items-end justify-center gap-1">
                <span
                  className="text-sm font-semibold tabular-nums"
                  style={{ color }}
                >
                  {result.percentage.toFixed(1)}%
                </span>
                <div className="w-full h-0.5 rounded-full overflow-hidden bg-white/5">
                  <div
                    className="h-full rounded-full transition-all duration-700"
                    style={{ width: `${barWidth}%`, background: color, opacity: 0.7 }}
                  />
                </div>
              </div>

              {/* Valor */}
              <div className="col-span-2 flex items-center justify-end">
                <span className="text-sm font-medium text-foreground tabular-nums">
                  {formatCurrency(result.value)}
                </span>
              </div>
            </div>
          );
        })}

        {/* Zero rows — subdued */}
        {zeroResults.map((result, i) => (
          <div
            key={`zero-${i}`}
            className="grid grid-cols-12 gap-4 py-3 border-b border-border/10 last:border-b-0 opacity-30"
          >
            <div className="col-span-4 flex items-center gap-2.5">
              <span className="w-2 h-2 rounded-full shrink-0 bg-muted-foreground/40" />
              <span className="text-sm text-muted-foreground truncate">{result.classe}</span>
            </div>
            <div className="col-span-4 flex items-center">
              <span className="text-xs text-muted-foreground truncate">{result.subclass}</span>
            </div>
            <div className="col-span-2 text-right">
              <span className="text-xs text-muted-foreground">—</span>
            </div>
            <div className="col-span-2 text-right">
              <span className="text-xs text-muted-foreground">—</span>
            </div>
          </div>
        ))}
      </div>

      {/* Total */}
      <div
        className="px-8 py-5 flex items-center justify-between"
        style={{
          background: 'hsl(42 78% 52% / 0.04)',
          borderTop: '1px solid hsl(42 78% 52% / 0.15)',
        }}
      >
        <div className="flex items-center gap-3">
          <span className="label-caps">Total alocado</span>
        </div>
        <div className="flex items-center gap-8">
          <span
            className="text-sm font-semibold"
            style={{ color: 'hsl(42 78% 52%)' }}
          >
            100,0%
          </span>
          <span
            className="text-lg font-semibold"
            style={{
              fontFamily: "'Cormorant Garamond', serif",
              color: 'hsl(42 78% 52%)',
              letterSpacing: '-0.01em',
            }}
          >
            {formatCurrency(totalValue)}
          </span>
        </div>
      </div>
    </div>
  );
};
