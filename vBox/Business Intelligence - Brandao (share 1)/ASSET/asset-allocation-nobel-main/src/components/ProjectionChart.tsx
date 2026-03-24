import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine, Area, AreaChart, Legend
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ProjectionPoint } from '@/types/portfolio';

interface ProjectionChartProps {
  data: ProjectionPoint[];
  highlightScenario?: string;
}

const SCENARIO_CONFIG: Record<string, { color: string; label: string }> = {
  'Conservadora': { color: '#94A3B8', label: 'Conservadora' },  // cinza azulado
  'Moderada':     { color: '#475569', label: 'Moderada' },       // cinza escuro
  'Sofisticada':  { color: '#C08B20', label: 'Sofisticada' },    // ouro Nobel
};

export const ProjectionChart = ({ data, highlightScenario }: ProjectionChartProps) => {
  const groupedData = data.reduce((acc, point) => {
    if (!acc[point.month]) acc[point.month] = { month: point.month };
    acc[point.month][point.scenario] = point.value;
    return acc;
  }, {} as Record<number, any>);

  const chartData = Object.values(groupedData).sort((a, b) => a.month - b.month);
  const scenarios = [...new Set(data.map(d => d.scenario))];

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);

  const formatYAxis = (value: number) => {
    if (value >= 1_000_000) return `R$ ${(value / 1_000_000).toFixed(1)}M`;
    if (value >= 1_000) return `R$ ${(value / 1_000).toFixed(0)}k`;
    return `R$ ${value}`;
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload?.length) return null;
    return (
      <div className="bg-card border border-border rounded-lg px-4 py-3 shadow-lg text-sm">
        <p className="font-semibold text-foreground mb-2 border-b border-border pb-1">
          Mês {label}
        </p>
        {payload.map((entry: any) => {
          const cfg = SCENARIO_CONFIG[entry.dataKey];
          const isHighlight = entry.dataKey === highlightScenario;
          return (
            <div key={entry.dataKey} className={`flex items-center gap-2 py-0.5 ${isHighlight ? 'font-bold' : ''}`}>
              <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: cfg?.color || entry.color }} />
              <span className="text-muted-foreground w-24">{entry.dataKey}:</span>
              <span style={{ color: cfg?.color || entry.color }}>{formatCurrency(entry.value)}</span>
            </div>
          );
        })}
      </div>
    );
  };

  const CustomLegend = () => (
    <div className="flex justify-center gap-6 pt-2">
      {scenarios.map((scenario) => {
        const cfg = SCENARIO_CONFIG[scenario];
        const isHighlight = scenario === highlightScenario;
        return (
          <div key={scenario} className={`flex items-center gap-2 ${isHighlight ? 'font-bold' : 'opacity-70'}`}>
            <div
              className="h-0.5 w-6 rounded-full"
              style={{ backgroundColor: cfg?.color, height: isHighlight ? 3 : 2 }}
            />
            <span className="text-sm text-foreground">{scenario}</span>
          </div>
        );
      })}
    </div>
  );

  return (
    <Card className="shadow-card">
      <CardHeader className="pb-2">
        <CardTitle className="text-xl text-center">Projeção de Patrimônio — 24 meses</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData} margin={{ top: 8, right: 32, left: 8, bottom: 4 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" strokeOpacity={0.6} />
            <XAxis
              dataKey="month"
              tickFormatter={(v) => `Mês ${v}`}
              tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }}
              tickLine={false}
              interval={2}
            />
            <YAxis
              tickFormatter={formatYAxis}
              tick={{ fontSize: 11, fill: 'hsl(var(--muted-foreground))' }}
              tickLine={false}
              axisLine={false}
              width={80}
            />
            <Tooltip content={<CustomTooltip />} />
            {scenarios.map((scenario) => {
              const cfg = SCENARIO_CONFIG[scenario];
              const isHighlight = scenario === highlightScenario;
              return (
                <Line
                  key={scenario}
                  type="monotone"
                  dataKey={scenario}
                  stroke={cfg?.color || '#888'}
                  strokeWidth={isHighlight ? 3 : 1.5}
                  dot={false}
                  activeDot={{ r: isHighlight ? 5 : 3, strokeWidth: 0 }}
                  strokeOpacity={highlightScenario && !isHighlight ? 0.35 : 1}
                />
              );
            })}
          </LineChart>
        </ResponsiveContainer>
        <CustomLegend />
      </CardContent>
    </Card>
  );
};
