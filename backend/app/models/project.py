import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class ProjectStatus(str, enum.Enum):
    active = "active"
    on_hold = "on_hold"
    completed = "completed"
    cancelled = "cancelled"


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="SET NULL"), nullable=True, index=True)

    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.active, nullable=False)
    budget = Column(Numeric(10, 2), nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Project id={self.id} name={self.name}>"