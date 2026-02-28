from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.api.deps import get_current_user
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.services.project_service import (
    get_projects, get_project, create_project, update_project, delete_project
)

router = APIRouter(prefix="/api/projects", tags=["Projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    project = create_project(db, data, current_user.id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Client not found or does not belong to you"
        )
    return project


@router.get("", response_model=list[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_projects(db, current_user.id)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_one(
    project_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    project = get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update(
    project_id: int,
    data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    project = update_project(db, project_id, data, current_user.id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or client does not belong to you"
        )
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    project_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    deleted = delete_project(db, project_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")