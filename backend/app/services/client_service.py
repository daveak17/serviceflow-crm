from sqlalchemy.orm import Session
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate


def get_clients(db: Session, user_id: int) -> list[Client]:
    return (
        db.query(Client)
        .filter(Client.user_id == user_id)
        .order_by(Client.created_at.desc())
        .all()
    )


def get_client(db: Session, client_id: int, user_id: int) -> Client | None:
    return (
        db.query(Client)
        .filter(Client.id == client_id, Client.user_id == user_id)
        .first()
    )


def create_client(db: Session, data: ClientCreate, user_id: int) -> Client:
    client = Client(**data.model_dump(), user_id=user_id)
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def update_client(db: Session, client_id: int, data: ClientUpdate, user_id: int) -> Client | None:
    client = get_client(db, client_id, user_id)
    if not client:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)
    db.commit()
    db.refresh(client)
    return client


def delete_client(db: Session, client_id: int, user_id: int) -> bool:
    client = get_client(db, client_id, user_id)
    if not client:
        return False
    db.delete(client)
    db.commit()
    return True