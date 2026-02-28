from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Numeric, Boolean, String
from sqlalchemy.sql import func
from app.db.database import Base


class TimeLog(Base):
    __tablename__ = "time_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True, index=True)

    description = Column(Text, nullable=True)
    hours = Column(Numeric(6, 2), nullable=False)
    hourly_rate = Column(Numeric(10, 2), nullable=True)
    is_billable = Column(Boolean, default=True, nullable=False)
    logged_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<TimeLog id={self.id} hours={self.hours}>"