const BASE_URL = '';

function getToken() {
  return localStorage.getItem('sf_token');
}

function setToken(token) {
  localStorage.setItem('sf_token', token);
}

function clearToken() {
  localStorage.removeItem('sf_token');
  localStorage.removeItem('sf_user');
}

function setUser(user) {
  localStorage.setItem('sf_user', JSON.stringify(user));
}

function getUser() {
  const u = localStorage.getItem('sf_user');
  return u ? JSON.parse(u) : null;
}

async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers });

  if (res.status === 401) {
    clearToken();
    showAuthScreen();
    return null;
  }

  if (res.status === 204) return { ok: true };

  const data = await res.json();
  if (!res.ok) throw { status: res.status, detail: data.detail || 'An error occurred' };
  return data;
}

const api = {
  // Auth
  login: (email, password) =>
    apiFetch('/api/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),
  register: (full_name, email, password) =>
    apiFetch('/api/auth/register', { method: 'POST', body: JSON.stringify({ full_name, email, password }) }),
  me: () => apiFetch('/api/auth/me'),

  // Clients
  getClients: () => apiFetch('/api/clients'),
  createClient: (data) => apiFetch('/api/clients', { method: 'POST', body: JSON.stringify(data) }),
  updateClient: (id, data) => apiFetch(`/api/clients/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteClient: (id) => apiFetch(`/api/clients/${id}`, { method: 'DELETE' }),

  // Projects
  getProjects: () => apiFetch('/api/projects'),
  createProject: (data) => apiFetch('/api/projects', { method: 'POST', body: JSON.stringify(data) }),
  updateProject: (id, data) => apiFetch(`/api/projects/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteProject: (id) => apiFetch(`/api/projects/${id}`, { method: 'DELETE' }),

  // Invoices
  getInvoices: () => apiFetch('/api/invoices'),
  createInvoice: (data) => apiFetch('/api/invoices', { method: 'POST', body: JSON.stringify(data) }),
  updateInvoice: (id, data) => apiFetch(`/api/invoices/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteInvoice: (id) => apiFetch(`/api/invoices/${id}`, { method: 'DELETE' }),
  getInvoiceSummary: (id) => apiFetch(`/api/invoices/${id}/summary`),
  addPayment: (id, data) => apiFetch(`/api/invoices/${id}/payments`, { method: 'POST', body: JSON.stringify(data) }),

  // Analytics
  getDashboard: () => apiFetch('/api/analytics/dashboard'),
  getMonthlyRevenue: () => apiFetch('/api/analytics/revenue/monthly?months=6'),
};