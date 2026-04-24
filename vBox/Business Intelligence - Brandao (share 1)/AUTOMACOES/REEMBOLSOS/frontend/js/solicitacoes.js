/**
 * solicitacoes.js — histórico de pedidos do assessor
 * Depende de: config.js, auth.js
 */

document.addEventListener('DOMContentLoaded', async () => {
  const user = initNavbar('assessor');
  if (!user) return;

  const listEl    = document.getElementById('reimbursements-list');
  const alertEl   = document.getElementById('page-alert');
  const tabBtns   = document.querySelectorAll('.tab-btn');

  let allData = [];
  let activeStatus = 'all';

  await loadData();

  // Tabs
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeStatus = btn.dataset.status;
      renderList();
    });
  });

  async function loadData() {
    listEl.innerHTML = `<tr><td colspan="6"><div class="loading-overlay"><div class="spinner"></div><span>Carregando...</span></div></td></tr>`;
    try {
      const res = await fetchAPI('/api/reimbursements');
      if (!res.ok) throw new Error('Erro ao carregar dados');
      allData = await res.json();
      updateCounts();
      renderList();
    } catch (e) {
      if (e.message !== 'Sessão expirada') {
        listEl.innerHTML = '';
        showAlert(alertEl, 'Erro ao carregar solicitações. Tente recarregar a página.', 'error');
      }
    }
  }

  function updateCounts() {
    const counts = { all: allData.length, pending: 0, approved: 0, rejected: 0 };
    allData.forEach(r => counts[r.status]++);
    tabBtns.forEach(btn => {
      const s = btn.dataset.status;
      const countEl = btn.querySelector('.tab-count');
      if (countEl) {
        const n = counts[s] || 0;
        countEl.textContent = n;
        countEl.style.display = n > 0 ? '' : 'none';
      }
    });
  }

  function renderList() {
    const filtered = activeStatus === 'all'
      ? allData
      : allData.filter(r => r.status === activeStatus);

    if (filtered.length === 0) {
      listEl.innerHTML = `
        <tr><td colspan="6">
          <div class="empty-state">
            <span class="empty-icon">📋</span>
            <div class="empty-title">Nenhuma solicitação encontrada</div>
            <p>${activeStatus === 'all' ? 'Você ainda não enviou pedidos de reembolso.' : 'Nenhum pedido neste status.'}</p>
          </div>
        </td></tr>`;
      return;
    }

    listEl.innerHTML = filtered.map(r => `
      <tr class="clickable" onclick="openModal(${r.id})">
        <td>${formatDate(r.expense_date)}</td>
        <td>${r.category}</td>
        <td>${r.cost_center}</td>
        <td class="amount-cell">${formatBRL(r.amount)}</td>
        <td>${statusBadge(r.status)}</td>
        <td style="color:var(--text-muted);font-size:13px">${formatDate(r.created_at)}</td>
      </tr>`).join('');
  }

  // --- Modal ---
  const modal     = document.getElementById('detail-modal');
  const modalBody = document.getElementById('modal-body');
  const closeBtn  = document.getElementById('modal-close');

  window.openModal = async function(id) {
    modal.classList.add('open');
    modalBody.innerHTML = '<div class="loading-overlay"><div class="spinner"></div></div>';

    try {
      const res = await fetchAPI(`/api/reimbursements/${id}`);
      if (!res.ok) throw new Error('Erro ao carregar detalhes');
      const r = await res.json();
      renderModalContent(r);
    } catch (e) {
      modalBody.innerHTML = `<p style="color:var(--red)">Erro ao carregar detalhes.</p>`;
    }
  };

  function renderModalContent(r) {
    const reviewSection = r.status !== 'pending' ? `
      <hr class="divider">
      <div class="detail-grid">
        <div class="detail-label">Revisado por</div>
        <div class="detail-value">${r.reviewer_name || '—'}</div>
        <div class="detail-label">Data revisão</div>
        <div class="detail-value">${formatDate(r.reviewed_at)}</div>
        ${r.reviewer_notes ? `
        <div class="detail-label">Observação</div>
        <div class="detail-value">${escapeHtml(r.reviewer_notes)}</div>` : ''}
      </div>` : '';

    modalBody.innerHTML = `
      <div style="margin-bottom:16px">${statusBadge(r.status)}</div>
      <div class="detail-grid">
        <div class="detail-label">Data da despesa</div>
        <div class="detail-value">${formatDate(r.expense_date)}</div>
        <div class="detail-label">Valor</div>
        <div class="detail-value amount">${formatBRL(r.amount)}</div>
        <div class="detail-label">Categoria</div>
        <div class="detail-value">${r.category}</div>
        <div class="detail-label">Centro de Custo</div>
        <div class="detail-value">${r.cost_center}</div>
        <div class="detail-label">Descrição</div>
        <div class="detail-value">${escapeHtml(r.description)}</div>
        <div class="detail-label">Enviado em</div>
        <div class="detail-value">${formatDate(r.created_at)}</div>
      </div>
      <button class="attachment-link" onclick="openAttachment(${r.id})">
        📎 Ver comprovante — ${escapeHtml(r.attachment_name)}
      </button>
      ${reviewSection}`;
  }

  closeBtn.addEventListener('click', closeModal);
  modal.addEventListener('click', (e) => { if (e.target === modal) closeModal(); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeModal(); });

  function closeModal() {
    modal.classList.remove('open');
  }
});

function escapeHtml(str) {
  const d = document.createElement('div');
  d.textContent = str;
  return d.innerHTML;
}
