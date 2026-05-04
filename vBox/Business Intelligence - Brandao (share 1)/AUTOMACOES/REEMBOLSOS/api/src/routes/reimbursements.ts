import { Hono } from 'hono';
import { AppContext, ReimbursementRecord, CATEGORIES, COST_CENTERS } from '../types';
import type { Env } from '../types';

const reimbursementRoutes = new Hono<AppContext>();

const ALLOWED_TYPES = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg'];
const MAX_SIZE = 10 * 1024 * 1024; // 10 MB

// POST /api/reimbursements — criar novo pedido
reimbursementRoutes.post('/', async (c) => {
  const user = c.get('user');

  let formData: FormData;
  try {
    formData = await c.req.formData();
  } catch {
    return c.json({ error: 'Dados do formulário inválidos' }, 400);
  }

  const expense_date = (formData.get('expense_date') as string)?.trim();
  const amountRaw = formData.get('amount') as string;
  const category = (formData.get('category') as string)?.trim();
  const cost_center = (formData.get('cost_center') as string)?.trim();
  const description = (formData.get('description') as string)?.trim();
  const file = formData.get('attachment') as File | null;

  // --- Validações ---
  if (!expense_date || !amountRaw || !category || !cost_center || !description || !file) {
    return c.json({ error: 'Todos os campos são obrigatórios, incluindo o comprovante' }, 400);
  }

  const today = new Date().toISOString().split('T')[0];
  if (expense_date > today) {
    return c.json({ error: 'Data da despesa não pode ser futura' }, 400);
  }

  const amount = parseFloat(amountRaw);
  if (isNaN(amount) || amount <= 0) {
    return c.json({ error: 'Valor deve ser maior que zero' }, 400);
  }

  if (!(CATEGORIES as readonly string[]).includes(category)) {
    return c.json({ error: `Categoria inválida. Valores aceitos: ${CATEGORIES.join(', ')}` }, 400);
  }

  if (!(COST_CENTERS as readonly string[]).includes(cost_center)) {
    return c.json({ error: `Centro de custo inválido. Valores aceitos: ${COST_CENTERS.join(', ')}` }, 400);
  }

  if (description.length < 10) {
    return c.json({ error: 'Descrição deve ter no mínimo 10 caracteres' }, 400);
  }

  if (!ALLOWED_TYPES.includes(file.type)) {
    return c.json({ error: 'Arquivo deve ser PDF, JPG ou PNG' }, 400);
  }

  if (file.size > MAX_SIZE) {
    return c.json({ error: 'Arquivo deve ter no máximo 10MB' }, 400);
  }

  // --- Upload para R2 ---
  const ext = file.name.split('.').pop()?.toLowerCase() || 'bin';
  const attachment_key = `reimbursements/${user.sub}/${Date.now()}.${ext}`;
  const arrayBuffer = await file.arrayBuffer();

  await c.env.ATTACHMENTS.put(attachment_key, arrayBuffer, {
    httpMetadata: { contentType: file.type },
    customMetadata: {
      originalName: file.name,
      uploadedBy: String(user.sub),
    },
  });

  // --- Salva no D1 ---
  const result = await c.env.DB.prepare(`
    INSERT INTO reimbursements
      (user_id, expense_date, amount, category, cost_center, description, attachment_key, attachment_name)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `).bind(user.sub, expense_date, amount, category, cost_center, description, attachment_key, file.name).run();

  const id = result.meta.last_row_id as number;

  // --- Emails assíncronos (não bloqueia a resposta) ---
  c.executionCtx.waitUntil(
    sendEmail(c.env, {
      type: 'new_request',
      assessorName: user.name,
      assessorEmail: user.email,
      amount, category, cost_center, expense_date, id,
    })
  );

  return c.json({ id, message: 'Pedido de reembolso enviado com sucesso' }, 201);
});

// GET /api/reimbursements — listar pedidos
reimbursementRoutes.get('/', async (c) => {
  const user = c.get('user');
  const status = c.req.query('status');

  const validStatuses = ['pending', 'approved', 'rejected'];
  const statusFilter = status && validStatuses.includes(status) ? status : null;

  let query: string;
  let bindings: (string | number)[];

  const base = `
    SELECT r.*,
           u.name  AS user_name,
           u.email AS user_email,
           u.team  AS user_team,
           rev.name AS reviewer_name
    FROM reimbursements r
    JOIN users u   ON r.user_id    = u.id
    LEFT JOIN users rev ON r.reviewer_id = rev.id
  `;

  if (user.role === 'financeiro') {
    query = base + (statusFilter ? 'WHERE r.status = ?' : '') + ' ORDER BY r.created_at DESC';
    bindings = statusFilter ? [statusFilter] : [];
  } else {
    query = base + (statusFilter
      ? 'WHERE r.user_id = ? AND r.status = ?'
      : 'WHERE r.user_id = ?'
    ) + ' ORDER BY r.created_at DESC';
    bindings = statusFilter ? [user.sub, statusFilter] : [user.sub];
  }

  const { results } = await c.env.DB.prepare(query).bind(...bindings).all<ReimbursementRecord>();
  return c.json(results);
});

// GET /api/reimbursements/:id — detalhe de um pedido
reimbursementRoutes.get('/:id', async (c) => {
  const user = c.get('user');
  const id = parseInt(c.req.param('id'));
  if (isNaN(id)) return c.json({ error: 'ID inválido' }, 400);

  const record = await c.env.DB.prepare(`
    SELECT r.*,
           u.name  AS user_name,
           u.email AS user_email,
           u.team  AS user_team,
           rev.name AS reviewer_name
    FROM reimbursements r
    JOIN users u ON r.user_id = u.id
    LEFT JOIN users rev ON r.reviewer_id = rev.id
    WHERE r.id = ?
  `).bind(id).first<ReimbursementRecord>();

  if (!record) return c.json({ error: 'Pedido não encontrado' }, 404);
  if (user.role !== 'financeiro' && record.user_id !== user.sub) {
    return c.json({ error: 'Acesso negado' }, 403);
  }

  return c.json(record);
});

// PATCH /api/reimbursements/:id/review — aprovar ou recusar (financeiro)
reimbursementRoutes.patch('/:id/review', async (c) => {
  const user = c.get('user');
  if (user.role !== 'financeiro') {
    return c.json({ error: 'Acesso restrito ao financeiro' }, 403);
  }

  const id = parseInt(c.req.param('id'));
  if (isNaN(id)) return c.json({ error: 'ID inválido' }, 400);

  let body: { status?: string; reviewer_notes?: string };
  try {
    body = await c.req.json();
  } catch {
    return c.json({ error: 'JSON inválido' }, 400);
  }

  const { status, reviewer_notes } = body;
  if (!status || !['approved', 'rejected'].includes(status)) {
    return c.json({ error: 'Status deve ser "approved" ou "rejected"' }, 400);
  }
  if (status === 'rejected' && (!reviewer_notes || reviewer_notes.trim().length < 5)) {
    return c.json({ error: 'Observação obrigatória ao recusar (mínimo 5 caracteres)' }, 400);
  }

  const record = await c.env.DB.prepare(
    'SELECT * FROM reimbursements WHERE id = ?'
  ).bind(id).first<any>();

  if (!record) return c.json({ error: 'Pedido não encontrado' }, 404);
  if (record.status !== 'pending') {
    return c.json({ error: 'Pedido já foi revisado anteriormente' }, 400);
  }

  await c.env.DB.prepare(`
    UPDATE reimbursements
    SET status = ?, reviewer_id = ?, reviewer_notes = ?, reviewed_at = datetime('now')
    WHERE id = ?
  `).bind(status, user.sub, reviewer_notes?.trim() || null, id).run();

  // Busca dados do assessor para email
  const assessor = await c.env.DB.prepare(
    'SELECT name, email FROM users WHERE id = ?'
  ).bind(record.user_id).first<any>();

  if (assessor) {
    c.executionCtx.waitUntil(
      sendEmail(c.env, {
        type: 'review_result',
        assessorName: assessor.name,
        assessorEmail: assessor.email,
        amount: record.amount,
        category: record.category,
        status,
        reviewer_notes: reviewer_notes?.trim(),
        id,
      })
    );
  }

  const msg = status === 'approved' ? 'Pedido aprovado com sucesso' : 'Pedido recusado';
  return c.json({ message: msg });
});

// GET /api/reimbursements/:id/attachment — serve o arquivo do R2
reimbursementRoutes.get('/:id/attachment', async (c) => {
  const user = c.get('user');
  const id = parseInt(c.req.param('id'));
  if (isNaN(id)) return c.json({ error: 'ID inválido' }, 400);

  const record = await c.env.DB.prepare(
    'SELECT user_id, attachment_key, attachment_name FROM reimbursements WHERE id = ?'
  ).bind(id).first<any>();

  if (!record) return c.json({ error: 'Pedido não encontrado' }, 404);
  if (user.role !== 'financeiro' && record.user_id !== user.sub) {
    return c.json({ error: 'Acesso negado' }, 403);
  }

  const object = await c.env.ATTACHMENTS.get(record.attachment_key);
  if (!object) return c.json({ error: 'Arquivo não encontrado no storage' }, 404);

  const headers = new Headers();
  object.writeHttpMetadata(headers);
  headers.set('Cache-Control', 'private, max-age=3600');
  headers.set(
    'Content-Disposition',
    `inline; filename="${encodeURIComponent(record.attachment_name)}"`
  );

  return new Response(object.body, { headers });
});

// --- Helpers de email ---

interface EmailParams {
  type: 'new_request' | 'review_result';
  assessorName: string;
  assessorEmail: string;
  amount: number;
  category: string;
  cost_center?: string;
  expense_date?: string;
  status?: string;
  reviewer_notes?: string;
  id: number;
}

async function sendEmail(env: Env, params: EmailParams): Promise<void> {
  if (!env.RESEND_API_KEY || !env.FINANCE_EMAIL) return;

  const brl = (v: number) => v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

  let subject: string;
  let html: string;
  let to: string[];

  if (params.type === 'new_request') {
    subject = `[Reembolso #${params.id}] Nova solicitação — ${brl(params.amount)}`;
    to = [env.FINANCE_EMAIL];
    html = `
      <div style="font-family:sans-serif;max-width:600px;margin:0 auto">
        <div style="background:#1a2744;padding:20px;border-radius:8px 8px 0 0">
          <h1 style="color:#c9a84c;margin:0;font-size:20px">Nobel Capital — Reembolsos</h1>
        </div>
        <div style="border:1px solid #e2e8f0;border-top:none;padding:24px;border-radius:0 0 8px 8px">
          <h2 style="margin-top:0">Nova Solicitação de Reembolso #${params.id}</h2>
          <table style="width:100%;border-collapse:collapse">
            <tr><td style="padding:6px 0;color:#718096">Solicitante</td><td><strong>${params.assessorName}</strong></td></tr>
            <tr><td style="padding:6px 0;color:#718096">Email</td><td>${params.assessorEmail}</td></tr>
            <tr><td style="padding:6px 0;color:#718096">Valor</td><td><strong style="font-size:18px">${brl(params.amount)}</strong></td></tr>
            <tr><td style="padding:6px 0;color:#718096">Categoria</td><td>${params.category}</td></tr>
            <tr><td style="padding:6px 0;color:#718096">Centro de Custo</td><td>${params.cost_center}</td></tr>
            <tr><td style="padding:6px 0;color:#718096">Data da Despesa</td><td>${params.expense_date}</td></tr>
          </table>
          <div style="margin-top:20px">
            <a href="${env.FRONTEND_URL}/admin.html" style="background:#1a2744;color:#c9a84c;padding:12px 24px;text-decoration:none;border-radius:6px;font-weight:bold">
              Ver no Painel
            </a>
          </div>
        </div>
      </div>`;
  } else {
    const approved = params.status === 'approved';
    subject = `[Reembolso #${params.id}] ${approved ? 'Aprovado' : 'Recusado'} — ${brl(params.amount)}`;
    to = [params.assessorEmail];
    html = `
      <div style="font-family:sans-serif;max-width:600px;margin:0 auto">
        <div style="background:#1a2744;padding:20px;border-radius:8px 8px 0 0">
          <h1 style="color:#c9a84c;margin:0;font-size:20px">Nobel Capital — Reembolsos</h1>
        </div>
        <div style="border:1px solid #e2e8f0;border-top:none;padding:24px;border-radius:0 0 8px 8px">
          <div style="background:${approved ? '#f0fff4' : '#fff5f5'};border-left:4px solid ${approved ? '#48bb78' : '#f56565'};padding:12px 16px;border-radius:4px;margin-bottom:20px">
            <strong style="color:${approved ? '#276749' : '#c53030'};font-size:16px">
              ${approved ? '✓ Pedido Aprovado' : '✗ Pedido Recusado'}
            </strong>
          </div>
          <table style="width:100%;border-collapse:collapse">
            <tr><td style="padding:6px 0;color:#718096">Pedido</td><td><strong>#${params.id}</strong></td></tr>
            <tr><td style="padding:6px 0;color:#718096">Valor</td><td><strong>${brl(params.amount)}</strong></td></tr>
            <tr><td style="padding:6px 0;color:#718096">Categoria</td><td>${params.category}</td></tr>
          </table>
          ${params.reviewer_notes ? `<div style="margin-top:16px;padding:12px;background:#f7fafc;border-radius:4px"><strong>Observação do financeiro:</strong><p style="margin:4px 0 0">${params.reviewer_notes}</p></div>` : ''}
          <div style="margin-top:20px">
            <a href="${env.FRONTEND_URL}/minhas-solicitacoes.html" style="background:#1a2744;color:#c9a84c;padding:12px 24px;text-decoration:none;border-radius:6px;font-weight:bold">
              Ver Minhas Solicitações
            </a>
          </div>
        </div>
      </div>`;
  }

  try {
    await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${env.RESEND_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from: 'Nobel Capital <reembolsos@nobelcapital.com.br>',
        to,
        subject,
        html,
      }),
    });
  } catch (e) {
    console.error('Falha ao enviar email:', e);
  }
}

export { reimbursementRoutes };
