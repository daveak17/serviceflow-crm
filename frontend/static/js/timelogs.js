let allTimeLogs = [];
let filteredTimeLogs = [];

async function loadTimeLogs() {
  try {
    const [logs, projects] = await Promise.all([
      api.getTimeLogs(),
      api.getProjects()
    ]);
    allTimeLogs = logs || [];
    allProjects = projects || [];
    populateTimeLogProjectFilter();
    filteredTimeLogs = [...allTimeLogs];
    renderTimeLogs();
  } catch (err) {
    showToast('Failed to load time logs', 'error');
  }
}

function populateTimeLogProjectFilter() {
  const select = document.getElementById('timelog-filter-project');
  select.innerHTML = '<option value="">All Projects</option>' +
    allProjects.map(p => `<option value="${p.id}">${esc(p.name)}</option>`).join('');
}

function filterTimeLogs() {
  const projectId = document.getElementById('timelog-filter-project').value;
  const billable = document.getElementById('timelog-filter-billable').value;

  filteredTimeLogs = allTimeLogs.filter(log => {
    const matchProject = !projectId || log.project_id == projectId;
    const matchBillable = billable === '' || String(log.is_billable) === billable;
    return matchProject && matchBillable;
  });

  renderTimeLogs();
}

function renderTimeLogs() {
  const tbody = document.getElementById('timelogs-tbody');

  if (filteredTimeLogs.length === 0) {
    tbody.innerHTML = `<tr><td colspan="8"><div class="empty-state">
      <div class="empty-state-icon">◷</div>
      <div class="empty-state-text">No time logs yet.</div>
    </div></td></tr>`;
    return;
  }

  let totalHours = 0;
  let totalValue = 0;

  const rows = filteredTimeLogs.map(log => {
    const project = allProjects.find(p => p.id === log.project_id);
    const hours = parseFloat(log.hours);
    const rate = log.hourly_rate ? parseFloat(log.hourly_rate) : null;
    const value = rate ? hours * rate : null;
    totalHours += hours;
    if (value) totalValue += value;

    return `<tr>
      <td>${log.logged_date ? log.logged_date.slice(0,10) : '—'}</td>
      <td>${project ? esc(project.name) : '—'}</td>
      <td>${esc(log.description || '—')}</td>
      <td><strong>${hours.toFixed(2)}h</strong></td>
      <td>${rate ? fmt(rate) + '/h' : '—'}</td>
      <td>${value ? fmt(value) : '—'}</td>
      <td>${log.is_billable
        ? '<span class="badge badge-paid">Billable</span>'
        : '<span class="badge badge-cancelled">Non-billable</span>'}</td>
      <td>
        <div class="action-btns">
          <button class="btn btn-secondary btn-sm" onclick="openTimeLogModal(${log.id})">Edit</button>
          <button class="btn btn-danger btn-sm" onclick="deleteTimeLog(${log.id})">Delete</button>
        </div>
      </td>
    </tr>`;
  });

  // Summary footer row
  rows.push(`<tr style="background:#f9fafb;font-weight:600">
    <td colspan="3" style="text-align:right;padding-right:12px">Total</td>
    <td>${totalHours.toFixed(2)}h</td>
    <td></td>
    <td>${totalValue ? fmt(totalValue) : '—'}</td>
    <td colspan="2"></td>
  </tr>`);

  tbody.innerHTML = rows.join('');
}

function openTimeLogModal(id = null) {
  const log = id ? allTimeLogs.find(l => l.id === id) : null;
  const projectOptions = allProjects.map(p =>
    `<option value="${p.id}" ${log?.project_id === p.id ? 'selected' : ''}>${esc(p.name)}</option>`
  ).join('');

  const today = new Date().toISOString().slice(0, 10);

  document.getElementById('modal-title').textContent = log ? 'Edit Time Log' : 'Log Time';
  document.getElementById('modal-body').innerHTML = `
    <div class="form-group">
      <label>Project *</label>
      <select id="tl-project">
        <option value="">Select project</option>
        ${projectOptions}
      </select>
    </div>
    <div class="form-group">
      <label>Description</label>
      <input id="tl-desc" value="${esc(log?.description || '')}" placeholder="What did you work on?" />
    </div>
    <div class="form-row">
      <div class="form-group">
        <label>Hours *</label>
        <input id="tl-hours" type="number" value="${log?.hours || ''}"
          placeholder="1.5" min="0.01" max="24" step="0.25" />
      </div>
      <div class="form-group">
        <label>Hourly Rate ($)</label>
        <input id="tl-rate" type="number" value="${log?.hourly_rate || ''}"
          placeholder="75.00" min="0" step="0.01" />
      </div>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label>Date</label>
        <input id="tl-date" type="date"
          value="${log?.logged_date ? log.logged_date.slice(0,10) : today}" />
      </div>
      <div class="form-group" style="display:flex;align-items:center;gap:8px;padding-top:24px">
        <input id="tl-billable" type="checkbox" style="width:auto"
          ${log ? (log.is_billable ? 'checked' : '') : 'checked'} />
        <label for="tl-billable" style="margin:0;cursor:pointer">Billable</label>
      </div>
    </div>
    <div class="modal-footer">
      ${log ? `<button class="btn btn-danger" onclick="deleteTimeLog(${log.id}, true)">Delete</button>` : ''}
      <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
      <button class="btn btn-primary" onclick="saveTimeLog(${id || 'null'})">
        ${log ? 'Save Changes' : 'Log Time'}
      </button>
    </div>`;
  openModal();
}

async function saveTimeLog(id) {
  const project_id = document.getElementById('tl-project').value;
  const hours = document.getElementById('tl-hours').value;

  if (!project_id) { showToast('Project is required', 'error'); return; }
  if (!hours || parseFloat(hours) <= 0) { showToast('Hours must be greater than 0', 'error'); return; }

  const data = {
    project_id: parseInt(project_id),
    description: document.getElementById('tl-desc').value.trim() || null,
    hours: parseFloat(hours),
    hourly_rate: document.getElementById('tl-rate').value
      ? parseFloat(document.getElementById('tl-rate').value) : null,
    logged_date: document.getElementById('tl-date').value
      ? document.getElementById('tl-date').value + 'T00:00:00' : null,
    is_billable: document.getElementById('tl-billable').checked,
  };

  try {
    if (id) {
      await api.updateTimeLog(id, data);
      showToast('Time log updated');
    } else {
      await api.createTimeLog(data);
      showToast('Time logged');
    }
    closeModal();
    loadTimeLogs();
  } catch (err) {
    showToast(err.detail || 'Failed to save time log', 'error');
  }
}

async function deleteTimeLog(id, fromModal = false) {
  if (!confirm('Delete this time log?')) return;
  try {
    await api.deleteTimeLog(id);
    showToast('Time log deleted');
    if (fromModal) closeModal();
    loadTimeLogs();
  } catch (err) {
    showToast(err.detail || 'Failed to delete', 'error');
  }
}