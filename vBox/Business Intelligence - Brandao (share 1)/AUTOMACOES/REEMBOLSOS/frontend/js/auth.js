/**
 * auth.js — helpers de autenticação compartilhados por todas as páginas.
 * Depende de: config.js (API_BASE_URL)
 */

const TOKEN_KEY = 'nobel_reembolsos_token';
const USER_KEY  = 'nobel_reembolsos_user';

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function getUser() {
  const raw = localStorage.getItem(USER_KEY);
  try { return raw ? JSON.parse(raw) : null; } catch { return null; }
}

function setAuth(token, user) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

function clearAuth() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

function isAuthenticated() {
  return !!getToken();
}

/**
 * Redireciona para login se não autenticado.
 * @param {'assessor'|'financeiro'|null} requiredRole — null = qualquer role
 */
function requireAuth(requiredRole = null) {
  if (!isAuthenticated()) {
    window.location.href = '/login.html';
    return null;
  }
  const user = getUser();
  if (requiredRole && user?.role !== requiredRole) {
    // Redireciona para a área correta
    if (user?.role === 'financeiro') {
      window.location.href = '/admin.html';
    } else {
      window.location.href = '/form.html';
    }
    return null;
  }
  return user;
}

/**
 * Faz fetch autenticado para a API.
 * Retorna o Response. Lança erro se 401 (redireciona para login).
 */
async function fetchAPI(path, options = {}) {
  const token = getToken();
  const headers = {
    ...(options.headers || {}),
    'Authorization': `Bearer ${token}`,
  };

  // Não definir Content-Type para FormData (o browser define com boundary)
  if (!(options.body instanceof FormData)) {
    if (!headers['Content-Type'] && options.body) {
      headers['Content-Type'] = 'application/json';
    }
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    clearAuth();
    window.location.href = '/login.html';
    throw new Error('Sessão expirada');
  }

  return response;
}

/**
 * Preenche o navbar com dados do usuário logado.
 * @param {'assessor'|'financeiro'|null} requiredRole
 */
function initNavbar(requiredRole = null) {
  const user = requireAuth(requiredRole);
  if (!user) return null;

  const nameEl = document.getElementById('navbar-user-name');
  const roleEl = document.getElementById('navbar-user-role');
  const logoutBtn = document.getElementById('btn-logout');

  if (nameEl) nameEl.textContent = user.name;
  if (roleEl) roleEl.textContent = user.role === 'financeiro' ? 'Financeiro' : 'Assessor';
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      clearAuth();
      window.location.href = '/login.html';
    });
  }

  return user;
}

/** Formata valor em BRL */
function formatBRL(value) {
  return Number(value).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

/** Formata data ISO para dd/mm/aaaa */
function formatDate(isoStr) {
  if (!isoStr) return '—';
  const d = isoStr.substring(0, 10); // "2025-04-01"
  const [y, m, day] = d.split('-');
  return `${day}/${m}/${y}`;
}

/** Retorna badge HTML por status */
function statusBadge(status) {
  const map = {
    pending:  { cls: 'badge-pending',  label: 'Pendente' },
    approved: { cls: 'badge-approved', label: 'Aprovado' },
    rejected: { cls: 'badge-rejected', label: 'Recusado' },
  };
  const { cls, label } = map[status] || { cls: '', label: status };
  return `<span class="badge ${cls}">${label}</span>`;
}

/** Abre anexo em nova aba (via Blob para passar o token) */
async function openAttachment(id) {
  try {
    const res = await fetchAPI(`/api/reimbursements/${id}/attachment`);
    if (!res.ok) throw new Error('Erro ao carregar anexo');
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    window.open(url, '_blank');
    // Revoga após 60s para liberar memória
    setTimeout(() => URL.revokeObjectURL(url), 60000);
  } catch (e) {
    alert('Não foi possível abrir o comprovante: ' + e.message);
  }
}

/** Mostra alerta numa div */
function showAlert(el, message, type = 'error') {
  el.className = `alert alert-${type} show`;
  el.textContent = message;
  el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function hideAlert(el) {
  el.className = 'alert';
  el.textContent = '';
}
