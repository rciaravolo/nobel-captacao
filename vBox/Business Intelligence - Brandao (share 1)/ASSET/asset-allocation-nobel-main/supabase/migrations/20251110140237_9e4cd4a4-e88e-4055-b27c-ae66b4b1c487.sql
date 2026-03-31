-- Set replica identity to allow deletes
ALTER TABLE "Asset Allocation - 11.2025" REPLICA IDENTITY FULL;

-- Delete existing data
DELETE FROM "Asset Allocation - 11.2025";

-- Insert new data
INSERT INTO "Asset Allocation - 11.2025" ("CLASSE", "SUBCLASSE", "CONSERVADORA", "MODERADA", "SOFISTICADA") VALUES
('RENDA FIXA BRASIL', 'Pós-fixado', '70,00%', '32,50%', '12,50%'),
('RENDA FIXA BRASIL', 'Inflação', '12,50%', '22,50%', '27,50%'),
('RENDA FIXA BRASIL', 'Prefixado', '5,00%', '10,00%', '7,50%'),
('MULTIMERCADOS', '-', '5,00%', '16,50%', '12,50%'),
('RENDA VARIÁVEL BRASIL', '-', '0,00%', '7,50%', '17,50%'),
('FUNDOS LISTADOS', '-', '2,50%', '2,00%', '8,00%'),
('ALTERNATIVOS', '-', '0,00%', '3,00%', '7,00%'),
('GLOBAL', 'Renda Fixa', '2,50%', '2,50%', '2,50%'),
('GLOBAL', 'Renda Variável', '2,50%', '3,50%', '5,00%');