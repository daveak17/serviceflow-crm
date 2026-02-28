from sqlalchemy.exc import IntegrityError
from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.invoice import Invoice, InvoiceItem, Payment, InvoiceStatus
from app.models.client import Client
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate, PaymentCreate


ALLOWED_TRANSITIONS: dict[InvoiceStatus, list[InvoiceStatus]] = {
    InvoiceStatus.draft: [InvoiceStatus.sent, InvoiceStatus.cancelled],
    InvoiceStatus.sent: [InvoiceStatus.overdue, InvoiceStatus.cancelled],
    InvoiceStatus.overdue: [InvoiceStatus.cancelled],
    InvoiceStatus.paid: [],        
    InvoiceStatus.cancelled: [],   
}


def validate_status_transition(current: InvoiceStatus, next_status: InvoiceStatus) -> bool:
    """Returns True if the transition is allowed."""
    return next_status in ALLOWED_TRANSITIONS.get(current, [])


def auto_set_overdue(invoice: Invoice) -> None:
    """Mark sent invoices as overdue if past due date. Call before returning invoice data."""
    if invoice.status == InvoiceStatus.sent and invoice.due_date < date.today():
        invoice.status = InvoiceStatus.overdue


def verify_client_ownership(db: Session, client_id: int, user_id: int) -> bool:
    return db.query(Client).filter(
        Client.id == client_id,
        Client.user_id == user_id
    ).first() is not None


def calculate_subtotal(items) -> Decimal:
    return sum(Decimal(str(item.quantity)) * Decimal(str(item.unit_price)) for item in items)


def calculate_totals(invoice: Invoice) -> dict:
    subtotal = calculate_subtotal(invoice.items)
    tax_amount = (subtotal * Decimal(str(invoice.tax_rate)) / Decimal("100")).quantize(Decimal("0.01"))
    total = subtotal + tax_amount
    total_paid = sum(Decimal(str(p.amount)) for p in invoice.payments)
    balance_due = total - total_paid
    return {
        "invoice_id": invoice.id,
        "invoice_number": invoice.invoice_number,
        "status": invoice.status,
        "subtotal": subtotal,
        "tax_amount": tax_amount,
        "total": total,
        "total_paid": total_paid,
        "balance_due": balance_due
    }


def get_invoices(db: Session, user_id: int) -> list[Invoice]:
    invoices = (
        db.query(Invoice)
        .filter(Invoice.user_id == user_id)
        .order_by(Invoice.created_at.desc())
        .all()
    )
    for inv in invoices:
        auto_set_overdue(inv)
    db.commit()
    return invoices


def get_invoice(db: Session, invoice_id: int, user_id: int) -> Invoice | None:
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.user_id == user_id
    ).first()
    if invoice:
        auto_set_overdue(invoice)
        db.commit()
    return invoice


def create_invoice(db: Session, data: InvoiceCreate, user_id: int) -> tuple[Invoice | None, str | None]:
    if data.client_id is not None:
        if not verify_client_ownership(db, data.client_id, user_id):
            return None, "Client not found or does not belong to you"

    invoice_data = data.model_dump(exclude={"items"})
    invoice = Invoice(**invoice_data, user_id=user_id)
    db.add(invoice)

    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        return None, f"Invoice number '{data.invoice_number}' already exists"

    for item_data in data.items:
        subtotal = (item_data.quantity * item_data.unit_price).quantize(Decimal("0.01"))
        item = InvoiceItem(
            invoice_id=invoice.id,
            description=item_data.description,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            subtotal=subtotal
        )
        db.add(item)

    db.commit()
    db.refresh(invoice)
    return invoice, None


def update_invoice(
    db: Session,
    invoice_id: int,
    data: InvoiceUpdate,
    user_id: int
) -> tuple[Invoice | None, str | None]:
    """
    Returns (invoice, error_message).
    error_message is None on success.
    """
    invoice = db.query(Invoice).filter(
        Invoice.id == invoice_id,
        Invoice.user_id == user_id
    ).first()

    if not invoice:
        return None, "Invoice not found"

    auto_set_overdue(invoice)

    update_data = data.model_dump(exclude_unset=True)

    if "status" in update_data:
        new_status = update_data["status"]
        if not validate_status_transition(invoice.status, new_status):
            allowed = [s.value for s in ALLOWED_TRANSITIONS.get(invoice.status, [])]
            return None, f"Cannot transition from '{invoice.status.value}' to '{new_status.value}'. Allowed: {[s for s in allowed]}"

    if "client_id" in update_data and update_data["client_id"] is not None:
        if not verify_client_ownership(db, update_data["client_id"], user_id):
            return None, "Client not found or does not belong to you"

    for field, value in update_data.items():
        setattr(invoice, field, value)

    db.commit()
    db.refresh(invoice)
    return invoice, None


def delete_invoice(db: Session, invoice_id: int, user_id: int) -> bool:
    invoice = get_invoice(db, invoice_id, user_id)
    if not invoice:
        return False
    if invoice.status not in (InvoiceStatus.draft, InvoiceStatus.cancelled):
        return False
    db.delete(invoice)
    db.commit()
    return True


def add_payment(db: Session, invoice_id: int, data: PaymentCreate, user_id: int) -> tuple[Payment | None, str | None]:
    """
    Returns (payment, error_message).
    error_message is None on success.
    """
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()

    if not invoice:
        return None, "Invoice not found"

    if invoice.user_id != user_id:
        return None, "Invoice not found"  

    if invoice.status == InvoiceStatus.draft:
        return None, "Cannot add payment to a draft invoice"

    if invoice.status == InvoiceStatus.cancelled:
        return None, "Cannot add payment to a cancelled invoice"

    totals = calculate_totals(invoice)
    if Decimal(str(data.amount)) > totals["balance_due"]:
        return None, f"Payment of {data.amount} exceeds balance due of {totals['balance_due']}"

    payment = Payment(
        invoice_id=invoice_id,
        user_id=user_id,
        amount=data.amount,
        payment_date=data.payment_date,
        notes=data.notes
    )
    db.add(payment)

    new_total_paid = totals["total_paid"] + Decimal(str(data.amount))
    if new_total_paid >= totals["total"]:
        invoice.status = InvoiceStatus.paid

    db.commit()
    db.refresh(payment)
    return payment, None