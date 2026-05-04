import { Hono } from 'hono';
import { AppContext } from '../types';
import { hashPassword } from '../middleware/auth';

const userRoutes = new Hono<AppContext>();

// GET /api/users — lista todos os usuários (financeiro only)
userRoutes.get('/', async (c) => {
  const user = c.get('user');
  if (user.role !== 'financeiro') return c.json({ error: 'Acesso negado' }, 403);

  const { results } = await c.env.DB.prepare(
    'SELECT id, name, email, role, team, active, created_at FROM users ORDER BY name'
  ).all();

  return c.json(results);
});

// POST /api/users — cria novo usuário (financeiro only)
userRoutes.post('/', async (c) => {
  const user = c.get('user');
  if (user.role !== 'financeiro') return c.json({ error: 'Acesso negado' }, 403);

  let body: { name?: string; email?: string; password?: string; role?: string; team?: string };
  try {
    body = await c.req.json();
  } catch {
    return c.json({ error: 'JSON inválido' }, 400);
  }

  const { name, email, password, role, team } = body;
  if (!name || !email || !password || !role) {
    return c.json({ error: 'name, email, password e role são obrigatórios' }, 400);
  }
  if (!['assessor', 'financeiro'].includes(role)) {
    return c.json({ error: 'Role inválido' }, 400);
  }
  if (password.length < 8) {
    return c.json({ error: 'Senha deve ter ao menos 8 caracteres' }, 400);
  }

  const existing = await c.env.DB.prepare(
    'SELECT id FROM users WHERE email = ?'
  ).bind(email.toLowerCase().trim()).first();

  if (existing) return c.json({ error: 'Email já cadastrado' }, 409);

  const hash = await hashPassword(password);
  const result = await c.env.DB.prepare(
    'INSERT INTO users (name, email, password_hash, role, team) VALUES (?, ?, ?, ?, ?)'
  ).bind(name.trim(), email.toLowerCase().trim(), hash, role, team?.trim() || null).run();

  return c.json({ id: result.meta.last_row_id, message: 'Usuário criado com sucesso' }, 201);
});

// PATCH /api/users/:id/toggle — ativa/desativa usuário (financeiro only)
userRoutes.patch('/:id/toggle', async (c) => {
  const user = c.get('user');
  if (user.role !== 'financeiro') return c.json({ error: 'Acesso negado' }, 403);

  const id = parseInt(c.req.param('id'));
  if (isNaN(id)) return c.json({ error: 'ID inválido' }, 400);

  const target = await c.env.DB.prepare(
    'SELECT id, active FROM users WHERE id = ?'
  ).bind(id).first<any>();

  if (!target) return c.json({ error: 'Usuário não encontrado' }, 404);
  if (target.id === user.sub) return c.json({ error: 'Não é possível desativar sua própria conta' }, 400);

  await c.env.DB.prepare(
    'UPDATE users SET active = ? WHERE id = ?'
  ).bind(target.active ? 0 : 1, id).run();

  return c.json({ message: `Usuário ${target.active ? 'desativado' : 'ativado'} com sucesso` });
});

// PATCH /api/users/:id/password — troca senha (financeiro only)
userRoutes.patch('/:id/password', async (c) => {
  const user = c.get('user');
  if (user.role !== 'financeiro') return c.json({ error: 'Acesso negado' }, 403);

  const id = parseInt(c.req.param('id'));
  let body: { password?: string };
  try {
    body = await c.req.json();
  } catch {
    return c.json({ error: 'JSON inválido' }, 400);
  }

  if (!body.password || body.password.length < 8) {
    return c.json({ error: 'Senha deve ter ao menos 8 caracteres' }, 400);
  }

  const target = await c.env.DB.prepare('SELECT id FROM users WHERE id = ?').bind(id).first();
  if (!target) return c.json({ error: 'Usuário não encontrado' }, 404);

  const hash = await hashPassword(body.password);
  await c.env.DB.prepare('UPDATE users SET password_hash = ? WHERE id = ?').bind(hash, id).run();

  return c.json({ message: 'Senha atualizada com sucesso' });
});

export { userRoutes };
