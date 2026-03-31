-- Corrigir produtos de Renda Fixa Global
UPDATE recommended_products 
SET asset_class = 'GLOBAL', asset_subclass = 'Renda Fixa'
WHERE month_year = '2025-12-01' AND asset_class = 'RENDA FIXA GLOBAL';

-- Corrigir produtos de Renda Variável Global
UPDATE recommended_products 
SET asset_class = 'GLOBAL', asset_subclass = 'Renda Variável'
WHERE month_year = '2025-12-01' AND asset_class = 'RENDA VARIÁVEL GLOBAL';