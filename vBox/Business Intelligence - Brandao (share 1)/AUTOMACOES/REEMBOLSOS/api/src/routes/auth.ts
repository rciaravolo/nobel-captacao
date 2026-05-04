import { Hono } from 'hono';
import { AppContext } from '../types';
import { signJWT, verifyJWT, verifyPassword, hashPassword } from '../middleware/auth';

const authRoutes = new Hono<AppContext>();

// POST /api/auth/login
authRoutes.post('/login', async (c) => {
  let body: { email?: string; password?: string };
  try {
    body = await c.req.json();
  } catch {
    return c.json({ error: 'JSON inválido' }, 400);
  }

  const { email, password } = body;
  if (!email || !password) {
    return c.json({ error: 'Email e senha são obrigatórios' }, 400);
  }

  const user = await c.env.DB.prepare(
    'SELECT * FROM users WHERE email = ? AND active = 1'
  ).bind(email.toLowerCase().trim()).first<any>();

  if (!user || !(await verifyPassword(password, user.password_hash))) {
    return c.json({ error: 'Credenciais inválidas' }, 401);
  }

  const token = await signJWT(
    { sub: user.id, email: user.email, name: user.name, role: user.role },
    c.env.JWT_SECRET
  );

  return c.json({
    token,
    user: { id: user.id, name: user.name, email: user.email, role: user.role, team: user.team },
  });
});

// GET /api/auth/me  (requer Bearer token manualmente — rota fora do middleware global)
authRoutes.get('/me', async (c) => {
  const authHeader = c.req.header('Authorization');
  if (!authHeader?.startsWith('Bearer ')) {
    return c.json({ error: 'Não autorizado' }, 401);
  }
  let payload;
  try {
    payload = await verifyJWT(authHeader.slice(7), c.env.JWT_SECRET);
  } catch {
    return c.json({ error: 'Token inválido' }, 401);
  }

  const dbUser = await c.env.DB.prepare(
    'SELECT id, name, email, role, team FROM users WHERE id = ?'
  ).bind(payload.sub).first();

  if (!dbUser) return c.json({ error: 'Usuário não encontrado' }, 404);
  return c.json(dbUser);
});

// POST /api/auth/setup  — cria primeiro usuário financeiro (só funciona se não há usuários)
authRoutes.post('/setup', async (c) => {
  const count = await c.env.DB.prepare(
    'SELECT COUNT(*) as count FROM users'
  ).first<{ count: number }>();

  if ((count?.count ?? 0) > 0) {
    return c.json({ error: 'Setup já realizado. Use o painel para criar usuários.' }, 403);
  }

  let body: { name?: string; email?: string; password?: string };
  try {
    body = await c.req.json();
  } catch {
    return c.json({ error: 'JSON inválido' }, 400);
  }

  const { name, email, password } = body;
  if (!name || !email || !password) {
    return c.json({ error: 'name, email e password são obrigatórios' }, 400);
  }
  if (password.length < 8) {
    return c.json({ error: 'Senha deve ter ao menos 8 caracteres' }, 400);
  }

  const hash = await hashPassword(password);
  await c.env.DB.prepare(
    'INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)'
  ).bind(name.trim(), email.toLowerCase().trim(), hash, 'financeiro').run();

  return c.json({ message: 'Usuário financeiro criado com sucesso. Faça login.' });
});

export { authRoutes };
