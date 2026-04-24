-- Schema inicial do sistema de reembolsos Nobel Capital
-- Executar via: wrangler d1 execute reembolsos --file=migrations/001_initial.sql

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL CHECK(role IN ('assessor', 'financeiro')),
  team TEXT,
  active INTEGER DEFAULT 1,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS reimbursements (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL REFERENCES users(id),
  expense_date TEXT NOT NULL,
  amount REAL NOT NULL,
  category TEXT NOT NULL CHECK(category IN ('Transporte', 'Alimentação', 'Hospedagem', 'Material', 'Outros')),
  cost_center TEXT NOT NULL CHECK(cost_center IN ('PRIVATE', 'BRAVO', 'RIO PRETO', 'SMART-GLOBAL', 'SMART-UNIQUE', 'SMART-ALFA')),
  description TEXT NOT NULL,
  attachment_key TEXT NOT NULL,
  attachment_name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'rejected')),
  reviewer_id INTEGER REFERENCES users(id),
  reviewer_notes TEXT,
  created_at TEXT DEFAULT (datetime('now')),
  reviewed_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_reimbursements_user_id ON reimbursements(user_id);
CREATE INDEX IF NOT EXISTS idx_reimbursements_status ON reimbursements(status);
CREATE INDEX IF NOT EXISTS idx_reimbursements_created_at ON reimbursements(created_at);
