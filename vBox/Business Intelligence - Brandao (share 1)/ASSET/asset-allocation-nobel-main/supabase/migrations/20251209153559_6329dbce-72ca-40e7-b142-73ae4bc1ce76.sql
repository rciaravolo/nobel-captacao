-- Adicionar produtos Multimercado para perfil Moderado
INSERT INTO recommended_products (month_year, asset_class, asset_subclass, profile, product_name, percentage, eligibility)
VALUES 
  ('2025-12-01', 'MULTIMERCADOS', 'Multimercado', 'moderate', 'Genoa Capital Radar', 6.0, 'PG'),
  ('2025-12-01', 'MULTIMERCADOS', 'Multimercado', 'moderate', 'Quantitas FIC FIM Mallorca', 6.0, 'PG'),
  ('2025-12-01', 'MULTIMERCADOS', 'Multimercado', 'moderate', 'Verde AM Mundi Mult XP Seg', 4.5, 'IQ');

-- Adicionar produtos Multimercado para perfil Sofisticado
INSERT INTO recommended_products (month_year, asset_class, asset_subclass, profile, product_name, percentage, eligibility)
VALUES 
  ('2025-12-01', 'MULTIMERCADOS', 'Multimercado', 'sophisticated', 'Genoa Capital Radar', 6.0, 'PG'),
  ('2025-12-01', 'MULTIMERCADOS', 'Multimercado', 'sophisticated', 'Quantitas FIC FIM Mallorca', 6.0, 'PG'),
  ('2025-12-01', 'MULTIMERCADOS', 'Multimercado', 'sophisticated', 'Verde AM Mundi Mult XP Seg', 4.5, 'IQ');