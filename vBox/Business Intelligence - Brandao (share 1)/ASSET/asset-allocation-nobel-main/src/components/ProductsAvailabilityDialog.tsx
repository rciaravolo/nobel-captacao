import { useState, useEffect } from 'react';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { AlertTriangle } from 'lucide-react';
import { supabase } from '@/integrations/supabase/client';
import { format, startOfMonth, isBefore } from 'date-fns';
import { ptBR } from 'date-fns/locale';

export function ProductsAvailabilityDialog() {
  const [open, setOpen] = useState(false);
  const [latestMonth, setLatestMonth] = useState<string | null>(null);

  useEffect(() => {
    const checkProductsAvailability = async () => {
      try {
        // Get the latest month_year from recommended_products
        const { data, error } = await supabase
          .from('recommended_products')
          .select('month_year')
          .order('month_year', { ascending: false })
          .limit(1);

        if (error) {
          console.error('Error checking products availability:', error);
          return;
        }

        if (data && data.length > 0) {
          // Parse the date correctly - adding time to avoid timezone issues
          const dateStr = data[0].month_year;
          const latestProductMonth = new Date(dateStr + 'T12:00:00');
          const currentMonth = startOfMonth(new Date());

          // If latest product month is before current month, show warning
          if (isBefore(latestProductMonth, currentMonth)) {
            setLatestMonth(format(latestProductMonth, "MMMM 'de' yyyy", { locale: ptBR }));
            setOpen(true);
          }
        }
      } catch (error) {
        console.error('Error in checkProductsAvailability:', error);
      }
    };

    // Small delay to ensure page is loaded
    const timer = setTimeout(checkProductsAvailability, 500);
    return () => clearTimeout(timer);
  }, []);

  if (!latestMonth) return null;

  return (
    <AlertDialog open={open} onOpenChange={setOpen}>
      <AlertDialogContent className="max-w-md">
        <AlertDialogHeader>
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-warning/10 rounded-full">
              <AlertTriangle className="h-6 w-6 text-warning" />
            </div>
            <AlertDialogTitle className="text-lg">
              Produtos em Atualização
            </AlertDialogTitle>
          </div>
          <AlertDialogDescription className="text-sm leading-relaxed">
            Os produtos recomendados disponíveis são referentes a{' '}
            <span className="font-semibold text-foreground capitalize">{latestMonth}</span>.
            <br /><br />
            A lista do mês atual ainda está sendo atualizada pela equipe. 
            Você pode continuar usando o sistema normalmente com os dados disponíveis.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogAction className="w-full sm:w-auto">
            Entendi
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
