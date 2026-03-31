-- Remover duplicados do GLOBAL, mantendo apenas os registros mais antigos
DELETE FROM recommended_products 
WHERE id IN (
  '710f36e3-cd91-4764-ab34-a2d910daffeb',  -- ARZ Confidas (CDI) moderate duplicado
  '7a9b80e0-eb96-4891-96cd-44211a0e0343',  -- ARZ Confidas (CDI) sophisticated duplicado
  '60eee8a0-db08-4412-8de0-9c9c6b61c2d8',  -- ARZ Confidas (DIJan) moderate duplicado
  '8f0ac232-447d-4a0a-af90-cf7599676d98',  -- ARZ Confidas (DIJan) sophisticated duplicado
  'fe227f5a-cedd-4d51-b0b5-cf6cd5949b44',  -- WHG Global moderate duplicado
  '0619644f-c498-4034-a526-568808faef98'   -- WHG Global sophisticated duplicado
);