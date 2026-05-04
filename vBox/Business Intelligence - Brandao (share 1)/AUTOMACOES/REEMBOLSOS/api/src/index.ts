import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { AppContext } from './types';
import { authMiddleware } from './middleware/auth';
import { authRoutes } from './routes/auth';
import { reimbursementRoutes } from './routes/reimbursements';
import { userRoutes } from './routes/users';

const app = new Hono<AppContext>();

// CORS — restringir ao domínio do Pages em produção
app.use('*', cors({
  origin: '*',
  allowMethods: ['GET', 'POST', 'PATCH', 'DELETE', 'OPTIONS'],
  allowHeaders: ['Content-Type', 'Authorization'],
  maxAge: 86400,
}));

// Health check
app.get('/', (c) => c.json({
  status: 'ok',
  service: 'Reembolsos Nobel Capital API',
  version: '1.0.0',
}));

// Rotas públicas (login, setup)
app.route('/api/auth', authRoutes);

// Middleware de autenticação para todas as rotas /api/* abaixo
app.use('/api/reimbursements/*', authMiddleware);
app.use('/api/users/*', authMiddleware);

// Rotas protegidas
app.route('/api/reimbursements', reimbursementRoutes);
app.route('/api/users', userRoutes);

// 404
app.notFound((c) => c.json({ error: 'Rota não encontrada' }, 404));

// Handler de erros
app.onError((err, c) => {
  console.error('Erro não tratado:', err);
  return c.json({ error: 'Erro interno do servidor' }, 500);
});

export default app;
