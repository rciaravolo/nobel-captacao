-- ============================================================
-- SETUP COMPLETO — Portfolio Advisor Nobel Capital
-- Executar no SQL Editor do novo projeto Supabase
-- https://supabase.com/dashboard/project/yrzgtapcbaapysdtnosn/sql
-- ============================================================

-- ------------------------------------------------------------
-- 1. Tabela Asset Allocation (percentuais por perfil)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public."Asset Allocation" (
  id BIGSERIAL PRIMARY KEY,
  "CLASSE" TEXT NOT NULL,
  "SUB-CLASSE" TEXT NOT NULL,
  "CONSERVADORA" TEXT,
  "MODERADA" TEXT,
  "SOFISTICADA" TEXT
);

ALTER TABLE public."Asset Allocation" ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read access to Asset Allocation"
ON public."Asset Allocation"
FOR SELECT
USING (true);

-- Dados de alocação
INSERT INTO public."Asset Allocation" ("CLASSE", "SUB-CLASSE", "CONSERVADORA", "MODERADA", "SOFISTICADA") VALUES
('Renda Fixa', 'Renda Fixa Pós-fixada', '60,00%', '40,00%', '20,00%'),
('Renda Fixa', 'Renda Fixa Pré-fixada', '25,00%', '20,00%',  '7,00%'),
('Renda Fixa', 'Renda Fixa Inflação',   '10,00%', '15,00%',  '3,00%'),
('Ações',      'Ações Brasil',           '3,00%',  '15,00%', '30,00%'),
('Ações',      'Ações Internacional',    '2,00%',   '5,00%', '25,00%'),
('Imobiliário','REITs',                  '0,00%',   '3,00%',  '8,00%'),
('Commodities','Commodities',            '0,00%',   '2,00%',  '5,00%'),
('Criptomoedas','Criptomoedas',          '0,00%',   '0,00%',  '2,00%');

-- ------------------------------------------------------------
-- 2. Tabela recommended_products (produtos extraídos do PDF)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.recommended_products (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  month_year DATE NOT NULL,
  asset_class TEXT NOT NULL,
  asset_subclass TEXT NOT NULL,
  profile TEXT NOT NULL CHECK (profile IN ('conservative', 'moderate', 'sophisticated')),
  product_name TEXT NOT NULL,
  percentage NUMERIC,
  expected_return TEXT,
  eligibility TEXT,
  product_type TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_recommended_products_month_profile
  ON public.recommended_products(month_year, profile);

CREATE INDEX IF NOT EXISTS idx_recommended_products_class
  ON public.recommended_products(asset_class, asset_subclass);

ALTER TABLE public.recommended_products ENABLE ROW LEVEL SECURITY;

-- Leitura pública
CREATE POLICY "Allow public read access to recommended_products"
ON public.recommended_products FOR SELECT USING (true);

-- Insert/Delete via service_role (usado pelo script Python)
-- (service_role bypassa RLS automaticamente — não precisa de policy extra)

-- Trigger updated_at
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = '';

CREATE TRIGGER update_recommended_products_updated_at
BEFORE UPDATE ON public.recommended_products
FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
