from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api.deps import get_current_user
from app.schemas.invoice import (
    InvoiceCreate, InvoiceUpdate, InvoiceResponse,
    PaymentCreate, PaymentResponse, InvoiceSummary
)
from app.services.invoice_service import (
    get_invoices, get_invoice, create_invoice,
    update_invoice, delete_invoice, add_payment, calculate_totals
)

router = APIRouter(prefix="/api/invoices", tags=["Invoices"])


@router.post("", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def create(
    data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    invoice, error = create_invoice(db, data, current_user.id)
    if error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error
        )
    return invoice


@router.get("", response_model=list[InvoiceResponse])
def list_invoices(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_invoices(db, current_user.id)


@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_one(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    invoice = get_invoice(db, invoice_id, current_user.id)
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    return invoice


@router.get("/{invoice_id}/summary", response_model=InvoiceSummary)
def invoice_summary(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    invoice = get_invoice(db, invoice_id, current_user.id)
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    return calculate_totals(invoice)


@router.put("/{invoice_id}", response_model=InvoiceResponse)
def update(
    invoice_id: int,
    data: InvoiceUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    invoice, error = update_invoice(db, invoice_id, data, current_user.id)
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return invoice


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    deleted = delete_invoice(db, invoice_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoice not found or cannot be deleted in its current status"
        )


@router.post("/{invoice_id}/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(
    invoice_id: int,
    data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    payment, error = add_payment(db, invoice_id, data, current_user.id)
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return payment


@router.get("/{invoice_id}/payments", response_model=list[PaymentResponse])
def list_payments(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    invoice = get_invoice(db, invoice_id, current_user.id)
    if not invoice:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    return invoice.payments