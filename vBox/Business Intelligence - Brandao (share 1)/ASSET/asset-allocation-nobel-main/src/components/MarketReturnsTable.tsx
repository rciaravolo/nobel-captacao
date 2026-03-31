import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { MarketReturn } from '@/types/portfolio';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface MarketReturnsTableProps {
  data: MarketReturn[];
}

export const MarketReturnsTable = ({ data }: MarketReturnsTableProps) => {
  const formatPercentage = (value: number) => {
    const formatted = value.toFixed(2);
    const isPositive = value >= 0;
    
    return (
      <span className={`inline-flex items-center gap-1 font-semibold ${
        isPositive ? 'text-success' : 'text-destructive'
      }`}>
        {isPositive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
        {formatted}%
      </span>
    );
  };

  const getClasseBadgeColor = (classe: string) => {
    const colors: Record<string, string> = {
      'Renda Fixa': 'bg-primary/10 text-primary',
      'Ações': 'bg-success/10 text-success',
      'Imobiliário': 'bg-yellow-500/10 text-yellow-600',
      'Commodities': 'bg-orange-500/10 text-orange-600',
      'Moedas': 'bg-purple-500/10 text-purple-600'
    };
    return colors[classe] || 'bg-muted text-muted-foreground';
  };

  return (
    <Card className="shadow-card">
      <CardHeader>
        <CardTitle className="text-xl">Retornos dos Mercados</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-3 px-2 font-medium text-muted-foreground">Classe</th>
                <th className="text-left py-3 px-2 font-medium text-muted-foreground">Índice</th>
                <th className="text-right py-3 px-2 font-medium text-muted-foreground">Mês Atual</th>
                <th className="text-right py-3 px-2 font-medium text-muted-foreground">No Ano</th>
                <th className="text-right py-3 px-2 font-medium text-muted-foreground">12 Meses</th>
                <th className="text-right py-3 px-2 font-medium text-muted-foreground">36 Meses</th>
                <th className="text-right py-3 px-2 font-medium text-muted-foreground">60 Meses</th>
              </tr>
            </thead>
            <tbody>
              {data.map((row, index) => (
                <tr key={index} className="border-b border-border/50 hover:bg-muted/20 transition-colors">
                  <td className="py-3 px-2">
                    <Badge className={getClasseBadgeColor(row.classe)}>
                      {row.classe}
                    </Badge>
                  </td>
                  <td className="py-3 px-2 font-medium text-foreground">{row.indice}</td>
                  <td className="py-3 px-2 text-right">{formatPercentage(row.mes_atual)}</td>
                  <td className="py-3 px-2 text-right">{formatPercentage(row.no_ano)}</td>
                  <td className="py-3 px-2 text-right">{formatPercentage(row.em_12m)}</td>
                  <td className="py-3 px-2 text-right">{formatPercentage(row.em_36m)}</td>
                  <td className="py-3 px-2 text-right">{formatPercentage(row.em_60m)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
};