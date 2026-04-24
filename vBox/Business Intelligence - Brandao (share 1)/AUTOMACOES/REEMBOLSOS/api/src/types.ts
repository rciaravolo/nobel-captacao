export interface Env {
  DB: D1Database;
  ATTACHMENTS: R2Bucket;
  JWT_SECRET: string;
  RESEND_API_KEY: string;
  FINANCE_EMAIL: string;
  FRONTEND_URL: string;
}

export interface JWTPayload {
  sub: number;
  email: string;
  name: string;
  role: 'assessor' | 'financeiro';
  exp: number;
}

export interface UserRecord {
  id: number;
  name: string;
  email: string;
  password_hash: string;
  role: 'assessor' | 'financeiro';
  team: string | null;
  active: number;
  created_at: string;
}

export interface ReimbursementRecord {
  id: number;
  user_id: number;
  expense_date: string;
  amount: number;
  category: string;
  cost_center: string;
  description: string;
  attachment_key: string;
  attachment_name: string;
  status: 'pending' | 'approved' | 'rejected';
  reviewer_id: number | null;
  reviewer_notes: string | null;
  created_at: string;
  reviewed_at: string | null;
  // campos de JOIN
  user_name?: string;
  user_email?: string;
  user_team?: string;
  reviewer_name?: string;
}

export type AppContext = {
  Bindings: Env;
  Variables: { user: JWTPayload };
};

export const CATEGORIES = ['Transporte', 'Alimentação', 'Hospedagem', 'Material', 'Outros'] as const;
export const COST_CENTERS = ['PRIVATE', 'BRAVO', 'RIO PRETO', 'SMART-GLOBAL', 'SMART-UNIQUE', 'SMART-ALFA'] as const;
