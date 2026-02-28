from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional
from decimal import Decimal


class TimeLogCreate(BaseModel):
    project_id: int
    task_id: Optional[int] = None
    description: Optional[str] = None
    hours: Decimal
    hourly_rate: Optional[Decimal] = None
    is_billable: bool = True
    logged_date: Optional[datetime] = None

    @field_validator("hours")
    @classmethod
    def hours_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Hours must be greater than 0")
        if v > 24:
            raise ValueError("Cannot log more than 24 hours in a single entry")
        return v


class TimeLogUpdate(BaseModel):
    task_id: Optional[int] = None
    description: Optional[str] = None
    hours: Optional[Decimal] = None
    hourly_rate: Optional[Decimal] = None
    is_billable: Optional[bool] = None
    logged_date: Optional[datetime] = None

    @field_validator("hours")
    @classmethod
    def hours_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Hours must be greater than 0")
        if v is not None and v > 24:
            raise ValueError("Cannot log more than 24 hours in a single entry")
        return v


class TimeLogResponse(BaseModel):
    id: int
    user_id: int
    project_id: int
    task_id: Optional[int] = None
    description: Optional[str] = None
    hours: Decimal
    hourly_rate: Optional[Decimal] = None
    is_billable: bool
    logged_date: datetime
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectHoursSummary(BaseModel):
    project_id: int
    total_hours: Decimal
    billable_hours: Decimal
    non_billable_hours: Decimal