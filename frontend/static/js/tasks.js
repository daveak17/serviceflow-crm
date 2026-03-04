let allTasks = [];
let filteredTasks = [];

async function loadTasks() {
  try {
    const [tasks, projects] = await Promise.all([
      api.getTasks(),
      api.getProjects()
    ]);
    allTasks = tasks || [];
    allProjects = projects || [];
    populateTaskProjectFilter();
    filteredTasks = [...allTasks];
    renderTaskBoard();
  } catch (err) {
    showToast('Failed to load tasks', 'error');
  }
}

function populateTaskProjectFilter() {
  const select = document.getElementById('task-filter-project');
  select.innerHTML = '<option value="">All Projects</option>' +
    allProjects.map(p => `<option value="${p.id}">${esc(p.name)}</option>`).join('');
}

function filterTasks() {
  const projectId = document.getElementById('task-filter-project').value;
  const status = document.getElementById('task-filter-status').value;

  filteredTasks = allTasks.filter(t => {
    const matchProject = !projectId || t.project_id == projectId;
    const matchStatus = !status || t.status === status;
    return matchProject && matchStatus;
  });

  renderTaskBoard();
}

function renderTaskBoard() {
  const cols = { todo: [], in_progress: [], done: [] };

  filteredTasks.forEach(task => {
    if (cols[task.status]) cols[task.status].push(task);
  });

  ['todo', 'in_progress', 'done'].forEach(status => {
    const col = document.getElementById('col-' + status);
    if (cols[status].length === 0) {
      col.innerHTML = `<div class="task-col-empty">No tasks</div>`;
      return;
    }
    col.innerHTML = cols[status].map(task => {
      const project = allProjects.find(p => p.id === task.project_id);
      return `
        <div class="task-card priority-${task.priority}" onclick="openTaskModal(${task.id})">
          <div class="task-card-project">${project ? esc(project.name) : 'Unknown project'}</div>
          <div class="task-card-title">${esc(task.title)}</div>
          ${task.description ? `<div style="font-size:12px;color:var(--text-secondary)">${esc(task.description)}</div>` : ''}
          <div class="task-card-meta">
            ${badge(task.priority)}
            ${task.due_date ? `<span style="font-size:11px;color:var(--text-secondary)">Due ${task.due_date.slice(0,10)}</span>` : ''}
          </div>
        </div>`;
    }).join('');
  });
}

function openTaskModal(id = null) {
  const task = id ? allTasks.find(t => t.id === id) : null;
  const projectOptions = allProjects.map(p =>
    `<option value="${p.id}" ${task?.project_id === p.id ? 'selected' : ''}>${esc(p.name)}</option>`
  ).join('');

  document.getElementById('modal-title').textContent = task ? 'Edit Task' : 'New Task';
  document.getElementById('modal-body').innerHTML = `
    <div class="form-group">
      <label>Title *</label>
      <input id="t-title" value="${esc(task?.title || '')}" placeholder="Task title" />
    </div>
    <div class="form-group">
      <label>Project *</label>
      <select id="t-project">
        <option value="">Select project</option>
        ${projectOptions}
      </select>
    </div>
    <div class="form-group">
      <label>Description</label>
      <textarea id="t-desc">${esc(task?.description || '')}</textarea>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label>Status</label>
        <select id="t-status">
          ${['todo', 'in_progress', 'done'].map(s =>
            `<option value="${s}" ${task?.status === s ? 'selected' : ''}>${s.replace('_', ' ')}</option>`
          ).join('')}
        </select>
      </div>
      <div class="form-group">
        <label>Priority</label>
        <select id="t-priority">
          ${['low', 'medium', 'high'].map(p =>
            `<option value="${p}" ${task?.priority === p ? 'selected' : ''}>${p}</option>`
          ).join('')}
        </select>
      </div>
    </div>
    <div class="form-group">
      <label>Due Date</label>
      <input id="t-due" type="date" value="${task?.due_date ? task.due_date.slice(0,10) : ''}" />
    </div>
    <div class="modal-footer">
      ${task ? `<button class="btn btn-danger" onclick="deleteTask(${task.id})">Delete</button>` : ''}
      <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
      <button class="btn btn-primary" onclick="saveTask(${id || 'null'})">
        ${task ? 'Save Changes' : 'Create Task'}
      </button>
    </div>`;
  openModal();
}

async function saveTask(id) {
  const title = document.getElementById('t-title').value.trim();
  const project_id = document.getElementById('t-project').value;

  if (!title) { showToast('Title is required', 'error'); return; }
  if (!project_id) { showToast('Project is required', 'error'); return; }

  const data = {
    title,
    project_id: parseInt(project_id),
    description: document.getElementById('t-desc').value.trim() || null,
    status: document.getElementById('t-status').value,
    priority: document.getElementById('t-priority').value,
    due_date: document.getElementById('t-due').value
      ? document.getElementById('t-due').value + 'T00:00:00' : null,
  };

  try {
    if (id) {
      await api.updateTask(id, data);
      showToast('Task updated');
    } else {
      await api.createTask(data);
      showToast('Task created');
    }
    closeModal();
    loadTasks();
  } catch (err) {
    showToast(err.detail || 'Failed to save task', 'error');
  }
}

async function deleteTask(id) {
  if (!confirm('Delete this task?')) return;
  try {
    await api.deleteTask(id);
    showToast('Task deleted');
    closeModal();
    loadTasks();
  } catch (err) {
    showToast(err.detail || 'Failed to delete task', 'error');
  }
}