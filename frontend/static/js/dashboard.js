let revenueChart = null;
let projectChart = null;

async function loadDashboard() {
  try {
    const data = await api.getDashboard();
    if (!data) return;

    // Stats
    document.getElementById('stat-invoiced').textContent = fmt(data.revenue.total_invoiced);
    document.getElementById('stat-collected').textContent = fmt(data.revenue.total_collected);
    document.getElementById('stat-outstanding').textContent = fmt(data.revenue.total_outstanding);
    document.getElementById('stat-net-income').textContent = fmt(data.revenue.net_income);
    

    // Monthly revenue chart
    const monthly = await api.getMonthlyRevenue();
    if (monthly) renderRevenueChart(monthly.reverse());

    // Project status chart
    renderProjectChart(data.project_statuses);

    // Top clients
    const clientsEl = document.getElementById('top-clients-list');
    if (data.top_clients.length === 0) {
      clientsEl.innerHTML = '<div class="empty-state"><div class="empty-state-text">No client data yet</div></div>';
    } else {
      clientsEl.innerHTML = data.top_clients.map(c => `
        <div class="client-row">
          <div>
            <div class="client-row-name">${esc(c.client_name)}</div>
            <div class="client-row-sub">${c.invoice_count} invoice${c.invoice_count !== 1 ? 's' : ''}</div>
          </div>
          <div style="text-align:right">
            <div class="client-row-amount">${fmt(c.total_invoiced)}</div>
            <div class="client-row-sub" style="color:var(--green)">${fmt(c.total_collected)} collected</div>
          </div>
        </div>`).join('');
    }

    // Outstanding invoices
    const outEl = document.getElementById('outstanding-list');
    if (data.outstanding_invoices.length === 0) {
      outEl.innerHTML = '<div class="empty-state"><div class="empty-state-text">No outstanding invoices</div></div>';
    } else {
      outEl.innerHTML = data.outstanding_invoices.map(inv => `
        <div class="outstanding-row">
          <div>
            <div style="font-weight:500">${esc(inv.invoice_number)}</div>
            <div style="font-size:12px;color:var(--text-secondary)">${inv.client_name || '—'} · Due ${inv.due_date}</div>
          </div>
          <div>
            <div style="font-weight:600">${fmt(inv.balance_due)}</div>
            <div style="text-align:right">${badge(inv.status)}</div>
          </div>
        </div>`).join('');
    }
  } catch (err) {
    console.error('Dashboard error:', err);
  }
}

function renderRevenueChart(monthly) {
  const ctx = document.getElementById('chart-revenue').getContext('2d');
  if (revenueChart) revenueChart.destroy();
  revenueChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: monthly.map(m => m.month_name.slice(0, 3) + ' ' + m.year),
      datasets: [
        {
          label: 'Invoiced',
          data: monthly.map(m => parseFloat(m.total_invoiced)),
          backgroundColor: '#6e56cf22',
          borderColor: '#6e56cf',
          borderWidth: 2,
          borderRadius: 4,
        },
        {
          label: 'Collected',
          data: monthly.map(m => parseFloat(m.total_collected)),
          backgroundColor: '#16a34a22',
          borderColor: '#16a34a',
          borderWidth: 2,
          borderRadius: 4,
        }
      ]
    },
    options: {
      responsive: true,
      plugins: { legend: { position: 'bottom' } },
      scales: { y: { beginAtZero: true, grid: { color: '#f3f4f6' } }, x: { grid: { display: false } } }
    }
  });
}

function renderProjectChart(statuses) {
  const ctx = document.getElementById('chart-projects').getContext('2d');
  if (projectChart) projectChart.destroy();

  const colorMap = {
    active: '#16a34a',
    on_hold: '#d97706',
    completed: '#2563eb',
    cancelled: '#9ca3af'
  };

  const sorted = [...statuses].sort((a, b) => {
    const order = { active: 0, on_hold: 1, completed: 2, cancelled: 3 };
    return (order[a.status] ?? 9) - (order[b.status] ?? 9);
  });

  projectChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: sorted.map(s => s.status.replace('_', ' ')),
      datasets: [{
        data: sorted.map(s => s.count),
        backgroundColor: sorted.map(s => colorMap[s.status] || '#6e56cf'),
        borderWidth: 0,
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { position: 'bottom' } },
      cutout: '65%'
    }
  });
}