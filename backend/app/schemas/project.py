from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from decimal import Decimal
from app.models.project import ProjectStatus


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.active
    budget: Optional[Decimal] = None
    deadline: Optional[datetime] = None
    client_id: Optional[int] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    budget: Optional[Decimal] = None
    deadline: Optional[datetime] = None
    client_id: Optional[int] = None


class ProjectResponse(BaseModel):
    id: int
    user_id: int
    client_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    status: ProjectStatus
    budget: Optional[Decimal] = None
    deadline: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}