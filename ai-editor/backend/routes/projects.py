from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from models.database import get_db
from models.user import User
from models.project import ProjectStatus
from utils.dependencies import get_current_user
from utils.activity_log import log
from services import project_service
from services.tasks import process_image_task, process_audio_task
import json

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/", status_code=201)
async def create_project(
    name: str = Form(...),
    project_type: str = Form(...),  # image | video | audio
    mode: str = Form("manual"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    file_bytes = await file.read()
    project = project_service.create_project(db, user.id, name, project_type, mode, file_bytes, file.filename)
    log(db, user.id, "upload", f"Project {project.id} ({project_type})")
    return {"project_id": project.id, "status": project.status}

@router.get("/")
def list_projects(skip: int = 0, limit: int = 20, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    projects = project_service.list_projects(db, user.id, skip, limit)
    return projects

@router.get("/{project_id}")
def get_project(project_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return project_service.get_project(db, project_id, user.id)

@router.post("/{project_id}/process")
def process_project(
    project_id: str,
    settings_json: str = Form("{}"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    project = project_service.get_project(db, project_id, user.id)
    settings = json.loads(settings_json)
    output = project.input_file_path.replace("/uploads/", "/outputs/").replace(f"/{user.id}/", f"/{user.id}/out_")

    if project.project_type.value == "image":
        task = process_image_task.delay(project_id, project.input_file_path, output, settings)
    elif project.project_type.value == "audio":
        task = process_audio_task.delay(project_id, project.input_file_path, output, settings)
    else:
        raise HTTPException(status_code=422, detail="Video processing not yet implemented in this route")

    project_service.update_project_status(db, project_id, ProjectStatus.PROCESSING)
    db.query(type(project)).filter_by(id=project_id).update({"celery_task_id": task.id})
    db.commit()
    return {"task_id": task.id, "status": "processing"}

@router.get("/{project_id}/download")
def download(project_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    project = project_service.get_project(db, project_id, user.id)
    if not project.output_file_path:
        raise HTTPException(status_code=404, detail="Output not ready")
    log(db, user.id, "export", f"Project {project_id}")
    return FileResponse(project.output_file_path, filename=f"pixelmind_{project_id[:8]}")

@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    project_service.delete_project(db, project_id, user.id)
