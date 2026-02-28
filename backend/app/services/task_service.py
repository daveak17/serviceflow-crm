from sqlalchemy.orm import Session
from app.models.task import Task
from app.models.project import Project
from app.schemas.task import TaskCreate, TaskUpdate


def verify_project_ownership(db: Session, project_id: int, user_id: int) -> bool:
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == user_id
    ).first()
    return project is not None


def get_tasks(db: Session, user_id: int, project_id: int | None = None) -> list[Task]:
    query = db.query(Task).filter(Task.user_id == user_id)
    if project_id:
        query = query.filter(Task.project_id == project_id)
    return query.order_by(Task.created_at.desc()).all()


def get_task(db: Session, task_id: int, user_id: int) -> Task | None:
    return (
        db.query(Task)
        .filter(Task.id == task_id, Task.user_id == user_id)
        .first()
    )


def create_task(db: Session, data: TaskCreate, user_id: int) -> Task | None:
    if not verify_project_ownership(db, data.project_id, user_id):
        return None
    task = Task(**data.model_dump(), user_id=user_id)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def update_task(db: Session, task_id: int, data: TaskUpdate, user_id: int) -> Task | None:
    task = get_task(db, task_id, user_id)
    if not task:
        return None
    update_data = data.model_dump(exclude_unset=True)
    if "project_id" in update_data:
        if not verify_project_ownership(db, update_data["project_id"], user_id):
            return None
    for field, value in update_data.items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task_id: int, user_id: int) -> bool:
    task = get_task(db, task_id, user_id)
    if not task:
        return False
    db.delete(task)
    db.commit()
    return True