import { useState, useEffect } from 'react';
import { SupabaseAllocationService } from '@/services/supabase-allocation';
import { AllocationService } from '@/services/allocation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import { supabase } from '@/integrations/supabase/client';
import { Loader2, Upload, FileText, BarChart3, Save } from 'lucide-react';
import * as pdfjsLib from 'pdfjs-dist';

// Configure PDF.js worker
pdfjsLib.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.mjs',
  import.meta.url
).toString();

// Estrutura fixa das linhas de alocação
const ALLOCATION_ROWS = [
  { classe: 'RENDA FIXA BRASIL',     subclasse: 'Pós-fixado'    },
  { classe: 'RENDA FIXA BRASIL',     subclasse: 'Inflação'       },
  { classe: 'RENDA FIXA BRASIL',     subclasse: 'Prefixado'      },
  { classe: 'MULTIMERCADOS',         subclasse: '-'              },
  { classe: 'RENDA VARIÁVEL BRASIL', subclasse: '-'              },
  { classe: 'FUNDOS LISTADOS',       subclasse: '-'              },
  { classe: 'ALTERNATIVOS',          subclasse: '-'              },
  { classe: 'GLOBAL',                subclasse: 'Renda Fixa'     },
  { classe: 'GLOBAL',                subclasse: 'Renda Variável' },
];

type AllocationRow = {
  conservadora: string;
  moderada: string;
  sofisticada: string;
};

type AllocationState = Record<string, AllocationRow>;

function rowKey(classe: string, sub: string) {
  return `${classe}||${sub}`;
}

function toDisplay(val: string): string {
  // "70,00%" → "70,0"
  return val.replace('%', '').replace(',', '.').replace(/\.?0+$/, '') || '0';
}

function toStorage(val: string): string {
  // "70" ou "70.0" → "70,00%"
  const num = parseFloat(val.replace(',', '.'));
  if (isNaN(num)) return '0,00%';
  return `${num.toFixed(2).replace('.', ',')}%`;
}

function sumPerfil(state: AllocationState, perfil: keyof AllocationRow): number {
  return ALLOCATION_ROWS.reduce((acc, r) => {
    const val = parseFloat(state[rowKey(r.classe, r.subclasse)]?.[perfil]?.replace(',', '.') || '0');
    return acc + (isNaN(val) ? 0 : val);
  }, 0);
}

export default function AdminMateriais() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [monthYear, setMonthYear] = useState('');
  const { toast } = useToast();

  // Alocação
  const defaultState = (): AllocationState => {
    const s: AllocationState = {};
    ALLOCATION_ROWS.forEach(r => {
      s[rowKey(r.classe, r.subclasse)] = { conservadora: '0', moderada: '0', sofisticada: '0' };
    });
    return s;
  };
  const [allocationValues, setAllocationValues] = useState<AllocationState>(defaultState);
  const [loadingAllocation, setLoadingAllocation] = useState(true);
  const [savingAllocation, setSavingAllocation] = useState(false);

  // Carrega os percentuais atuais ao abrir a página
  useEffect(() => {
    const load = async () => {
      setLoadingAllocation(true);
      try {
        const { data, error } = await supabase
          .from('Asset Allocation' as any)
          .select('*');

        if (error || !data || data.length === 0) {
          setLoadingAllocation(false);
          return;
        }

        const s: AllocationState = defaultState();
        (data as any[]).forEach((row: any) => {
          const sub = row['SUB-CLASSE'] ?? row.SUBCLASSE ?? '-';
          const k = rowKey(row.CLASSE, sub);
          if (s[k]) {
            s[k] = {
              conservadora: toDisplay(row.CONSERVADORA || '0'),
              moderada:     toDisplay(row.MODERADA     || '0'),
              sofisticada:  toDisplay(row.SOFISTICADA   || '0'),
            };
          }
        });
        setAllocationValues(s);
      } catch (e) {
        console.error(e);
      } finally {
        setLoadingAllocation(false);
      }
    };
    load();
  }, []);

  const handleCellChange = (key: string, perfil: keyof AllocationRow, value: string) => {
    setAllocationValues(prev => ({
      ...prev,
      [key]: { ...prev[key], [perfil]: value },
    }));
  };

  const handleSaveAllocation = async () => {
    // Valida totais
    const totals = {
      conservadora: sumPerfil(allocationValues, 'conservadora'),
      moderada:     sumPerfil(allocationValues, 'moderada'),
      sofisticada:  sumPerfil(allocationValues, 'sofisticada'),
    };
    const perfisInvalidos = Object.entries(totals)
      .filter(([, v]) => Math.abs(v - 100) > 0.1)
      .map(([k, v]) => `${k}: ${v.toFixed(1)}%`);

    if (perfisInvalidos.length > 0) {
      toast({
        title: 'Total não fecha 100%',
        description: perfisInvalidos.join(' | '),
        variant: 'destructive',
      });
      return;
    }

    setSavingAllocation(true);
    try {
      // Monta os registros
      const rows = ALLOCATION_ROWS.map(r => ({
        'CLASSE':        r.classe,
        'SUB-CLASSE':    r.subclasse,
        'CONSERVADORA':  toStorage(allocationValues[rowKey(r.classe, r.subclasse)].conservadora),
        'MODERADA':      toStorage(allocationValues[rowKey(r.classe, r.subclasse)].moderada),
        'SOFISTICADA':   toStorage(allocationValues[rowKey(r.classe, r.subclasse)].sofisticada),
      }));

      // Deleta todos e reinserere
      const { error: delErr } = await supabase
        .from('Asset Allocation' as any)
        .delete()
        .neq('id', 0); // deleta tudo

      if (delErr) throw delErr;

      const { error: insErr } = await supabase
        .from('Asset Allocation' as any)
        .insert(rows);

      if (insErr) throw insErr;

      // Invalida cache de cenários para próxima recalculação
      (SupabaseAllocationService as any)._latestMonth = null;
      (AllocationService as any).scenarios = null;

      toast({ title: 'Alocação salva!', description: 'Percentuais atualizados com sucesso.' });
    } catch (e: any) {
      toast({ title: 'Erro ao salvar', description: e.message, variant: 'destructive' });
    } finally {
      setSavingAllocation(false);
    }
  };

  // PDF helpers
  const extractTextFromPDF = async (file: File): Promise<string> => {
    const arrayBuffer = await file.arrayBuffer();
    const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
    let fullText = '';
    for (let i = 1; i <= pdf.numPages; i++) {
      const page = await pdf.getPage(i);
      const textContent = await page.getTextContent();
      fullText += textContent.items.map((item: any) => item.str).join(' ') + '\n';
    }
    return fullText;
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type === 'application/pdf') {
      setSelectedFile(file);
    } else {
      toast({ title: 'Erro', description: 'Por favor, selecione um arquivo PDF', variant: 'destructive' });
    }
  };

  const handleProcessPDF = async () => {
    if (!selectedFile || !monthYear) {
      toast({ title: 'Erro', description: 'Selecione um PDF e informe o mês/ano', variant: 'destructive' });
      return;
    }
    setIsProcessing(true);
    try {
      toast({ title: 'Processando', description: 'Extraindo texto do PDF...' });
      const pdfText = await extractTextFromPDF(selectedFile);
      toast({ title: 'Processando', description: 'Analisando produtos com IA...' });
      const { data, error } = await supabase.functions.invoke('parse-allocation-materials', {
        body: { pdfContent: pdfText, monthYear }
      });
      if (error) throw error;
      (SupabaseAllocationService as any)._latestMonth = null;
      toast({ title: 'Sucesso!', description: `${data.products_count} produtos extraídos e salvos.` });
      setSelectedFile(null);
      setMonthYear('');
      const fi = document.getElementById('pdf-file') as HTMLInputElement;
      if (fi) fi.value = '';
    } catch (e: any) {
      toast({ title: 'Erro', description: e.message || 'Erro ao processar PDF', variant: 'destructive' });
    } finally {
      setIsProcessing(false);
    }
  };

  const availablePDFs = [
    { name: 'Produtos Destaque - Março 2026',    file: '/materiais/Produtos-Destaque-Marco-2026.pdf',    suggestedDate: '2026-03-01' },
    { name: 'Produtos Destaque - Novembro 2025', file: '/materiais/Produtos-Destaque-Novembro-2025.pdf', suggestedDate: '2025-11-01' },
    { name: 'Produtos Destaque - Outubro 2025',  file: '/materiais/Produtos-Destaque-Outubro-2025.pdf',  suggestedDate: '2025-10-01' },
    { name: 'Produtos Destaque - Setembro 2025', file: '/materiais/Produtos-Destaque-Setembro-2025.pdf', suggestedDate: '2025-09-01' },
  ];

  const handleProcessExistingPDF = async (pdfPath: string, suggestedDate: string) => {
    setIsProcessing(true);
    try {
      const response = await fetch(pdfPath);
      const blob = await response.blob();
      const file = new File([blob], pdfPath.split('/').pop() || 'document.pdf', { type: 'application/pdf' });
      toast({ title: 'Processando', description: 'Extraindo texto do PDF...' });
      const pdfText = await extractTextFromPDF(file);
      toast({ title: 'Processando', description: 'Analisando produtos com IA...' });
      const { data, error } = await supabase.functions.invoke('parse-allocation-materials', {
        body: { pdfContent: pdfText, monthYear: suggestedDate }
      });
      if (error) throw error;
      toast({ title: 'Sucesso!', description: `${data.products_count} produtos extraídos e salvos.` });
    } catch (e: any) {
      toast({ title: 'Erro', description: e.message || 'Erro ao processar PDF', variant: 'destructive' });
    } finally {
      setIsProcessing(false);
    }
  };

  const perfis: { key: keyof AllocationRow; label: string }[] = [
    { key: 'conservadora', label: 'Conservadora' },
    { key: 'moderada',     label: 'Moderada'     },
    { key: 'sofisticada',  label: 'Sofisticada'  },
  ];

  return (
    <div className="container mx-auto py-8 px-4 max-w-5xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-foreground mb-1">Admin — Materiais</h1>
        <p className="text-muted-foreground text-sm">Atualize percentuais de alocação e produtos recomendados</p>
      </div>

      <div className="space-y-6">

        {/* ── Percentuais de Alocação ── */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base">
              <BarChart3 className="h-4 w-4" />
              Percentuais de Alocação
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loadingAllocation ? (
              <div className="flex items-center gap-2 text-muted-foreground text-sm py-4">
                <Loader2 className="h-4 w-4 animate-spin" /> Carregando...
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border">
                      <th className="text-left py-2 pr-4 font-medium text-muted-foreground w-[180px]">Classe</th>
                      <th className="text-left py-2 pr-4 font-medium text-muted-foreground w-[130px]">Sub-classe</th>
                      {perfis.map(p => (
                        <th key={p.key} className="text-center py-2 px-2 font-medium text-muted-foreground w-[110px]">
                          {p.label}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {ALLOCATION_ROWS.map(r => {
                      const k = rowKey(r.classe, r.subclasse);
                      return (
                        <tr key={k} className="border-b border-border/40 hover:bg-muted/20">
                          <td className="py-2 pr-4 font-medium text-xs text-foreground">{r.classe}</td>
                          <td className="py-2 pr-4 text-xs text-muted-foreground">
                            {r.subclasse === '-' ? '—' : r.subclasse}
                          </td>
                          {perfis.map(p => (
                            <td key={p.key} className="py-1.5 px-2">
                              <div className="relative">
                                <Input
                                  className="h-8 text-center text-sm pr-6 tabular-nums"
                                  value={allocationValues[k]?.[p.key] ?? '0'}
                                  onChange={e => handleCellChange(k, p.key, e.target.value)}
                                />
                                <span className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground text-xs pointer-events-none">%</span>
                              </div>
                            </td>
                          ))}
                        </tr>
                      );
                    })}
                    {/* Totais */}
                    <tr className="border-t-2 border-border bg-muted/20 font-semibold">
                      <td className="py-2 pr-4 text-xs" colSpan={2}>Total</td>
                      {perfis.map(p => {
                        const total = sumPerfil(allocationValues, p.key);
                        const ok = Math.abs(total - 100) <= 0.1;
                        return (
                          <td key={p.key} className={`py-2 px-2 text-center text-sm tabular-nums ${ok ? 'text-foreground' : 'text-destructive font-bold'}`}>
                            {total.toFixed(1)}%
                          </td>
                        );
                      })}
                    </tr>
                  </tbody>
                </table>
              </div>
            )}

            <div className="mt-4 flex justify-end">
              <Button onClick={handleSaveAllocation} disabled={savingAllocation || loadingAllocation}>
                {savingAllocation
                  ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Salvando...</>
                  : <><Save className="mr-2 h-4 w-4" />Salvar Alocação</>
                }
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* ── Upload Manual de PDF ── */}
        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-base">
                <Upload className="h-4 w-4" />
                Upload de PDF — Produtos
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="pdf-file">Arquivo PDF</Label>
                <Input id="pdf-file" type="file" accept=".pdf" onChange={handleFileChange} disabled={isProcessing} />
              </div>
              <div>
                <Label htmlFor="month-year">Mês de referência</Label>
                <Input
                  id="month-year"
                  type="date"
                  value={monthYear}
                  onChange={e => setMonthYear(e.target.value)}
                  disabled={isProcessing}
                  placeholder="2026-03-01"
                />
              </div>
              <Button onClick={handleProcessPDF} disabled={isProcessing || !selectedFile || !monthYear} className="w-full">
                {isProcessing
                  ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Processando...</>
                  : <><Upload className="mr-2 h-4 w-4" />Processar PDF</>
                }
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="flex items-center gap-2 text-base">
                <FileText className="h-4 w-4" />
                PDFs Disponíveis
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {availablePDFs.map((pdf, i) => (
                  <div key={i} className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50">
                    <div className="flex-1">
                      <p className="font-medium text-sm">{pdf.name}</p>
                      <p className="text-xs text-muted-foreground">{pdf.suggestedDate}</p>
                    </div>
                    <Button size="sm" variant="outline" onClick={() => handleProcessExistingPDF(pdf.file, pdf.suggestedDate)} disabled={isProcessing}>
                      {isProcessing ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Processar'}
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

      </div>
    </div>
  );
}

