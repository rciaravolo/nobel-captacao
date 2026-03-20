import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine,
} from 'recharts';
import { ProjectionPoint } from '@/types/portfolio';

interface ProjectionChartProps {
  data: ProjectionPoint[];
  highlightScenario?: string;
}

const SCENARIO_STYLES: Record<string, { color: string; dash?: string }> = {
  'Conservadora': { color: 'hsl(152 45% 48%)',  dash: undefined },
  'Moderada':     { color: 'hsl(42 78% 52%)',   dash: undefined },
  'Sofisticada':  { color: 'hsl(4 68% 58%)',    dash: undefined },
};

const fmt = (v: number) =>
  new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    notation: v >= 1_000_000 ? 'compact' : 'standard',
    maximumFractionDigits: v >= 1_000_000 ? 1 : 0,
  }).format(v);

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div
      className="rounded-lg px-4 py-3 text-sm space-y-1.5"
      style={{
        background: 'hsl(25 8% 11%)',
        border: '1px solid hsl(42 78% 52% / 0.2)',
        boxShadow: '0 8px 30px hsl(0 0% 0% / 0.5)',
      }}
    >
      <p className="label-caps mb-2">Mês {label}</p>
      {payload.map((entry: any) => (
        <div key={entry.dataKey} className="flex items-center gap-2.5">
          <span
            className="w-2 h-2 rounded-full shrink-0"
            style={{ background: entry.color, boxShadow: `0 0 6px ${entry.color}80` }}
          />
          <span className="text-muted-foreground text-xs">{entry.dataKey}:</span>
          <span className="font-medium text-foreground tabular-nums ml-auto pl-4">{fmt(entry.value)}</span>
        </div>
      ))}
    </div>
  );
};

export const ProjectionChart = ({ data, highlightScenario }: ProjectionChartProps) => {
  const grouped = data.reduce((acc, point) => {
    if (!acc[point.month]) acc[point.month] = { month: point.month };
    acc[point.month][point.scenario] = point.value;
    return acc;
  }, {} as Record<number, any>);

  const chartData = Object.values(grouped).sort((a, b) => a.month - b.month);
  const scenarios = [...new Set(data.map(d => d.scenario))];

  return (
    <div className="vault-card rounded-lg overflow-hidden animate-fade-up animate-delay-300">
      {/* Header */}
      <div className="px-8 py-6 border-b border-border/50 flex items-center justify-between">
        <div>
          <p className="label-caps mb-1">Simulação · 24 meses</p>
          <h3
            className="text-xl font-light"
            style={{ fontFamily: "'Cormorant Garamond', serif", color: 'hsl(36 40% 92%)' }}
          >
            Projeção de Retornos
          </h3>
        </div>
        {/* Legend */}
        <div className="flex items-center gap-5">
          {scenarios.map(s => {
            const style = SCENARIO_STYLES[s] ?? { color: '#888' };
            const isHL = highlightScenario === s;
            return (
              <div key={s} className="flex items-center gap-1.5" style={{ opacity: isHL ? 1 : 0.55 }}>
                <span
                  className="w-3 h-0.5 rounded-full"
                  style={{ background: style.color, boxShadow: isHL ? `0 0 8px ${style.color}` : 'none' }}
                />
                <span className="text-xs text-muted-foreground">{s}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Chart */}
      <div className="px-4 py-6">
        <ResponsiveContainer width="100%" height={320}>
          <LineChart data={chartData} margin={{ top: 10, right: 24, left: 8, bottom: 4 }}>
            <defs>
              {scenarios.map(s => {
                const col = SCENARIO_STYLES[s]?.color ?? '#888';
                return (
                  <linearGradient key={s} id={`grad-${s}`} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor={col} stopOpacity={0.15} />
                    <stop offset="100%" stopColor={col} stopOpacity={0} />
                  </linearGradient>
                );
              })}
            </defs>

            <CartesianGrid
              strokeDasharray="2 4"
              stroke="hsl(36 12% 18%)"
              vertical={false}
            />

            <XAxis
              dataKey="month"
              tickFormatter={v => `M${v}`}
              tick={{ fill: 'hsl(36 12% 40%)', fontSize: 11, fontFamily: 'Outfit' }}
              axisLine={false}
              tickLine={false}
              interval={5}
            />

            <YAxis
              tickFormatter={v => fmt(v)}
              tick={{ fill: 'hsl(36 12% 40%)', fontSize: 11, fontFamily: 'Outfit' }}
              axisLine={false}
              tickLine={false}
              width={85}
            />

            <Tooltip content={<CustomTooltip />} cursor={{ stroke: 'hsl(42 78% 52% / 0.15)', strokeWidth: 1 }} />

            {scenarios.map(s => {
              const style = SCENARIO_STYLES[s] ?? { color: '#888' };
              const isHL = highlightScenario === s;
              return (
                <Line
                  key={s}
                  type="monotone"
                  dataKey={s}
                  stroke={style.color}
                  strokeWidth={isHL ? 2.5 : 1.5}
                  dot={false}
                  activeDot={{
                    r: 4,
                    fill: style.color,
                    stroke: 'hsl(25 8% 9%)',
                    strokeWidth: 2,
                  }}
                  strokeOpacity={isHL ? 1 : 0.45}
                  strokeDasharray={(!isHL && highlightScenario) ? '4 3' : undefined}
                />
              );
            })}

            <ReferenceLine x={12} stroke="hsl(42 78% 52% / 0.12)" strokeDasharray="2 4" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
