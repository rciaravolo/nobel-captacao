import { ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, Cell } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AllocationResult } from '@/types/portfolio';
import { useIsMobile } from '@/hooks/use-mobile';

interface AllocationChartProps {
  results: AllocationResult[];
  totalValue: number;
}

// Colors per subclass/class — ordered from gold (RF) → blue (Ações) → teal (Imob) → amber (Comm) → lavender (Cripto)
const ASSET_COLORS: Record<string, string> = {
  'Renda Fixa Pós-fixada': 'hsl(42 78% 52%)',
  'Renda Fixa Pré-fixada': 'hsl(42 65% 62%)',
  'Renda Fixa Inflação':   'hsl(42 50% 70%)',
  'Renda Fixa':            'hsl(42 78% 52%)',
  'Ações Brasil':          'hsl(213 65% 58%)',
  'Ações Internacional':   'hsl(213 80% 68%)',
  'Ações':                 'hsl(213 65% 58%)',
  'REITs':                 'hsl(168 52% 50%)',
  'Imobiliário':           'hsl(168 52% 50%)',
  'Commodities':           'hsl(28 78% 58%)',
  'Criptomoedas':          'hsl(258 48% 66%)',
};

const getBarColor = (item: { displayName: string; classe: string }) =>
  ASSET_COLORS[item.displayName] || ASSET_COLORS[item.classe] || 'hsl(42 78% 52%)';

export const AllocationChart = ({ results, totalValue }: AllocationChartProps) => {
  const isMobile = useIsMobile();

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
      notation: value > 1000000 ? 'compact' : 'standard',
    }).format(value);

  const chartData = results
    .filter(item => item.percentage > 0)
    .map(item => ({
      ...item,
      displayName: item.subclass === '-' ? item.classe : item.subclass,
    }))
    .sort((a, b) => b.value - a.value);

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const color = getBarColor(data);
      return (
        <div className="bg-card border border-border rounded-lg px-3.5 py-2.5 shadow-elevated">
          <div className="flex items-center gap-2 mb-1">
            <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: color }} />
            <p className="font-medium text-foreground text-sm leading-none">{data.displayName}</p>
          </div>
          <p className="text-xs text-muted-foreground pl-4">
            {formatCurrency(data.value)}
            <span className="ml-2 text-foreground font-semibold">
              {data.percentage.toFixed(1)}%
            </span>
          </p>
        </div>
      );
    }
    return null;
  };

  const mobileChartHeight = Math.max(300, chartData.length * 42);

  return (
    <Card className="shadow-card" data-chart-container>
      <CardHeader className="pb-2 md:pb-4">
        <CardTitle className="font-serif text-xl font-light text-foreground text-center tracking-wide">
          Visualização da Alocação
        </CardTitle>
      </CardHeader>
      <CardContent className="px-2 md:px-6">
        <div style={{ height: isMobile ? mobileChartHeight : 340 }} className="mt-2">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              layout={isMobile ? 'vertical' : 'horizontal'}
              margin={isMobile
                ? { top: 5, right: 55, left: 10, bottom: 5 }
                : { top: 16, right: 10, left: 5, bottom: 58 }
              }
            >
              {isMobile ? (
                <>
                  <XAxis type="number" tick={false} axisLine={false} tickLine={false} />
                  <YAxis
                    type="category"
                    dataKey="displayName"
                    width={105}
                    fontSize={10}
                    tick={{ fill: 'hsl(var(--foreground))', fontFamily: 'Outfit, sans-serif' }}
                    tickLine={false}
                    axisLine={false}
                  />
                </>
              ) : (
                <>
                  <XAxis
                    dataKey="displayName"
                    angle={-40}
                    textAnchor="end"
                    height={58}
                    fontSize={10}
                    tick={{ fill: 'hsl(var(--muted-foreground))', fontFamily: 'Outfit, sans-serif' }}
                    interval={0}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis tick={false} axisLine={false} tickLine={false} width={5} />
                </>
              )}
              <Tooltip content={<CustomTooltip />} cursor={{ fill: 'hsl(var(--muted) / 0.4)' }} />
              <Bar
                dataKey="value"
                name="Volume (R$)"
                radius={isMobile ? [0, 3, 3, 0] : [3, 3, 0, 0]}
                label={{
                  position: isMobile ? 'right' : 'top',
                  formatter: formatCurrency,
                  style: {
                    fill: 'hsl(var(--muted-foreground))',
                    fontSize: '9px',
                    fontFamily: 'Outfit, sans-serif',
                    fontWeight: 500,
                  },
                }}
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getBarColor(entry)} opacity={0.88} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
};
