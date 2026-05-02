from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from models.database import Base

class ProjectType(str, enum.Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"

class ProjectStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"

class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    project_type = Column(Enum(ProjectType), nullable=False)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PENDING)
    mode = Column(String, default="manual")  # manual | ai
    input_file_path = Column(String, nullable=True)
    output_file_path = Column(String, nullable=True)
    thumbnail_path = Column(String, nullable=True)
    edit_settings = Column(JSON, default={})   # stores all edit params
    ai_results = Column(JSON, default={})      # AI detection/analysis output
    celery_task_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    exported_at = Column(DateTime(timezone=True), nullable=True)

    owner = relationship("User", back_populates="projects")

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String, nullable=False)   # "login" | "upload" | "export" | "voice_clone" etc.
    detail = Column(Text, nullable=True)
    ip_address = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="activity_logs")
