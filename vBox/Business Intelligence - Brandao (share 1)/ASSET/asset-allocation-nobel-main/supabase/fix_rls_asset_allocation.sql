-- Libera INSERT e DELETE na tabela Asset Allocation para o admin page
-- Executar em: supabase.com/dashboard/project/yrzgtapcbaapysdtnosn/sql/new

CREATE POLICY "Allow anon insert on Asset Allocation"
ON public."Asset Allocation"
FOR INSERT
WITH CHECK (true);

CREATE POLICY "Allow anon delete on Asset Allocation"
ON public."Asset Allocation"
FOR DELETE
USING (true);
