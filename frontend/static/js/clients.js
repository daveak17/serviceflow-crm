let allClients = [];

async function loadClients() {
  try {
    allClients = await api.getClients() || [];
    renderClients(allClients);
  } catch (err) {
    showToast('Failed to load clients', 'error');
  }
}

function filterClients() {
  const query = document.getElementById('client-search').value.toLowerCase().trim();
  if (!query) {
    renderClients(allClients);
    return;
  }
  const filtered = allClients.filter(c =>
    (c.name || '').toLowerCase().includes(query) ||
    (c.company || '').toLowerCase().includes(query) ||
    (c.email || '').toLowerCase().includes(query) ||
    (c.phone || '').toLowerCase().includes(query)
  );
  renderClients(filtered);
}

function renderClients(clients) {
  const tbody = document.getElementById('clients-tbody');
  if (clients.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5"><div class="empty-state">
      <div class="empty-state-icon">◎</div>
      <div class="empty-state-text">No clients found.</div>
    </div></td></tr>`;
    return;
  }
  tbody.innerHTML = clients.map(c => `
    <tr>
      <td><strong>${esc(c.name)}</strong></td>
      <td>${esc(c.company || '—')}</td>
      <td>${esc(c.email || '—')}</td>
      <td>${esc(c.phone || '—')}</td>
      <td>
        <div class="action-btns">
          <button class="btn btn-secondary btn-sm" onclick="openClientModal(${c.id})">Edit</button>
          <button class="btn btn-danger btn-sm" onclick="deleteClient(${c.id})">Delete</button>
        </div>
      </td>
    </tr>`).join('');
}

function openClientModal(id = null) {
  const client = id ? allClients.find(c => c.id === id) : null;
  document.getElementById('modal-title').textContent = client ? 'Edit Client' : 'New Client';
  document.getElementById('modal-body').innerHTML = `
    <div class="form-group">
      <label>Name *</label>
      <input id="c-name" value="${esc(client?.name || '')}" placeholder="Client name" />
    </div>
    <div class="form-row">
      <div class="form-group">
        <label>Company</label>
        <input id="c-company" value="${esc(client?.company || '')}" placeholder="Company name" />
      </div>
      <div class="form-group">
        <label>Email</label>
        <input id="c-email" type="email" value="${esc(client?.email || '')}" placeholder="email@example.com" />
      </div>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label>Phone</label>
        <input id="c-phone" value="${esc(client?.phone || '')}" placeholder="+1 555 0100" />
      </div>
      <div class="form-group">
        <label>Address</label>
        <input id="c-address" value="${esc(client?.address || '')}" placeholder="City, Country" />
      </div>
    </div>
    <div class="form-group">
      <label>Notes</label>
      <textarea id="c-notes">${esc(client?.notes || '')}</textarea>
    </div>
    <div class="modal-footer">
      <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
      <button class="btn btn-primary" onclick="saveClient(${id || 'null'})">
        ${client ? 'Save Changes' : 'Create Client'}
      </button>
    </div>`;
  openModal();
}

async function saveClient(id) {
  const data = {
    name: document.getElementById('c-name').value.trim(),
    company: document.getElementById('c-company').value.trim() || null,
    email: document.getElementById('c-email').value.trim() || null,
    phone: document.getElementById('c-phone').value.trim() || null,
    address: document.getElementById('c-address').value.trim() || null,
    notes: document.getElementById('c-notes').value.trim() || null,
  };
  if (!data.name) { showToast('Name is required', 'error'); return; }
  try {
    if (id) {
      await api.updateClient(id, data);
      showToast('Client updated');
    } else {
      await api.createClient(data);
      showToast('Client created');
    }
    closeModal();
    loadClients();
  } catch (err) {
    showToast(err.detail || 'Failed to save client', 'error');
  }
}

async function deleteClient(id) {
  if (!confirm('Delete this client? This cannot be undone.')) return;
  try {
    await api.deleteClient(id);
    showToast('Client deleted');
    loadClients();
  } catch (err) {
    showToast(err.detail || 'Failed to delete client', 'error');
  }
}