from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.db.database import get_db
from app.api.deps import get_current_user
from app.schemas.time_log import TimeLogCreate, TimeLogUpdate, TimeLogResponse, ProjectHoursSummary
from app.services.time_log_service import (
    get_time_logs, get_time_log, create_time_log,
    update_time_log, delete_time_log, get_project_hours_summary
)

router = APIRouter(prefix="/api/time-logs", tags=["Time Logs"])


@router.post("", response_model=TimeLogResponse, status_code=status.HTTP_201_CREATED)
def create(
    data: TimeLogCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    log = create_time_log(db, data, current_user.id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Project or task not found or does not belong to you"
        )
    return log


@router.get("/summary/{project_id}", response_model=ProjectHoursSummary)
def project_summary(
    project_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    summary = get_project_hours_summary(db, project_id, current_user.id)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or does not belong to you"
        )
    return summary


@router.get("", response_model=list[TimeLogResponse])
def list_logs(
    project_id: Optional[int] = Query(None, description="Filter by project"),
    task_id: Optional[int] = Query(None, description="Filter by task"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return get_time_logs(db, current_user.id, project_id, task_id)


@router.get("/{log_id}", response_model=TimeLogResponse)
def get_one(
    log_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    log = get_time_log(db, log_id, current_user.id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time log not found"
        )
    return log


@router.put("/{log_id}", response_model=TimeLogResponse)
def update(
    log_id: int,
    data: TimeLogUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    log = update_time_log(db, log_id, data, current_user.id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time log not found"
        )
    return log


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    log_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    deleted = delete_time_log(db, log_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time log not found"
        )