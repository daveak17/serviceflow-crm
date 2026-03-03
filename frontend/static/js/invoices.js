let allInvoices = [];
let invoiceItems = [];

async function loadInvoices() {
  try {
    allInvoices = await api.getInvoices() || [];
    renderInvoices();
  } catch (err) {
    showToast('Failed to load invoices', 'error');
  }
}

function renderInvoices() {
  const tbody = document.getElementById('invoices-tbody');
  if (allInvoices.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6"><div class="empty-state">
      <div class="empty-state-icon">◻</div>
      <div class="empty-state-text">No invoices yet.</div>
    </div></td></tr>`;
    return;
  }

  tbody.innerHTML = allInvoices.map(inv => {
    const subtotal = inv.items.reduce((s, i) => s + parseFloat(i.subtotal), 0);
    const tax = subtotal * parseFloat(inv.tax_rate) / 100;
    const total = subtotal + tax;
    const client = allClients.find(c => c.id === inv.client_id);

    return `<tr>
      <td><strong>${esc(inv.invoice_number)}</strong></td>
      <td>${client ? esc(client.name) : '—'}</td>
      <td>${fmt(total)}</td>
      <td>${badge(inv.status)}</td>
      <td>${inv.due_date}</td>
      <td>
        <div class="action-btns">
          ${inv.status === 'sent' || inv.status === 'overdue'
            ? `<button class="btn btn-primary btn-sm" onclick="openPaymentModal(${inv.id}, ${total})">Pay</button>` : ''}
          ${inv.status === 'draft'
            ? `<button class="btn btn-secondary btn-sm" onclick="markSent(${inv.id})">Send</button>` : ''}
          ${inv.status === 'draft' || inv.status === 'cancelled'
            ? `<button class="btn btn-danger btn-sm" onclick="deleteInvoice(${inv.id})">Delete</button>` : ''}
        </div>
      </td>
    </tr>`;
  }).join('');
}

function openInvoiceModal() {
  invoiceItems = [{ description: '', quantity: 1, unit_price: '' }];
  const clientOptions = allClients.map(c =>
    `<option value="${c.id}">${esc(c.name)}</option>`).join('');
  const today = new Date().toISOString().slice(0, 10);
  const due = new Date(Date.now() + 30 * 86400000).toISOString().slice(0, 10);

  document.getElementById('modal-title').textContent = 'New Invoice';
  document.getElementById('modal-body').innerHTML = `
    <div class="form-row">
      <div class="form-group">
        <label>Invoice Number *</label>
        <input id="inv-number" placeholder="INV-001" />
      </div>
      <div class="form-group">
        <label>Client</label>
        <select id="inv-client">
          <option value="">No client</option>
          ${clientOptions}
        </select>
      </div>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label>Issue Date *</label>
        <input id="inv-issue" type="date" value="${today}" />
      </div>
      <div class="form-group">
        <label>Due Date *</label>
        <input id="inv-due" type="date" value="${due}" />
      </div>
    </div>
    <div class="form-group">
      <label>Tax Rate (%)</label>
      <input id="inv-tax" type="number" value="0" min="0" max="100" />
    </div>
    <div class="form-group">
      <label>Line Items</label>
      <div class="invoice-items">
        <div class="invoice-items-header">
          <span>Description</span><span>Qty</span><span>Unit Price</span><span></span>
        </div>
        <div id="items-container"></div>
      </div>
      <button class="btn btn-secondary btn-sm" onclick="addInvoiceItem()" style="margin-top:8px">+ Add Item</button>
    </div>
    <div class="form-group">
      <label>Notes</label>
      <textarea id="inv-notes" placeholder="Payment terms, notes..."></textarea>
    </div>
    <div class="modal-footer">
      <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
      <button class="btn btn-primary" onclick="saveInvoice()">Create Invoice</button>
    </div>`;
  renderInvoiceItems();
  openModal();
}

function renderInvoiceItems() {
  document.getElementById('items-container').innerHTML = invoiceItems.map((item, i) => `
    <div class="invoice-item-row">
      <input placeholder="Description" value="${esc(item.description)}"
        oninput="invoiceItems[${i}].description=this.value" />
      <input type="number" placeholder="1" value="${item.quantity}" min="0.01" step="0.01"
        oninput="invoiceItems[${i}].quantity=this.value" />
      <input type="number" placeholder="0.00" value="${item.unit_price}" min="0.01" step="0.01"
        oninput="invoiceItems[${i}].unit_price=this.value" />
      <button class="item-remove" onclick="removeInvoiceItem(${i})">✕</button>
    </div>`).join('');
}

function addInvoiceItem() {
  invoiceItems.push({ description: '', quantity: 1, unit_price: '' });
  renderInvoiceItems();
}

function removeInvoiceItem(i) {
  if (invoiceItems.length === 1) { showToast('At least one item required', 'error'); return; }
  invoiceItems.splice(i, 1);
  renderInvoiceItems();
}

async function saveInvoice() {
  const number = document.getElementById('inv-number').value.trim();
  if (!number) { showToast('Invoice number required', 'error'); return; }

  const items = invoiceItems.map(item => ({
    description: item.description,
    quantity: parseFloat(item.quantity),
    unit_price: parseFloat(item.unit_price),
  }));

  if (items.some(i => !i.description || isNaN(i.quantity) || isNaN(i.unit_price))) {
    showToast('All line items must be complete', 'error'); return;
  }

  const data = {
    invoice_number: number,
    client_id: document.getElementById('inv-client').value || null,
    issue_date: document.getElementById('inv-issue').value,
    due_date: document.getElementById('inv-due').value,
    tax_rate: parseFloat(document.getElementById('inv-tax').value) || 0,
    notes: document.getElementById('inv-notes').value.trim() || null,
    items,
  };

  try {
    await api.createInvoice(data);
    showToast('Invoice created');
    closeModal();
    loadInvoices();
  } catch (err) {
    showToast(err.detail || 'Failed to create invoice', 'error');
  }
}

async function markSent(id) {
  try {
    await api.updateInvoice(id, { status: 'sent' });
    showToast('Invoice marked as sent');
    loadInvoices();
  } catch (err) {
    showToast(err.detail || 'Failed to update invoice', 'error');
  }
}

function openPaymentModal(invoiceId, total) {
  const today = new Date().toISOString().slice(0, 10);
  document.getElementById('modal-title').textContent = 'Record Payment';
  document.getElementById('modal-body').innerHTML = `
    <div class="form-group">
      <label>Amount</label>
      <input id="pay-amount" type="number" value="${total}" min="0.01" step="0.01" />
    </div>
    <div class="form-group">
      <label>Payment Date</label>
      <input id="pay-date" type="date" value="${today}" />
    </div>
    <div class="form-group">
      <label>Notes</label>
      <input id="pay-notes" placeholder="Payment reference, method..." />
    </div>
    <div class="modal-footer">
      <button class="btn btn-secondary" onclick="closeModal()">Cancel</button>
      <button class="btn btn-primary" onclick="savePayment(${invoiceId})">Record Payment</button>
    </div>`;
  openModal();
}

async function savePayment(invoiceId) {
  const data = {
    amount: parseFloat(document.getElementById('pay-amount').value),
    payment_date: document.getElementById('pay-date').value,
    notes: document.getElementById('pay-notes').value.trim() || null,
  };

  try {
    await api.addPayment(invoiceId, data);
    showToast('Payment recorded');
    closeModal();
    loadInvoices();
  } catch (err) {
    showToast(err.detail || 'Failed to record payment', 'error');
  }
}

async function deleteInvoice(id) {
  if (!confirm('Delete this invoice?')) return;
  try {
    await api.deleteInvoice(id);
    showToast('Invoice deleted');
    loadInvoices();
  } catch (err) {
    showToast(err.detail || 'Failed to delete invoice', 'error');
  }
}