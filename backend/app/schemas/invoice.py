from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal
from app.models.invoice import InvoiceStatus


class InvoiceItemCreate(BaseModel):
    description: str
    quantity: Decimal
    unit_price: Decimal

    @field_validator("quantity", "unit_price")
    @classmethod
    def must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Must be greater than 0")
        return v


class InvoiceItemResponse(BaseModel):
    id: int
    invoice_id: int
    description: str
    quantity: Decimal
    unit_price: Decimal
    subtotal: Decimal

    model_config = {"from_attributes": True}


class InvoiceCreate(BaseModel):
    client_id: Optional[int] = None
    invoice_number: str
    issue_date: date
    due_date: date
    notes: Optional[str] = None
    tax_rate: Decimal = Decimal("0")
    items: List[InvoiceItemCreate]

    @field_validator("items")
    @classmethod
    def must_have_items(cls, v):
        if len(v) == 0:
            raise ValueError("Invoice must have at least one item")
        return v

    @field_validator("tax_rate")
    @classmethod
    def tax_rate_valid(cls, v):
        if v < 0 or v > 100:
            raise ValueError("Tax rate must be between 0 and 100")
        return v


class InvoiceUpdate(BaseModel):
    client_id: Optional[int] = None
    invoice_number: Optional[str] = None
    status: Optional[InvoiceStatus] = None
    issue_date: Optional[date] = None
    due_date: Optional[date] = None
    notes: Optional[str] = None
    tax_rate: Optional[Decimal] = None


class PaymentCreate(BaseModel):
    amount: Decimal
    payment_date: date
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Payment amount must be greater than 0")
        return v


class PaymentResponse(BaseModel):
    id: int
    invoice_id: int
    user_id: int
    amount: Decimal
    payment_date: date
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class InvoiceSummary(BaseModel):
    invoice_id: int
    invoice_number: str
    status: InvoiceStatus
    subtotal: Decimal
    tax_amount: Decimal
    total: Decimal
    total_paid: Decimal
    balance_due: Decimal


class InvoiceResponse(BaseModel):
    id: int
    user_id: int
    client_id: Optional[int] = None
    invoice_number: str
    status: InvoiceStatus
    issue_date: date
    due_date: date
    notes: Optional[str] = None
    tax_rate: Decimal
    created_at: datetime
    updated_at: datetime
    items: List[InvoiceItemResponse] = []
    payments: List[PaymentResponse] = []

    model_config = {"from_attributes": True}