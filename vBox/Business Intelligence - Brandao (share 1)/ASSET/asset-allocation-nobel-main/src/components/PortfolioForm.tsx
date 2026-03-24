import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { AllocationInput, Scenario } from '@/types/portfolio';
import { AllocationService } from '@/services/allocation';
import { z } from 'zod';
import { toast } from 'sonner';

// CDI fixo — atualizar conforme COPOM
const CDI_ANUAL = 0.1315;

const portfolioSchema = z.object({
  valor_captado: z.number()
    .positive({ message: "Valor deve ser positivo" })
    .min(1000, { message: "Valor mínimo: R$ 1.000" })
    .max(1000000000, { message: "Valor máximo excedido" }),
  cdi_anual: z.number()
    .min(0, { message: "CDI não pode ser negativo" })
    .max(1, { message: "CDI deve ser menor que 100%" }),
  perfil: z.string().min(1, { message: "Selecione um perfil" })
});
interface PortfolioFormProps {
  onSubmit: (data: AllocationInput) => void;
  loading?: boolean;
}
export const PortfolioForm = ({
  onSubmit,
  loading
}: PortfolioFormProps) => {
  const [formData, setFormData] = useState<AllocationInput>({
    valor_captado: 100000,
    perfil: '',
    cdi_anual: CDI_ANUAL
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

  // Auto-submit when form data changes with validation
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
    
    // Validate the value
    const valueValidation = z.number()
      .positive({ message: "Valor deve ser positivo" })
      .min(1000, { message: "Valor mínimo: R$ 1.000" })
      .max(1000000000, { message: "Valor máximo excedido" })
      .safeParse(numericValue);
    
    if (!valueValidation.success && numericValue > 0) {
      toast.error(valueValidation.error.errors[0].message);
    }
    
    setFormData(prev => ({
      ...prev,
      valor_captado: numericValue
    }));
  };
  return <Card className="w-full max-w-2xl mx-auto shadow-card">
      <CardHeader>
        <CardTitle className="text-2xl text-primary text-center">Alocação de Carteira</CardTitle>
        <CardDescription className="text-center">
          Configure os parâmetros para calcular a alocação ideal e projeção de retornos
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-8">
          {/* Centered Value Field */}
          <div className="flex justify-center">
            <div className="w-full max-w-md space-y-2">
              <Label htmlFor="valor" className="text-center block">Valor Captado (R$)</Label>
              <Input id="valor" type="text" value={formatCurrency(formData.valor_captado.toString())} onChange={e => handleValueChange(e.target.value)} placeholder="100.000" className="text-right text-lg font-semibold h-12" />
            </div>
          </div>

          {/* Portfolio Selection Dropdown */}
          <div className="flex justify-center">
            <div className="w-full max-w-md space-y-2">
              <Label className="text-center block">Perfil de Investimento</Label>
              {loadingScenarios ? (
                <div className="text-center py-4">Carregando perfis...</div>
              ) : (
                <Select
                  value={formData.perfil}
                  onValueChange={(value) => setFormData(prev => ({ ...prev, perfil: value }))}
                >
                  <SelectTrigger className="h-12 text-base">
                    <SelectValue placeholder="Selecione o seu perfil" />
                  </SelectTrigger>
                  <SelectContent className="bg-background border border-border z-50">
                    {scenarios.map(scenario => (
                      <SelectItem 
                        key={scenario.id} 
                        value={scenario.id}
                        className="cursor-pointer"
                      >
                        <div className="flex items-center gap-3">
                          <span className="font-semibold">{scenario.name}</span>
                          <span className="text-xs text-muted-foreground">
                            {scenario.expected_return} • Vol: {scenario.target_vol}%
                          </span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
            </div>
          </div>


        </div>
      </CardContent>
    </Card>;
};