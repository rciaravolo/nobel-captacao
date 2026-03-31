-- Mover COE Petrobrás para Renda Fixa Pré-fixada
UPDATE recommended_products 
SET asset_class = 'RENDA FIXA', asset_subclass = 'Pré-fixado'
WHERE month_year = '2025-12-01' AND product_name ILIKE '%COE Petrobrás%';

-- Mover COE Soberano Pós para Renda Fixa Pós-fixada
UPDATE recommended_products 
SET asset_class = 'RENDA FIXA', asset_subclass = 'Pós-fixado'
WHERE month_year = '2025-12-01' AND product_name ILIKE '%COE Soberano%';

-- Remover Riza Malls dos Alternativos (mantendo apenas COE Bitcoin e Kinea Special)
DELETE FROM recommended_products 
WHERE month_year = '2025-12-01' AND asset_class = 'ALTERNATIVOS' AND product_name ILIKE '%Riza Malls%';