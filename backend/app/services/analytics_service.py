from decimal import Decimal
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func, case, extract
from app.models.invoice import Invoice, InvoiceItem, Payment, InvoiceStatus
from app.models.project import Project
from app.models.time_log import TimeLog
from app.models.client import Client


MONTH_NAMES = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}


def _invoice_total_subquery(db: Session):
    """Subquery: invoice_id → subtotal from items."""
    return (
        db.query(
            InvoiceItem.invoice_id,
            func.sum(InvoiceItem.subtotal).label("items_subtotal")
        )
        .group_by(InvoiceItem.invoice_id)
        .subquery()
    )


def get_revenue_summary(db: Session, user_id: int) -> dict:
    item_totals = _invoice_total_subquery(db)

    # Total invoiced (non-cancelled invoices only)
    invoiced_row = (
        db.query(
            func.coalesce(
                func.sum(
                    item_totals.c.items_subtotal *
                    (1 + Invoice.tax_rate / 100)
                ), 0
            ).label("total_invoiced")
        )
        .join(item_totals, Invoice.id == item_totals.c.invoice_id)
        .filter(
            Invoice.user_id == user_id,
            Invoice.status != InvoiceStatus.cancelled
        )
        .first()
    )

    # Total collected (sum of all payments)
    collected_row = (
        db.query(
            func.coalesce(func.sum(Payment.amount), 0).label("total_collected")
        )
        .join(Invoice, Payment.invoice_id == Invoice.id)
        .filter(Invoice.user_id == user_id)
        .first()
    )

    # Total overdue
    overdue_row = (
        db.query(
            func.coalesce(
                func.sum(
                    item_totals.c.items_subtotal *
                    (1 + Invoice.tax_rate / 100)
                ), 0
            ).label("total_overdue")
        )
        .join(item_totals, Invoice.id == item_totals.c.invoice_id)
        .filter(
            Invoice.user_id == user_id,
            Invoice.status == InvoiceStatus.overdue
        )
        .first()
    )

    total_invoiced = Decimal(str(invoiced_row.total_invoiced)).quantize(Decimal("0.01"))
    total_collected = Decimal(str(collected_row.total_collected)).quantize(Decimal("0.01"))
    total_overdue = Decimal(str(overdue_row.total_overdue)).quantize(Decimal("0.01"))
    total_outstanding = (total_invoiced - total_collected).quantize(Decimal("0.01"))

    return {
        "total_invoiced": total_invoiced,
        "total_collected": total_collected,
        "total_outstanding": total_outstanding,
        "total_overdue": total_overdue
    }


def get_monthly_revenue(db: Session, user_id: int, months: int = 12) -> list[dict]:
    item_totals = _invoice_total_subquery(db)

    rows = (
        db.query(
            extract("year", Invoice.issue_date).label("year"),
            extract("month", Invoice.issue_date).label("month"),
            func.coalesce(
                func.sum(
                    item_totals.c.items_subtotal *
                    (1 + Invoice.tax_rate / 100)
                ), 0
            ).label("total_invoiced")
        )
        .join(item_totals, Invoice.id == item_totals.c.invoice_id)
        .filter(
            Invoice.user_id == user_id,
            Invoice.status != InvoiceStatus.cancelled
        )
        .group_by(
            extract("year", Invoice.issue_date),
            extract("month", Invoice.issue_date)
        )
        .order_by(
            extract("year", Invoice.issue_date).desc(),
            extract("month", Invoice.issue_date).desc()
        )
        .limit(months)
        .all()
    )

    # Get collected per month
    collected_rows = (
        db.query(
            extract("year", Invoice.issue_date).label("year"),
            extract("month", Invoice.issue_date).label("month"),
            func.coalesce(func.sum(Payment.amount), 0).label("total_collected")
        )
        .join(Payment, Invoice.id == Payment.invoice_id)
        .filter(Invoice.user_id == user_id)
        .group_by(
            extract("year", Invoice.issue_date),
            extract("month", Invoice.issue_date)
        )
        .all()
    )

    collected_map = {
        (int(r.year), int(r.month)): Decimal(str(r.total_collected))
        for r in collected_rows
    }

    result = []
    for row in rows:
        year = int(row.year)
        month = int(row.month)
        result.append({
            "year": year,
            "month": month,
            "month_name": MONTH_NAMES[month],
            "total_invoiced": Decimal(str(row.total_invoiced)).quantize(Decimal("0.01")),
            "total_collected": collected_map.get((year, month), Decimal("0")).quantize(Decimal("0.01"))
        })

    return result


def get_top_clients(db: Session, user_id: int, limit: int = 5) -> list[dict]:
    item_totals = _invoice_total_subquery(db)

    rows = (
        db.query(
            Client.id.label("client_id"),
            Client.name.label("client_name"),
            func.coalesce(
                func.sum(
                    item_totals.c.items_subtotal *
                    (1 + Invoice.tax_rate / 100)
                ), 0
            ).label("total_invoiced"),
            func.count(Invoice.id).label("invoice_count")
        )
        .join(Invoice, Invoice.client_id == Client.id)
        .join(item_totals, Invoice.id == item_totals.c.invoice_id)
        .filter(
            Invoice.user_id == user_id,
            Invoice.status != InvoiceStatus.cancelled
        )
        .group_by(Client.id, Client.name)
        .order_by(func.sum(item_totals.c.items_subtotal).desc())
        .limit(limit)
        .all()
    )

    # Get collected per client
    collected_rows = (
        db.query(
            Invoice.client_id,
            func.coalesce(func.sum(Payment.amount), 0).label("total_collected")
        )
        .join(Payment, Invoice.id == Payment.invoice_id)
        .filter(Invoice.user_id == user_id)
        .group_by(Invoice.client_id)
        .all()
    )

    collected_map = {
        r.client_id: Decimal(str(r.total_collected))
        for r in collected_rows
    }

    return [
        {
            "client_id": row.client_id,
            "client_name": row.client_name,
            "total_invoiced": Decimal(str(row.total_invoiced)).quantize(Decimal("0.01")),
            "total_collected": collected_map.get(row.client_id, Decimal("0")).quantize(Decimal("0.01")),
            "invoice_count": row.invoice_count
        }
        for row in rows
    ]


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
            func.coalesce(
                func.sum(TimeLog.hours * TimeLog.hourly_rate), 0
            ).label("value")
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
    item_totals = _invoice_total_subquery(db)

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
        subtotal = sum(Decimal(str(item.subtotal)) for item in inv.items)
        tax = (subtotal * Decimal(str(inv.tax_rate)) / 100).quantize(Decimal("0.01"))
        total = subtotal + tax
        paid = sum(Decimal(str(p.amount)) for p in inv.payments)
        balance_due = total - paid

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