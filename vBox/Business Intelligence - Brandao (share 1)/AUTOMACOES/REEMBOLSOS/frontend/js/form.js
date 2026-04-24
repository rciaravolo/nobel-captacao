/**
 * form.js — formulário de submissão de reembolso
 * Depende de: config.js, auth.js
 */

document.addEventListener('DOMContentLoaded', () => {
  const user = initNavbar('assessor');
  if (!user) return;

  const form      = document.getElementById('reimbursement-form');
  const alertEl   = document.getElementById('form-alert');
  const submitBtn = document.getElementById('btn-submit');
  const fileInput = document.getElementById('attachment');
  const preview   = document.getElementById('file-preview');
  const previewName = document.getElementById('preview-name');
  const removeBtn = document.getElementById('btn-remove-file');
  const uploadZone = document.getElementById('upload-zone');

  // --- Upload file handling ---
  fileInput.addEventListener('change', handleFileSelect);
  removeBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    clearFile();
  });

  // Drag and drop
  uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('dragover');
  });
  uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('dragover'));
  uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file) {
      const dt = new DataTransfer();
      dt.items.add(file);
      fileInput.files = dt.files;
      handleFileSelect();
    }
  });

  function handleFileSelect() {
    const file = fileInput.files[0];
    if (!file) return clearFile();

    const allowed = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg'];
    if (!allowed.includes(file.type)) {
      showAlert(alertEl, 'Tipo de arquivo não permitido. Use PDF, JPG ou PNG.', 'error');
      clearFile();
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      showAlert(alertEl, 'Arquivo muito grande. Tamanho máximo: 10MB.', 'error');
      clearFile();
      return;
    }

    const icon = file.type === 'application/pdf' ? '📄' : '🖼';
    const size = (file.size / 1024).toFixed(0);
    previewName.textContent = `${icon} ${file.name} (${size} KB)`;
    preview.classList.add('show');
    uploadZone.querySelector('.upload-text').style.display = 'none';
    hideAlert(alertEl);
  }

  function clearFile() {
    fileInput.value = '';
    preview.classList.remove('show');
    uploadZone.querySelector('.upload-text').style.display = '';
  }

  // --- Set today as max date ---
  const dateInput = document.getElementById('expense_date');
  const today = new Date().toISOString().split('T')[0];
  dateInput.setAttribute('max', today);

  // --- Form submit ---
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideAlert(alertEl);

    // Validate file
    if (!fileInput.files[0]) {
      showAlert(alertEl, 'Comprovante obrigatório. Anexe um PDF, JPG ou PNG.', 'error');
      return;
    }

    submitBtn.disabled = true;
    submitBtn.classList.add('btn-loading');
    submitBtn.textContent = 'Enviando...';

    const formData = new FormData(form);
    // Garantir nome correto do campo do arquivo
    formData.set('attachment', fileInput.files[0]);

    try {
      const res = await fetchAPI('/api/reimbursements', {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();

      if (!res.ok) {
        showAlert(alertEl, data.error || 'Erro ao enviar pedido', 'error');
        return;
      }

      // Sucesso
      showAlert(alertEl, `Pedido #${data.id} enviado com sucesso! Você receberá um email de confirmação.`, 'success');
      form.reset();
      clearFile();
      dateInput.setAttribute('max', today);

      // Scroll to top
      window.scrollTo({ top: 0, behavior: 'smooth' });

    } catch (err) {
      if (err.message !== 'Sessão expirada') {
        showAlert(alertEl, 'Erro de conexão. Verifique sua internet e tente novamente.', 'error');
      }
    } finally {
      submitBtn.disabled = false;
      submitBtn.classList.remove('btn-loading');
      submitBtn.textContent = 'Enviar Pedido';
    }
  });
});
