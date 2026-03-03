// ── Utilities ──
function fmt(amount) {
  return '$' + parseFloat(amount || 0).toLocaleString('en-US', {
    minimumFractionDigits: 2, maximumFractionDigits: 2
  });
}

function esc(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function badge(status) {
  return `<span class="badge badge-${status}">${status.replace('_', ' ')}</span>`;
}

function showToast(msg, type = 'success') {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.className = `toast ${type}`;
  el.classList.remove('hidden');
  setTimeout(() => el.classList.add('hidden'), 3000);
}

// ── Modal ──
function openModal() {
  document.getElementById('modal-overlay').classList.remove('hidden');
}

function closeModal() {
  document.getElementById('modal-overlay').classList.add('hidden');
}

// ── Navigation ──
async function navigate(page) {
  document.querySelectorAll('.page').forEach(p => {
    p.classList.toggle('active', p.id === 'page-' + page);
    p.classList.toggle('hidden', p.id !== 'page-' + page);
  });
  document.querySelectorAll('.nav-item').forEach(n => {
    n.classList.toggle('active', n.dataset.page === page);
  });

  if (page === 'dashboard') await loadDashboard();
  if (page === 'clients') await loadClients();
  if (page === 'projects') { await loadClients(); await loadProjects(); }
  if (page === 'invoices') { await loadClients(); await loadInvoices(); }
}

// ── Auth Screen ──
function showAuthScreen() {
  document.getElementById('auth-screen').classList.remove('hidden');
  document.getElementById('app').classList.add('hidden');
}

// ── Responsive resize handler ──
let resizeTimer;
window.addEventListener('resize', () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => {
    if (typeof revenueChart !== 'undefined' && revenueChart) revenueChart.resize();
    if (typeof projectChart !== 'undefined' && projectChart) projectChart.resize();
  }, 100);
});

// ── Init App ──
async function initApp() {
  const token = getToken();
  if (!token) { showAuthScreen(); return; }

  document.getElementById('auth-screen').classList.add('hidden');
  document.getElementById('app').classList.remove('hidden');

  const user = getUser();
  if (user) {
    document.getElementById('user-name').textContent = user.full_name;
    document.getElementById('user-email').textContent = user.email;
    document.getElementById('user-avatar').textContent = user.full_name.charAt(0).toUpperCase();
  }

  await navigate('dashboard');
}

// ── Boot ──
initApp();