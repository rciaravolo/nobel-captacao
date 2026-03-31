-- Populate Asset Allocation table with allocation data
INSERT INTO public."Asset Allocation" ("CLASSE", "SUB-CLASSE", "CONSERVADORA", "MODERADA", "SOFISTICADA") VALUES
('Renda Fixa', 'Renda Fixa Pós-fixada', '60,00%', '40,00%', '20,00%'),
('Renda Fixa', 'Renda Fixa Pré-fixada', '25,00%', '20,00%', '7,00%'),
('Renda Fixa', 'Renda Fixa Inflação', '10,00%', '15,00%', '3,00%'),
('Ações', 'Ações Brasil', '3,00%', '15,00%', '30,00%'),
('Ações', 'Ações Internacional', '2,00%', '5,00%', '25,00%'),
('Imobiliário', 'REITs', '0,00%', '3,00%', '8,00%'),
('Commodities', 'Commodities', '0,00%', '2,00%', '5,00%'),
('Criptomoedas', 'Criptomoedas', '0,00%', '0,00%', '2,00%');