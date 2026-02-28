from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api.deps import get_current_user
from app.schemas.client import ClientCreate, ClientUpdate, ClientResponse
from app.services.client_service import (
    get_clients, get_client, create_client, update_client, delete_client
)

router = APIRouter(prefix="/api/clients", tags=["Clients"])


@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
def create(
    data: ClientCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return create_client(db, data, current_user.id)


@router.get("", response_model=list[ClientResponse])
def list_clients(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_clients(db, current_user.id)


@router.get("/{client_id}", response_model=ClientResponse)
def get_one(
    client_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    client = get_client(db, client_id, current_user.id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    return client


@router.put("/{client_id}", response_model=ClientResponse)
def update(
    client_id: int,
    data: ClientUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    client = update_client(db, client_id, data, current_user.id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    return client


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    client_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    deleted = delete_client(db, client_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )