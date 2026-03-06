from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.models.invoice import Invoice, InvoiceItem, Payment, InvoiceStatus
from app.models.project import Project
from app.models.time_log import TimeLog
from app.models.client import Client


MONTH_NAMES = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}


def _compute_invoice_total(invoice: Invoice) -> Decimal:
    subtotal = sum(Decimal(str(item.subtotal)) for item in invoice.items)
    tax = (subtotal * Decimal(str(invoice.tax_rate)) / 100).quantize(Decimal("0.01"))
    return subtotal + tax


def _compute_invoice_paid(invoice: Invoice) -> Decimal:
    return sum(Decimal(str(p.amount)) for p in invoice.payments)

def _compute_invoice_subtotal(invoice: Invoice) -> Decimal:
    return sum(Decimal(str(item.subtotal)) for item in invoice.items)

def get_revenue_summary(db: Session, user_id: int) -> dict:
    # Total invoiced — sum of all non-cancelled invoice totals
    active_invoices = (
        db.query(Invoice)
        .filter(
            Invoice.user_id == user_id,
            Invoice.status != InvoiceStatus.cancelled
        )
        .all()
    )

    total_invoiced = Decimal("0")
    for inv in active_invoices:
        total_invoiced += _compute_invoice_total(inv)

    # Total collected — sum of payments on non-cancelled invoices only
    total_collected = Decimal("0")
    for inv in active_invoices:
        total_collected += _compute_invoice_paid(inv)

    # Outstanding — sum of per-invoice balance due for sent/overdue invoices
    # This is correct: max(total - paid, 0) per invoice
    outstanding_invoices = (
        db.query(Invoice)
        .filter(
            Invoice.user_id == user_id,
            Invoice.status.in_([InvoiceStatus.sent, InvoiceStatus.overdue])
        )
        .all()
    )

    total_outstanding = Decimal("0")
    total_overdue = Decimal("0")
    for inv in outstanding_invoices:
        total = _compute_invoice_total(inv)
        paid = _compute_invoice_paid(inv)
        balance = max(total - paid, Decimal("0"))
        total_outstanding += balance
        if inv.status == InvoiceStatus.overdue:
            total_overdue += balance

    
    net_income = Decimal("0")
    for inv in active_invoices:
        paid = _compute_invoice_paid(inv)
        if paid <= Decimal("0"):
            continue
        subtotal = _compute_invoice_subtotal(inv)
        total = _compute_invoice_total(inv)
        if total > Decimal("0"):
            tax_ratio = (total - subtotal) / total
            net_income += paid * (1 - tax_ratio)

    return {
        "total_invoiced": total_invoiced.quantize(Decimal("0.01")),
        "total_collected": total_collected.quantize(Decimal("0.01")),
        "total_outstanding": total_outstanding.quantize(Decimal("0.01")),
        "total_overdue": total_overdue.quantize(Decimal("0.01")),
        "net_income": net_income.quantize(Decimal("0.01"))
    }


def get_monthly_revenue(db: Session, user_id: int, months: int = 12) -> list[dict]:
    # Subquery: invoice_id -> subtotal from invoice_items
    item_totals = (
        db.query(
            InvoiceItem.invoice_id.label("invoice_id"),
            func.coalesce(func.sum(InvoiceItem.subtotal), 0).label("subtotal_sum"),
        )
        .group_by(InvoiceItem.invoice_id)
        .subquery()
    )

    # Total invoiced (WITH tax) grouped by invoice.issue_date month
    invoiced_rows = (
        db.query(
            extract("year", Invoice.issue_date).label("year"),
            extract("month", Invoice.issue_date).label("month"),
            func.coalesce(
                func.sum(
                    item_totals.c.subtotal_sum * (1 + (Invoice.tax_rate / 100))
                ),
                0
            ).label("total_invoiced"),
        )
        .join(item_totals, Invoice.id == item_totals.c.invoice_id)
        .filter(
            Invoice.user_id == user_id,
            Invoice.status != InvoiceStatus.cancelled,
        )
        .group_by(
            extract("year", Invoice.issue_date),
            extract("month", Invoice.issue_date),
        )
        .order_by(
            extract("year", Invoice.issue_date).desc(),
            extract("month", Invoice.issue_date).desc(),
        )
        .limit(months)
        .all()
    )

    # Total collected grouped by Payment.payment_date month (exclude cancelled invoices)
    collected_rows = (
        db.query(
            extract("year", Payment.payment_date).label("year"),
            extract("month", Payment.payment_date).label("month"),
            func.coalesce(func.sum(Payment.amount), 0).label("total_collected"),
        )
        .join(Invoice, Payment.invoice_id == Invoice.id)
        .filter(
            Invoice.user_id == user_id,
            Invoice.status != InvoiceStatus.cancelled,
        )
        .group_by(
            extract("year", Payment.payment_date),
            extract("month", Payment.payment_date),
        )
        .all()
    )

    collected_map = {
        (int(r.year), int(r.month)): Decimal(str(r.total_collected))
        for r in collected_rows
    }

    result: list[dict] = []
    for row in invoiced_rows:
        year = int(row.year)
        month = int(row.month)

        result.append({
            "year": year,
            "month": month,
            "month_name": MONTH_NAMES.get(month, str(month)),
            "total_invoiced": Decimal(str(row.total_invoiced)).quantize(Decimal("0.01")),
            "total_collected": collected_map.get((year, month), Decimal("0")).quantize(Decimal("0.01")),
        })

    return result


def get_top_clients(db: Session, user_id: int, limit: int = 5) -> list[dict]:
    invoices = (
        db.query(Invoice)
        .filter(
            Invoice.user_id == user_id,
            Invoice.status != InvoiceStatus.cancelled,
            Invoice.client_id.isnot(None)
        )
        .all()
    )

    client_totals: dict[int, dict] = {}
    for inv in invoices:
        cid = inv.client_id
        if cid not in client_totals:
            client_totals[cid] = {
                "total_invoiced": Decimal("0"),
                "total_collected": Decimal("0"),
                "invoice_count": 0
            }
        client_totals[cid]["total_invoiced"] += _compute_invoice_total(inv)
        client_totals[cid]["total_collected"] += _compute_invoice_paid(inv)
        client_totals[cid]["invoice_count"] += 1

    # Sort by total invoiced descending, take top N
    sorted_clients = sorted(
        client_totals.items(),
        key=lambda x: x[1]["total_invoiced"],
        reverse=True
    )[:limit]

    result = []
    for client_id, totals in sorted_clients:
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            continue
        result.append({
            "client_id": client_id,
            "client_name": client.name,
            "total_invoiced": totals["total_invoiced"].quantize(Decimal("0.01")),
            "total_collected": totals["total_collected"].quantize(Decimal("0.01")),
            "invoice_count": totals["invoice_count"]
        })

    return result


def get_project_status_counts(db: Session, user_id: int) -> list[dict]:
    rows = (
        db.query(
            Project.status.label("status"),
            func.count(Project.id).label("count")
        )
        .filter(Project.user_id == user_id)
        .group_by(Project.status)
        .all()
    )
    return [{"status": row.status, "count": row.count} for row in rows]


def get_hours_summary(db: Session, user_id: int) -> dict:
    rows = (
        db.query(
            TimeLog.is_billable,
            func.coalesce(func.sum(TimeLog.hours), 0).label("total"),
            func.coalesce(func.sum(TimeLog.hours * TimeLog.hourly_rate), 0).label("value")
        )
        .filter(TimeLog.user_id == user_id)
        .group_by(TimeLog.is_billable)
        .all()
    )

    billable_hours = Decimal("0")
    non_billable_hours = Decimal("0")
    estimated_value = Decimal("0")

    for row in rows:
        if row.is_billable:
            billable_hours = Decimal(str(row.total)).quantize(Decimal("0.01"))
            estimated_value = Decimal(str(row.value)).quantize(Decimal("0.01"))
        else:
            non_billable_hours = Decimal(str(row.total)).quantize(Decimal("0.01"))

    return {
        "total_hours": (billable_hours + non_billable_hours).quantize(Decimal("0.01")),
        "billable_hours": billable_hours,
        "non_billable_hours": non_billable_hours,
        "estimated_value": estimated_value
    }


def get_outstanding_invoices(db: Session, user_id: int) -> list[dict]:
    invoices = (
        db.query(Invoice)
        .filter(
            Invoice.user_id == user_id,
            Invoice.status.in_([InvoiceStatus.sent, InvoiceStatus.overdue])
        )
        .order_by(Invoice.due_date.asc())
        .all()
    )

    result = []
    for inv in invoices:
        total = _compute_invoice_total(inv)
        paid = _compute_invoice_paid(inv)
        balance_due = total - paid

        # Fix Issue 3: skip fully paid invoices even if status not updated yet
        if balance_due <= Decimal("0"):
            continue

        client_name = None
        if inv.client_id:
            client = db.query(Client).filter(Client.id == inv.client_id).first()
            client_name = client.name if client else None

        result.append({
            "invoice_id": inv.id,
            "invoice_number": inv.invoice_number,
            "client_name": client_name,
            "total": total.quantize(Decimal("0.01")),
            "balance_due": balance_due.quantize(Decimal("0.01")),
            "due_date": str(inv.due_date),
            "status": inv.status.value
        })

    return result


def get_dashboard_summary(db: Session, user_id: int) -> dict:
    return {
        "revenue": get_revenue_summary(db, user_id),
        "hours": get_hours_summary(db, user_id),
        "project_statuses": get_project_status_counts(db, user_id),
        "top_clients": get_top_clients(db, user_id),
        "outstanding_invoices": get_outstanding_invoices(db, user_id)
    }