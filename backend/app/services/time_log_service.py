from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.time_log import TimeLog
from app.models.project import Project
from app.models.task import Task
from app.schemas.time_log import TimeLogCreate, TimeLogUpdate


def verify_project_ownership(db: Session, project_id: int, user_id: int) -> bool:
    return db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == user_id
    ).first() is not None


def verify_task_for_log(db: Session, task_id: int, user_id: int, project_id: int) -> bool:
    """Single query that checks: task exists, belongs to user, belongs to project."""
    return db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == user_id,
        Task.project_id == project_id
    ).first() is not None


def get_time_logs(
    db: Session,
    user_id: int,
    project_id: int | None = None,
    task_id: int | None = None
) -> list[TimeLog]:
    query = db.query(TimeLog).filter(TimeLog.user_id == user_id)
    if project_id:
        query = query.filter(TimeLog.project_id == project_id)
    if task_id:
        query = query.filter(TimeLog.task_id == task_id)
    return query.order_by(TimeLog.logged_date.desc()).all()


def get_time_log(db: Session, log_id: int, user_id: int) -> TimeLog | None:
    return db.query(TimeLog).filter(
        TimeLog.id == log_id,
        TimeLog.user_id == user_id
    ).first()


def create_time_log(db: Session, data: TimeLogCreate, user_id: int) -> TimeLog | None:
    if not verify_project_ownership(db, data.project_id, user_id):
        return None
    if data.task_id is not None:
        if not verify_task_for_log(db, data.task_id, user_id, data.project_id):
            return None
    payload = data.model_dump()
    if payload.get("logged_date") is None:
        payload.pop("logged_date")
    log = TimeLog(**payload, user_id=user_id)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def update_time_log(db: Session, log_id: int, data: TimeLogUpdate, user_id: int) -> TimeLog | None:
    log = get_time_log(db, log_id, user_id)
    if not log:
        return None
    update_data = data.model_dump(exclude_unset=True)
    # project_id is immutable after creation — use the existing project_id for task validation
    if "task_id" in update_data and update_data["task_id"] is not None:
        if not verify_task_for_log(db, update_data["task_id"], user_id, log.project_id):
            return None
    for field, value in update_data.items():
        setattr(log, field, value)
    db.commit()
    db.refresh(log)
    return log


def delete_time_log(db: Session, log_id: int, user_id: int) -> bool:
    log = get_time_log(db, log_id, user_id)
    if not log:
        return False
    db.delete(log)
    db.commit()
    return True


def get_project_hours_summary(db: Session, project_id: int, user_id: int) -> dict | None:
    if not verify_project_ownership(db, project_id, user_id):
        return None

    rows = db.query(
        TimeLog.is_billable,
        func.sum(TimeLog.hours).label("total")
    ).filter(
        TimeLog.project_id == project_id,
        TimeLog.user_id == user_id
    ).group_by(TimeLog.is_billable).all()

    billable = Decimal("0")
    non_billable = Decimal("0")

    for row in rows:
        if row.is_billable:
            billable = Decimal(str(row.total))
        else:
            non_billable = Decimal(str(row.total))

    return {
        "project_id": project_id,
        "total_hours": billable + non_billable,
        "billable_hours": billable,
        "non_billable_hours": non_billable
    }