import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ProjectionPoint } from '@/types/portfolio';
interface ProjectionChartProps {
  data: ProjectionPoint[];
  highlightScenario?: string;
}
export const ProjectionChart = ({
  data,
  highlightScenario
}: ProjectionChartProps) => {
  // Group data by month and create combined data points
  const groupedData = data.reduce((acc, point) => {
    if (!acc[point.month]) {
      acc[point.month] = {
        month: point.month
      };
    }
    acc[point.month][point.scenario] = point.value;
    return acc;
  }, {} as Record<number, any>);
  const chartData = Object.values(groupedData).sort((a, b) => a.month - b.month);
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
      notation: value > 1000000 ? 'compact' : 'standard'
    }).format(value);
  };
  const CustomTooltip = ({
    active,
    payload,
    label
  }: any) => {
    if (active && payload && payload.length) {
      return <div className="bg-card border border-border rounded-lg p-3 shadow-elevated">
          <p className="font-medium text-foreground mb-2">Mês {label}</p>
          {payload.map((entry: any, index: number) => <p key={index} className="text-sm" style={{
          color: entry.color
        }}>
              <span className="font-medium">{entry.dataKey}:</span>{' '}
              {formatCurrency(entry.value)}
            </p>)}
        </div>;
    }
    return null;
  };
  const scenarios = [...new Set(data.map(d => d.scenario))];
  const colors = {
    'Conservadora': '#16a34a',
    'Moderada': '#2563eb',
    'Sofisticada': '#dc2626'
  };
  return <Card className="shadow-card">
      <CardHeader>
        <CardTitle className="text-2xl">Projeção de Retornos</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={chartData} margin={{ top: 10, right: 30, left: 20, bottom: 10 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis
              dataKey="month"
              tickFormatter={(v) => `M${v}`}
              stroke="hsl(var(--muted-foreground))"
            />
            <YAxis
              tickFormatter={formatCurrency}
              width={90}
              stroke="hsl(var(--muted-foreground))"
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            {scenarios.map((scenario) => (
              <Line
                key={scenario}
                type="monotone"
                dataKey={scenario}
                stroke={colors[scenario as keyof typeof colors] ?? '#888'}
                strokeWidth={highlightScenario === scenario ? 3 : 1.5}
                dot={false}
                strokeDasharray={highlightScenario && highlightScenario !== scenario ? '4 2' : undefined}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>;
};