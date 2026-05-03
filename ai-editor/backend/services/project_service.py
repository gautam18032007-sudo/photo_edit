from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.project import Project, ProjectStatus, ProjectType
from utils.storage import save_upload, output_path, generate_thumbnail
import uuid

def create_project(db: Session, user_id: str, name: str, project_type: str, mode: str, file_bytes: bytes, filename: str) -> Project:
    file_path = save_upload(user_id, file_bytes, filename)
    project = Project(
        owner_id=user_id,
        name=name,
        project_type=ProjectType(project_type),
        mode=mode,
        input_file_path=file_path,
        status=ProjectStatus.PENDING,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

def get_project(db: Session, project_id: str, user_id: str) -> Project:
    p = db.query(Project).filter(Project.id == project_id, Project.owner_id == user_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return p

def list_projects(db: Session, user_id: str, skip: int = 0, limit: int = 20) -> list:
    return (
        db.query(Project)
        .filter(Project.owner_id == user_id)
        .order_by(Project.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def update_project_status(db: Session, project_id: str, status: ProjectStatus, output_file: str = None, ai_results: dict = None):
    p = db.query(Project).filter(Project.id == project_id).first()
    if p:
        p.status = status
        if output_file:
            p.output_file_path = output_file
        if ai_results:
            p.ai_results = ai_results
        db.commit()

def delete_project(db: Session, project_id: str, user_id: str):
    p = get_project(db, project_id, user_id)
    db.delete(p)
    db.commit()
