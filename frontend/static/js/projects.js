let allProjects = [];

async function loadProjects() {
  try {
    const [projects, clients] = await Promise.all([
      api.getProjects(),
      api.getClients()
    ]);
    allProjects = projects || [];
    allClients = clients || [];
    renderProjects();
  } catch (err) {
    showToast('Failed to load projects', 'error');
  }
}

function renderProjects() {
  const grid = document.getElementById('projects-grid');
  if (allProjects.length === 0) {
    grid.innerHTML = `<div class="empty-state" style="grid-column:1/-1">
      <div class="empty-state-icon">◈</div>
      <div class="empty-state-text">No projects yet. Create your first project.</div>
    </div>`;
    return;
  }
  grid.innerHTML = allProjects.map(p => `
    <div class="project-card">
      <div class="project-card-header">
        <div>
          <div class="project-name">${esc(p.name)}</div>
          <div class="project-client">${p.client_id ? (allClients.find(c => c.id === p.client_id)?.name || 'Client #' + p.client_id) : 'No client'}</div>
        </div>
        ${badge(p.status)}
      </div>
      <div style="font-size:13px;color:var(--text-secondary);min-height:36px">
        ${esc(p.description || 'No description')}
      </div>
      <div class="project-meta">
        ${p.budget ? '<span>Budget: ' + fmt(p.budget) + '</span>' : ''}
        ${p.deadline ? '<span>Due: ' + p.deadline.slice(0,10) + '</span>' : ''}
      </div>
      <div class="project-actions">
        <button class="btn btn-secondary btn-sm" onclick="openProjectModal(${p.id})">Edit</button>
        <button class="btn btn-danger btn-sm" onclick="deleteProject(${p.id})">Delete</button>
      </div>
    </div>`).join('');
}

function openProjectModal(id = null) {
  const project = id ? allProjects.find(p => p.id === id) : null;
  const clientOptions = allClients.map(c =>
    `<option value="${c.id}" ${project?.client_id === c.id ? 'selected' : ''}>${esc(c.name)}</option>`
  ).join('');

  document.getElementById('modal-title').textContent = project ? 'Edit Project' : 'New Project';
  document.getElementById('modal-body').innerHTML = `
    <div class="form-group">
      <label>Project Name *</label>
      <input id="p-name" value="${esc(project?.name || '')}" placeholder="Project name" />
    </div>
    <div class="form-group">
      <label>Client</label>
      <select id="p-client">
        <option value="">No client</option>
        ${clientOptions}
      </select>
    </div>
    <div class="form-group">
      <label>Description</label>
      <textarea id="p-desc">${esc(project?.description || '')}</textarea>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label>Status</label>
        <select id="p-status">
          ${['active','on_hold','completed','cancelled'].map(s =>
            `<option value="${s}" ${project?.status === s ? 'selected' : ''}>${s.replace('_',' ')}</option>`
          ).join('')}
        </select>
      </div>
      <div class="form-group">
        <label>Budget ($)</label>
        <input id="p-budget" type="number" value="${project?.budget || ''}" placeholder="0.00" />
      </div>
    </div>
    <div class="form-group">
      <label>Deadline</label>
      <input id="p-deadline" type="date" value="${project?.deadline ? project.deadline.slice(0,10) : ''}" />
    </div>
    <div class="modal-footer">
      <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
      <button class="btn btn-primary" onclick="saveProject(${id || 'null'})">
        ${project ? 'Save Changes' : 'Create Project'}
      </button>
    </div>`;
  openModal();
}

async function saveProject(id) {
  const name = document.getElementById('p-name').value.trim();
  if (!name) { showToast('Name is required', 'error'); return; }

  const data = {
    name,
    client_id: document.getElementById('p-client').value || null,
    description: document.getElementById('p-desc').value.trim() || null,
    status: document.getElementById('p-status').value,
    budget: document.getElementById('p-budget').value || null,
    deadline: document.getElementById('p-deadline').value
      ? document.getElementById('p-deadline').value + 'T00:00:00' : null,
  };

  try {
    if (id) {
      await api.updateProject(id, data);
      showToast('Project updated');
    } else {
      await api.createProject(data);
      showToast('Project created');
    }
    closeModal();
    loadProjects();
  } catch (err) {
    showToast(err.detail || 'Failed to save project', 'error');
  }
}

async function deleteProject(id) {
  if (!confirm('Delete this project?')) return;
  try {
    await api.deleteProject(id);
    showToast('Project deleted');
    loadProjects();
  } catch (err) {
    showToast(err.detail || 'Failed to delete', 'error');
  }
}