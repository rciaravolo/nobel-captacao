function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
  });
}
function err(msg, status = 400) { return json({ error: msg }, status); }

function timeToMinutes(t) {
  const [h, m] = t.split(':').map(Number);
  return h * 60 + m;
}

function computeBets(bets, result, type) {
  if (!bets || bets.length === 0) return [];
  if (type === 'time') {
    const real = timeToMinutes(result);
    const diffs = bets.map(b => {
      let d = Math.abs(timeToMinutes(b.bet_value) - real);
      if (d > 720) d = 1440 - d;
      return { ...b, diff: d };
    });
    const minD = Math.min(...diffs.map(d => d.diff));
    return diffs.map(d => {
      const closest = d.diff === minD;
      const points = closest ? (d.diff <= 3 ? 3 : 1) : (d.diff <= 3 ? 1 : 0);
      return { ...d, points, is_closest: closest ? 1 : 0 };
    });
  } else {
    const real = parseInt(result);
    const diffs = bets.map(b => ({ ...b, diff: Math.abs(parseInt(b.bet_value) - real) }));
    const minD = Math.min(...diffs.map(d => d.diff));
    return diffs.map(d => ({
      ...d,
      points: d.diff === minD ? 3 : d.diff <= 1 ? 1 : 0,
      is_closest: d.diff === minD ? 1 : 0,
    }));
  }
}

async function hashPassword(salt, password) {
  const data = new TextEncoder().encode(salt + password);
  const buf = await crypto.subtle.digest('SHA-256', data);
  return Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('');
}

async function getSession(request, env) {
  const token = request.headers.get('Authorization')?.replace('Bearer ', '').trim();
  if (!token) return null;
  return env.DB.prepare(
    `SELECT s.token, u.id as user_id, u.participant_id, u.username, u.is_master
     FROM sessions s JOIN users u ON s.user_id = u.id
     WHERE s.token = ? AND s.expires_at > datetime('now')`
  ).bind(token).first();
}

export async function onRequest(context) {
  const { request, env, params } = context;

  if (request.method === 'OPTIONS') {
    return new Response(null, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      },
    });
  }

  const path = params.path || [];
  const method = request.method;

  // ── AUTH ROUTES ─────────────────────────────────────────────────────────────
  if (path[0] === 'auth') {
    const action = path[1];

    if (method === 'POST' && action === 'login') {
      const body = await request.json().catch(() => ({}));
      const { username, password } = body;
      if (!username || !password) return err('Dados incompletos');
      const user = await env.DB.prepare('SELECT * FROM users WHERE username = ?').bind(username.toLowerCase()).first();
      if (!user) return err('Usuário ou senha inválidos', 401);
      const hash = await hashPassword(user.salt, password);
      if (hash !== user.password_hash) return err('Usuário ou senha inválidos', 401);
      const token = crypto.randomUUID();
      const expires = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString();
      await env.DB.prepare('INSERT INTO sessions (token, user_id, expires_at) VALUES (?, ?, ?)').bind(token, user.id, expires).run();
      const participant = await env.DB.prepare('SELECT name FROM participants WHERE id = ?').bind(user.participant_id).first();
      return json({ token, name: participant?.name || user.username, is_master: user.is_master, participant_id: user.participant_id });
    }

    if (method === 'POST' && action === 'logout') {
      const session = await getSession(request, env);
      if (session) await env.DB.prepare('DELETE FROM sessions WHERE token = ?').bind(session.token).run();
      return json({ success: true });
    }

    if (method === 'GET' && action === 'me') {
      const session = await getSession(request, env);
      if (!session) return err('Não autenticado', 401);
      const participant = await env.DB.prepare('SELECT name FROM participants WHERE id = ?').bind(session.participant_id).first();
      return json({ name: participant?.name || session.username, is_master: session.is_master, participant_id: session.participant_id });
    }

    return err('Not found', 404);
  }

  // ── CHAMPIONSHIP ROUTES ──────────────────────────────────────────────────────
  const [slug, resource, resourceId, subResource] = path;
  if (!slug) return err('Missing slug', 404);

  const champ = await env.DB.prepare('SELECT * FROM championships WHERE slug = ?').bind(slug).first();
  if (!champ) return err('Championship not found', 404);

  const session = await getSession(request, env);
  const isMaster = session?.is_master === 1;
  const isAuthed = !!session;

  // GET /api/:slug/state
  if (method === 'GET' && resource === 'state') {
    const [participants, rounds, bets] = await Promise.all([
      env.DB.prepare('SELECT * FROM participants WHERE championship_id = ? ORDER BY created_at').bind(champ.id).all(),
      env.DB.prepare('SELECT * FROM rounds WHERE championship_id = ? ORDER BY number').bind(champ.id).all(),
      env.DB.prepare('SELECT b.* FROM bets b JOIN rounds r ON b.round_id = r.id WHERE r.championship_id = ?').bind(champ.id).all(),
    ]);
    const roundsWithBets = rounds.results.map(r => ({
      ...r,
      bets: bets.results.filter(b => b.round_id === r.id).map(b => {
        if (r.status === 'open') {
          const isOwn = session && b.participant_id === session.participant_id;
          return { participant_id: b.participant_id, has_bet: true, bet_value: isOwn ? b.bet_value : null };
        }
        return b;
      }),
    }));
    return json({ championship: champ, participants: participants.results, rounds: roundsWithBets });
  }

  // POST /api/:slug/rounds — master abre nova rodada
  if (method === 'POST' && resource === 'rounds' && !resourceId) {
    if (!isMaster) return err('Unauthorized', 401);
    const openRound = await env.DB.prepare("SELECT id FROM rounds WHERE championship_id = ? AND status = 'open'").bind(champ.id).first();
    if (openRound) return err('Já existe uma rodada em aberto');
    const { number, date, leave_time } = await request.json().catch(() => ({}));
    if (!date || !leave_time) return err('Informe data e horário de saída');
    const roundId = crypto.randomUUID();
    await env.DB.prepare(
      "INSERT INTO rounds (id, championship_id, number, date, leave_time, result, status, created_at) VALUES (?, ?, ?, ?, ?, '', 'open', ?)"
    ).bind(roundId, champ.id, number || 1, date, leave_time, new Date().toISOString()).run();
    return json({ success: true, roundId });
  }

  // POST /api/:slug/rounds/:id/bet — usuário envia palpite
  if (method === 'POST' && resource === 'rounds' && resourceId && subResource === 'bet') {
    if (!isAuthed) return err('Faça login para apostar', 401);
    const round = await env.DB.prepare("SELECT * FROM rounds WHERE id = ? AND championship_id = ? AND status = 'open'").bind(resourceId, champ.id).first();
    if (!round) return err('Rodada não encontrada ou já encerrada');
    const { bet_value } = await request.json().catch(() => ({}));
    if (!bet_value) return err('Informe seu palpite');
    const existing = await env.DB.prepare('SELECT id FROM bets WHERE round_id = ? AND participant_id = ?').bind(resourceId, session.participant_id).first();
    if (existing) {
      await env.DB.prepare('UPDATE bets SET bet_value = ? WHERE id = ?').bind(bet_value, existing.id).run();
    } else {
      await env.DB.prepare(
        'INSERT INTO bets (id, round_id, participant_id, bet_value, diff_value, points, is_closest, created_at) VALUES (?, ?, ?, ?, NULL, 0, 0, ?)'
      ).bind(crypto.randomUUID(), resourceId, session.participant_id, bet_value, new Date().toISOString()).run();
    }
    return json({ success: true });
  }

  // POST /api/:slug/rounds/:id/close — master encerra rodada e calcula pontos
  if (method === 'POST' && resource === 'rounds' && resourceId && subResource === 'close') {
    if (!isMaster) return err('Unauthorized', 401);
    const round = await env.DB.prepare("SELECT * FROM rounds WHERE id = ? AND championship_id = ? AND status = 'open'").bind(resourceId, champ.id).first();
    if (!round) return err('Rodada não encontrada ou já encerrada');
    const { result } = await request.json().catch(() => ({}));
    if (!result) return err('Informe o horário de chegada');
    const bets = await env.DB.prepare('SELECT * FROM bets WHERE round_id = ?').bind(resourceId).all();
    if (bets.results.length > 0) {
      const computed = computeBets(bets.results, result, champ.type);
      const updateStmt = env.DB.prepare('UPDATE bets SET diff_value = ?, points = ?, is_closest = ? WHERE id = ?');
      await env.DB.batch(computed.map(b => updateStmt.bind(b.diff, b.points, b.is_closest, b.id)));
    }
    await env.DB.prepare("UPDATE rounds SET status = 'closed', result = ? WHERE id = ?").bind(result, resourceId).run();
    return json({ success: true });
  }

  // DELETE /api/:slug/rounds/:id
  if (method === 'DELETE' && resource === 'rounds' && resourceId) {
    if (!isMaster) return err('Unauthorized', 401);
    await env.DB.prepare('DELETE FROM rounds WHERE id = ? AND championship_id = ?').bind(resourceId, champ.id).run();
    return json({ success: true });
  }

  // POST /api/:slug/participants
  if (method === 'POST' && resource === 'participants') {
    if (!isMaster) return err('Unauthorized', 401);
    const { name } = await request.json().catch(() => ({}));
    if (!name) return err('Missing name');
    const id = crypto.randomUUID();
    await env.DB.prepare('INSERT INTO participants VALUES (?, ?, ?, ?)').bind(id, champ.id, name, new Date().toISOString()).run();
    return json({ success: true, id });
  }

  // DELETE /api/:slug/participants/:id
  if (method === 'DELETE' && resource === 'participants' && resourceId) {
    if (!isMaster) return err('Unauthorized', 401);
    await env.DB.prepare('DELETE FROM participants WHERE id = ? AND championship_id = ?').bind(resourceId, champ.id).run();
    return json({ success: true });
  }

  // DELETE /api/:slug/reset
  if (method === 'DELETE' && resource === 'reset') {
    if (!isMaster) return err('Unauthorized', 401);
    await env.DB.prepare('DELETE FROM rounds WHERE championship_id = ?').bind(champ.id).run();
    await env.DB.prepare('DELETE FROM participants WHERE championship_id = ?').bind(champ.id).run();
    return json({ success: true });
  }

  return err('Not found', 404);
}
