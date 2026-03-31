import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AllocationResult } from '@/types/portfolio';
import { useEffect, useState } from 'react';
import { RecommendationsService, RecommendedProduct } from '@/services/recommendations';
import { SupabaseAllocationService } from '@/services/supabase-allocation';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { useIsMobile } from '@/hooks/use-mobile';

interface AllocationResultsProps {
  results: AllocationResult[];
  totalValue: number;
  scenario: string;
}

export const AllocationResults = ({ results, totalValue, scenario }: AllocationResultsProps) => {
  const isMobile = useIsMobile();
  const [recommendations, setRecommendations] = useState<Record<string, RecommendedProduct[]>>({});
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set());

  const maxPercentage = Math.max(...results.map(r => r.percentage));

  useEffect(() => {
    const load = async () => {
      const profileMap: Record<string, string> = {
        'Conservadora': 'conservative',
        'Moderada': 'moderate',
        'Sofisticada': 'sophisticated'
      };
      const profile = profileMap[scenario] || 'moderate';
      const monthYear = await SupabaseAllocationService.getCurrentMonth();
      const map: Record<string, RecommendedProduct[]> = {};

      for (const result of results) {
        const key = `${result.classe}-${result.subclass}`;
        const recs = await RecommendationsService.getRecommendationsForAllocation(
          profile, result.classe, result.subclass, monthYear
        );
        if (recs.length > 0) map[key] = recs;
      }
      setRecommendations(map);
    };
    load();
  }, [results, scenario]);

  const toggleRow = (i: number) => {
    const next = new Set(expandedRows);
    next.has(i) ? next.delete(i) : next.add(i);
    setExpandedRows(next);
  };

  const fmt = (v: number) =>
    new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', minimumFractionDigits: 2 }).format(v);

  const fmtCompact = (v: number) =>
    new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(v);

  const label = (r: AllocationResult) =>
    r.subclass && r.subclass !== '-' ? r.subclass : r.classe;

  return (
    <Card className="shadow-card overflow-hidden">
      <CardHeader className="pb-4 border-b border-border">
        <div className="flex flex-col items-center gap-2">
          <CardTitle className="text-xl font-semibold tracking-tight text-foreground">
            Alocação de Portfólio
          </CardTitle>
          <span className="text-xs uppercase tracking-widest text-muted-foreground font-medium">
            Perfil {scenario}
          </span>
        </div>
      </CardHeader>

      <CardContent className="px-0 pb-0">

        {/* Column headers */}
        <div className="grid grid-cols-[1fr_120px] px-6 py-2.5 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground border-b border-border/60">
          <span>Classe de Ativo</span>
          <span className="text-right">Alocação</span>
        </div>

        {/* Rows */}
        <div className="divide-y divide-border/40">
          {results.map((result, index) => {
            const key = `${result.classe}-${result.subclass}`;
            const hasRecs = recommendations[key]?.length > 0;
            const isExpanded = expandedRows.has(index);
            const barPct = (result.percentage / maxPercentage) * 100;

            return (
              <div key={index}>
                <div
                  className={`group grid grid-cols-[1fr_120px] items-center gap-4 px-6 py-4 hover:bg-muted/25 transition-colors ${hasRecs ? 'cursor-pointer' : ''}`}
                  onClick={hasRecs ? () => toggleRow(index) : undefined}
                >

                  {/* Left: name + bar */}
                  <div className="flex flex-col gap-2 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-[14px] text-foreground leading-none">
                        {label(result)}
                      </span>
                      {result.subclass && result.subclass !== '-' && (
                        <span className="text-[11px] text-muted-foreground hidden sm:inline">
                          {result.classe}
                        </span>
                      )}
                      {hasRecs && (
                        <span className="flex items-center gap-0.5 text-[11px] text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity">
                          {isExpanded
                            ? <ChevronUp className="h-3.5 w-3.5" />
                            : <ChevronDown className="h-3.5 w-3.5" />}
                          <span className="hidden sm:inline">
                            {isExpanded ? 'fechar' : `${recommendations[key].length} produtos`}
                          </span>
                        </span>
                      )}
                    </div>

                    {/* Bar */}
                    <div className="h-[5px] bg-border/60 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all duration-700 ease-out bg-foreground/70"
                        style={{ width: `${barPct}%` }}
                      />
                    </div>
                  </div>

                  {/* Right: % + value */}
                  <div className="flex flex-col items-end gap-0.5">
                    <span className="text-[22px] font-bold tabular-nums text-foreground leading-none">
                      {result.percentage.toFixed(1).replace('.', ',')}%
                    </span>
                    <span className="text-[12px] text-muted-foreground tabular-nums">
                      {isMobile ? fmtCompact(result.value) : fmt(result.value)}
                    </span>
                  </div>
                </div>

                {/* Expanded products */}
                {hasRecs && isExpanded && (
                  <div className="px-6 py-3 bg-muted/30 border-t border-border/40">
                    <p className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground mb-2">
                      Produtos recomendados
                    </p>
                    <div className="space-y-1.5">
                      {recommendations[key].map((p, i) => (
                        <div
                          key={i}
                          className="flex items-center justify-between gap-3 bg-card rounded px-3 py-2 border border-border/50 text-sm"
                        >
                          <span className="font-medium text-foreground">{p.product_name}</span>
                          <div className="flex items-center gap-2 flex-shrink-0">
                            {p.percentage && (
                              <span className="font-semibold tabular-nums text-foreground">
                                {p.percentage.toFixed(1)}%
                              </span>
                            )}
                            {p.expected_return && (
                              <Badge variant="outline" className="text-[10px] px-1.5 py-0 border-border text-muted-foreground">
                                {p.expected_return}
                              </Badge>
                            )}
                            {p.eligibility && (
                              <Badge variant="secondary" className="text-[10px] px-1.5 py-0">
                                {p.eligibility}
                              </Badge>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Total */}
        <div className="grid grid-cols-[1fr_120px] items-center gap-4 px-6 py-4 border-t-2 border-border bg-muted/20">
          <span className="text-sm font-semibold uppercase tracking-widest text-muted-foreground">
            Total
          </span>
          <div className="flex flex-col items-end gap-0.5">
            <span className="text-[22px] font-bold tabular-nums text-primary leading-none">
              100,0%
            </span>
            <span className="text-[12px] font-semibold tabular-nums text-primary">
              {fmt(totalValue)}
            </span>
          </div>
        </div>

      </CardContent>
    </Card>
  );
};
