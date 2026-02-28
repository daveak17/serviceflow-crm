from pydantic import BaseModel
from decimal import Decimal
from typing import Optional


class RevenueSummary(BaseModel):
    total_invoiced: Decimal
    total_collected: Decimal
    total_outstanding: Decimal
    total_overdue: Decimal


class MonthlyRevenue(BaseModel):
    year: int
    month: int
    month_name: str
    total_invoiced: Decimal
    total_collected: Decimal


class TopClient(BaseModel):
    client_id: int
    client_name: str
    total_invoiced: Decimal
    total_collected: Decimal
    invoice_count: int


class ProjectStatusCount(BaseModel):
    status: str
    count: int


class HoursSummary(BaseModel):
    total_hours: Decimal
    billable_hours: Decimal
    non_billable_hours: Decimal
    estimated_value: Decimal


class OutstandingInvoice(BaseModel):
    invoice_id: int
    invoice_number: str
    client_name: Optional[str]
    total: Decimal
    balance_due: Decimal
    due_date: str
    status: str


class DashboardSummary(BaseModel):
    revenue: RevenueSummary
    hours: HoursSummary
    project_statuses: list[ProjectStatusCount]
    top_clients: list[TopClient]
    outstanding_invoices: list[OutstandingInvoice]