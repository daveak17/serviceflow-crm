from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api.deps import get_current_user
from app.schemas.analytics import (
    RevenueSummary, MonthlyRevenue, TopClient,
    ProjectStatusCount, HoursSummary,
    OutstandingInvoice, DashboardSummary
)
from app.services.analytics_service import (
    get_revenue_summary, get_monthly_revenue, get_top_clients,
    get_project_status_counts, get_hours_summary,
    get_outstanding_invoices, get_dashboard_summary
)

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/dashboard", response_model=DashboardSummary)
def dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_dashboard_summary(db, current_user.id)


@router.get("/revenue", response_model=RevenueSummary)
def revenue_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_revenue_summary(db, current_user.id)


@router.get("/revenue/monthly", response_model=list[MonthlyRevenue])
def monthly_revenue(
    months: int = Query(default=12, ge=1, le=24, description="Number of months to return"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_monthly_revenue(db, current_user.id, months)


@router.get("/clients/top", response_model=list[TopClient])
def top_clients(
    limit: int = Query(default=5, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_top_clients(db, current_user.id, limit)


@router.get("/projects/status", response_model=list[ProjectStatusCount])
def project_statuses(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_project_status_counts(db, current_user.id)


@router.get("/hours", response_model=HoursSummary)
def hours_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_hours_summary(db, current_user.id)


@router.get("/invoices/outstanding", response_model=list[OutstandingInvoice])
def outstanding_invoices(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_outstanding_invoices(db, current_user.id)