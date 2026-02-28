from sqlalchemy.orm import Session
from app.models.project import Project
from app.models.client import Client
from app.schemas.project import ProjectCreate, ProjectUpdate


def verify_client_ownership(db: Session, client_id: int, user_id: int) -> bool:
    client = (
        db.query(Client)
        .filter(Client.id == client_id, Client.user_id == user_id)
        .first()
    )
    return client is not None


def get_projects(db: Session, user_id: int) -> list[Project]:
    return (
        db.query(Project)
        .filter(Project.user_id == user_id)
        .order_by(Project.created_at.desc())
        .all()
    )


def get_project(db: Session, project_id: int, user_id: int) -> Project | None:
    return (
        db.query(Project)
        .filter(Project.id == project_id, Project.user_id == user_id)
        .first()
    )


def create_project(db: Session, data: ProjectCreate, user_id: int) -> Project | None:
    payload = data.model_dump()

    # If client_id is provided, ensure it belongs to the same user
    if payload.get("client_id") is not None:
        if not verify_client_ownership(db, payload["client_id"], user_id):
            return None

    project = Project(**payload, user_id=user_id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def update_project(db: Session, project_id: int, data: ProjectUpdate, user_id: int) -> Project | None:
    project = get_project(db, project_id, user_id)
    if not project:
        return None

    update_data = data.model_dump(exclude_unset=True)

    # If client_id is being changed, validate ownership (allow null to unlink)
    if "client_id" in update_data and update_data["client_id"] is not None:
        if not verify_client_ownership(db, update_data["client_id"], user_id):
            return None

    for field, value in update_data.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project_id: int, user_id: int) -> bool:
    project = get_project(db, project_id, user_id)
    if not project:
        return False
    db.delete(project)
    db.commit()
    return True