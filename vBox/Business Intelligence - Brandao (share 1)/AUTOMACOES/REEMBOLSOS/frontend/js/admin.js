/**
 * admin.js — painel do financeiro (pendentes + histórico)
 * Depende de: config.js, auth.js
 */

document.addEventListener('DOMContentLoaded', async () => {
  const user = initNavbar('financeiro');
  if (!user) return;

  const listEl      = document.getElementById('reimbursements-list');
  const alertEl     = document.getElementById('page-alert');
  const tabBtns     = document.querySelectorAll('.tab-btn');
  const filterStatus = document.getElementById('filter-status');
  const filterSearch = document.getElementById('filter-search');

  let allData = [];
  let activeStatus = document.body.dataset.initialStatus || 'pending';

  // Marca a tab inicial correta
  tabBtns.forEach(b => b.classList.remove('active'));
  const initialTab = document.querySelector(`.tab-btn[data-status="${activeStatus}"]`);
  if (initialTab) initialTab.classList.add('active');

  await loadData();

  // Tabs
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeStatus = btn.dataset.status;
      if (filterStatus) filterStatus.value = activeStatus === 'all' ? '' : activeStatus;
      renderList();
    });
  });

  // Filtros
  if (filterStatus) filterStatus.addEventListener('change', renderList);
  if (filterSearch) filterSearch.addEventListener('input', renderList);

  async function loadData() {
    listEl.innerHTML = `<tr><td colspan="7"><div class="loading-overlay"><div class="spinner"></div><span>Carregando...</span></div></td></tr>`;
    try {
      const res = await fetchAPI('/api/reimbursements');
      if (!res.ok) throw new Error();
      allData = await res.json();
      updateStats();
      renderList();
    } catch {
      listEl.innerHTML = '';
      showAlert(alertEl, 'Erro ao carregar solicitações. Tente recarregar a página.', 'error');
    }
  }

  function updateStats() {
    const pending  = allData.filter(r => r.status === 'pending').length;
    const approved = allData.filter(r => r.status === 'approved').length;
    const rejected = allData.filter(r => r.status === 'rejected').length;
    const totalBRL = allData
      .filter(r => r.status === 'approved')
      .reduce((sum, r) => sum + r.amount, 0);

    setText('stat-pending',  pending);
    setText('stat-approved', approved);
    setText('stat-rejected', rejected);
    setText('stat-total',    formatBRL(totalBRL));

    // Atualiza contagem nas tabs
    tabBtns.forEach(btn => {
      const s = btn.dataset.status;
      const countEl = btn.querySelector('.tab-count');
      if (!countEl) return;
      const n = s === 'pending' ? pending : s === 'approved' ? approved : s === 'rejected' ? rejected : allData.length;
      countEl.textContent = n;
      countEl.style.display = n > 0 ? '' : 'none';
    });
  }

  function setText(id, val) {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  }

  function getFiltered() {
    let data = allData;

    // Tab filter
    if (activeStatus !== 'all') {
      data = data.filter(r => r.status === activeStatus);
    }

    // Status dropdown filter (histórico page)
    if (filterStatus && filterStatus.value) {
      data = data.filter(r => r.status === filterStatus.value);
    }

    // Search filter
    if (filterSearch && filterSearch.value.trim()) {
      const q = filterSearch.value.trim().toLowerCase();
      data = data.filter(r =>
        (r.user_name || '').toLowerCase().includes(q) ||
        (r.category  || '').toLowerCase().includes(q) ||
        (r.cost_center || '').toLowerCase().includes(q) ||
        String(r.id).includes(q)
      );
    }

    return data;
  }

  function renderList() {
    const filtered = getFiltered();

    if (filtered.length === 0) {
      listEl.innerHTML = `
        <tr><td colspan="7">
          <div class="empty-state">
            <span class="empty-icon">📋</span>
            <div class="empty-title">Nenhuma solicitação encontrada</div>
            <p>${activeStatus === 'pending' ? 'Não há pedidos pendentes de análise.' : 'Nenhum resultado para os filtros aplicados.'}</p>
          </div>
        </td></tr>`;
      return;
    }

    listEl.innerHTML = filtered.map(r => `
      <tr class="clickable" onclick="openModal(${r.id})">
        <td style="font-weight:600;color:var(--text-muted)">#${r.id}</td>
        <td>
          <div style="font-weight:600">${escapeHtml(r.user_name || '—')}</div>
          <div style="font-size:12px;color:var(--text-muted)">${r.user_team || ''}</div>
        </td>
        <td>${formatDate(r.expense_date)}</td>
        <td class="amount-cell">${formatBRL(r.amount)}</td>
        <td>${r.category}</td>
        <td>${r.cost_center}</td>
        <td>${statusBadge(r.status)}</td>
      </tr>`).join('');
  }

  // --- Modal ---
  const modal        = document.getElementById('detail-modal');
  const modalTitle   = document.getElementById('modal-title');
  const modalBody    = document.getElementById('modal-body');
  const closeBtn     = document.getElementById('modal-close');
  const approveBtn   = document.getElementById('btn-approve');
  const rejectBtn    = document.getElementById('btn-reject');
  const reviewSection = document.getElementById('review-section');
  const notesInput   = document.getElementById('reviewer-notes');
  const confirmRejectBtn = document.getElementById('btn-confirm-reject');
  const cancelRejectBtn  = document.getElementById('btn-cancel-reject');
  const modalAlert   = document.getElementById('modal-alert');

  let currentId = null;
  let currentRecord = null;

  window.openModal = async function(id) {
    currentId = id;
    modal.classList.add('open');
    modalTitle.textContent = `Pedido #${id}`;
    modalBody.innerHTML = '<div class="loading-overlay"><div class="spinner"></div></div>';
    setReviewActions(false);

    try {
      const res = await fetchAPI(`/api/reimbursements/${id}`);
      if (!res.ok) throw new Error();
      currentRecord = await res.json();
      renderModalContent(currentRecord);
      setReviewActions(currentRecord.status === 'pending');
    } catch {
      modalBody.innerHTML = `<p style="color:var(--red)">Erro ao carregar detalhes.</p>`;
    }
  };

  function setReviewActions(show) {
    [approveBtn, rejectBtn].forEach(btn => {
      if (btn) btn.style.display = show ? '' : 'none';
    });
    if (reviewSection) reviewSection.style.display = 'none';
  }

  function renderModalContent(r) {
    const reviewInfo = r.status !== 'pending' ? `
      <hr class="divider">
      <div class="detail-grid">
        <div class="detail-label">Revisado por</div>
        <div class="detail-value">${escapeHtml(r.reviewer_name || '—')}</div>
        <div class="detail-label">Data revisão</div>
        <div class="detail-value">${formatDate(r.reviewed_at)}</div>
        ${r.reviewer_notes ? `
        <div class="detail-label">Observação</div>
        <div class="detail-value">${escapeHtml(r.reviewer_notes)}</div>` : ''}
      </div>` : '';

    modalBody.innerHTML = `
      <div style="margin-bottom:16px">${statusBadge(r.status)}</div>
      <div class="detail-grid">
        <div class="detail-label">Solicitante</div>
        <div class="detail-value"><strong>${escapeHtml(r.user_name || '—')}</strong>${r.user_team ? ` <span style="color:var(--text-muted);font-size:12px">— ${r.user_team}</span>` : ''}</div>
        <div class="detail-label">Email</div>
        <div class="detail-value">${escapeHtml(r.user_email || '—')}</div>
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
        📎 Abrir comprovante — ${escapeHtml(r.attachment_name)}
      </button>
      ${reviewInfo}`;
  }

  // Aprovar
  if (approveBtn) {
    approveBtn.addEventListener('click', async () => {
      if (!confirm(`Confirma a aprovação do pedido #${currentId}?`)) return;
      await submitReview('approved', '');
    });
  }

  // Recusar — mostra textarea
  if (rejectBtn) {
    rejectBtn.addEventListener('click', () => {
      reviewSection.style.display = '';
      notesInput.focus();
      rejectBtn.style.display = 'none';
    });
  }

  if (cancelRejectBtn) {
    cancelRejectBtn.addEventListener('click', () => {
      reviewSection.style.display = 'none';
      notesInput.value = '';
      rejectBtn.style.display = '';
    });
  }

  if (confirmRejectBtn) {
    confirmRejectBtn.addEventListener('click', async () => {
      const notes = notesInput.value.trim();
      if (notes.length < 5) {
        showAlert(modalAlert, 'Observação deve ter ao menos 5 caracteres.', 'error');
        return;
      }
      await submitReview('rejected', notes);
    });
  }

  async function submitReview(status, notes) {
    [approveBtn, rejectBtn, confirmRejectBtn, cancelRejectBtn].forEach(b => {
      if (b) b.disabled = true;
    });
    hideAlert(modalAlert);

    try {
      const res = await fetchAPI(`/api/reimbursements/${currentId}/review`, {
        method: 'PATCH',
        body: JSON.stringify({ status, reviewer_notes: notes }),
      });
      const data = await res.json();

      if (!res.ok) {
        showAlert(modalAlert, data.error || 'Erro ao processar revisão', 'error');
        [approveBtn, rejectBtn, confirmRejectBtn, cancelRejectBtn].forEach(b => { if (b) b.disabled = false; });
        return;
      }

      // Atualiza local e fecha modal
      const idx = allData.findIndex(r => r.id === currentId);
      if (idx !== -1) allData[idx].status = status;
      updateStats();
      renderList();
      closeModal();
      showAlert(alertEl, data.message, 'success');
    } catch {
      showAlert(modalAlert, 'Erro de conexão.', 'error');
      [approveBtn, rejectBtn, confirmRejectBtn, cancelRejectBtn].forEach(b => { if (b) b.disabled = false; });
    }
  }

  closeBtn.addEventListener('click', closeModal);
  modal.addEventListener('click', (e) => { if (e.target === modal) closeModal(); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeModal(); });

  function closeModal() {
    modal.classList.remove('open');
    currentId = null;
    currentRecord = null;
    if (reviewSection) { reviewSection.style.display = 'none'; }
    if (notesInput) notesInput.value = '';
    hideAlert(modalAlert);
  }
});

function escapeHtml(str) {
  const d = document.createElement('div');
  d.textContent = str || '';
  return d.innerHTML;
}
