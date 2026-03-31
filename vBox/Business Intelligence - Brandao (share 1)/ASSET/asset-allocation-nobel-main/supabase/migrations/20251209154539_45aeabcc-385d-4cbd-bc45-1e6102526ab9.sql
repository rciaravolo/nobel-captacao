-- Adicionar produtos Renda Fixa Global para perfil Moderado
INSERT INTO recommended_products (month_year, asset_class, asset_subclass, profile, product_name, percentage, expected_return, eligibility)
VALUES 
  ('2025-12-01', 'RENDA FIXA GLOBAL', 'Renda Fixa Global', 'moderate', 'ARZ Confidas (CDI + 4,70% a.a.)', 1.25, 'CDI + 4,70% a.a.', 'IQ'),
  ('2025-12-01', 'RENDA FIXA GLOBAL', 'Renda Fixa Global', 'moderate', 'ARZ Confidas (DIJan/30 +2,70% a.a)', 1.25, 'DIJan/30 +2,70% a.a', 'IQ');

-- Adicionar produto Renda Variável Global para perfil Moderado
INSERT INTO recommended_products (month_year, asset_class, asset_subclass, profile, product_name, percentage, eligibility)
VALUES 
  ('2025-12-01', 'RENDA VARIÁVEL GLOBAL', 'Renda Variável Global', 'moderate', 'WHG Global LB BRL FIC FIM CP IE', 3.5, 'IQ');

-- Adicionar produtos Renda Fixa Global para perfil Sofisticado
INSERT INTO recommended_products (month_year, asset_class, asset_subclass, profile, product_name, percentage, expected_return, eligibility)
VALUES 
  ('2025-12-01', 'RENDA FIXA GLOBAL', 'Renda Fixa Global', 'sophisticated', 'ARZ Confidas (CDI + 4,70% a.a.)', 1.25, 'CDI + 4,70% a.a.', 'IQ'),
  ('2025-12-01', 'RENDA FIXA GLOBAL', 'Renda Fixa Global', 'sophisticated', 'ARZ Confidas (DIJan/30 +2,70% a.a)', 1.25, 'DIJan/30 +2,70% a.a', 'IQ');

-- Adicionar produto Renda Variável Global para perfil Sofisticado
INSERT INTO recommended_products (month_year, asset_class, asset_subclass, profile, product_name, percentage, eligibility)
VALUES 
  ('2025-12-01', 'RENDA VARIÁVEL GLOBAL', 'Renda Variável Global', 'sophisticated', 'WHG Global LB BRL FIC FIM CP IE', 3.5, 'IQ');