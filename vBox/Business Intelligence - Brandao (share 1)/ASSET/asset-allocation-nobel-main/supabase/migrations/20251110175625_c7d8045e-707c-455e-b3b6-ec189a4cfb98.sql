-- Create recommended_products table
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

-- Create index for faster queries
CREATE INDEX idx_recommended_products_month_profile ON public.recommended_products(month_year, profile);
CREATE INDEX idx_recommended_products_class ON public.recommended_products(asset_class, asset_subclass);

-- Enable RLS
ALTER TABLE public.recommended_products ENABLE ROW LEVEL SECURITY;

-- Create policy for public read access
CREATE POLICY "Allow public read access to recommended_products"
ON public.recommended_products
FOR SELECT
USING (true);

-- Create updated_at trigger function if it doesn't exist
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for automatic timestamp updates
CREATE TRIGGER update_recommended_products_updated_at
BEFORE UPDATE ON public.recommended_products
FOR EACH ROW
EXECUTE FUNCTION public.update_updated_at_column();