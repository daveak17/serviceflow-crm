from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.api.deps import get_current_user
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.services.task_service import (
    get_tasks, get_task, create_task, update_task, delete_task
)

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create(
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    task = create_task(db, data, current_user.id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Project not found or does not belong to you"
        )
    return task


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    project_id: Optional[int] = Query(None, description="Filter tasks by project"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_tasks(db, current_user.id, project_id)


@router.get("/{task_id}", response_model=TaskResponse)
def get_one(
    task_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    task = get_task(db, task_id, current_user.id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update(
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    task = update_task(db, task_id, data, current_user.id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    task_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    deleted = delete_task(db, task_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")