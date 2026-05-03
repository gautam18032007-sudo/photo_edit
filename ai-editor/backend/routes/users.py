from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models.database import get_db
from models.user import User
from models.project import ActivityLog
from utils.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

class ProfileUpdate(BaseModel):
    full_name: str | None = None

@router.get("/me")
def get_profile(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "plan": user.plan,
        "is_verified": user.is_verified,
        "created_at": user.created_at,
        "export_count_month": user.export_count_month,
    }

@router.patch("/me")
def update_profile(body: ProfileUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if body.full_name:
        user.full_name = body.full_name
    db.commit()
    return {"message": "Profile updated"}

@router.get("/me/activity")
def activity_log(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    logs = (
        db.query(ActivityLog)
        .filter(ActivityLog.user_id == user.id)
        .order_by(ActivityLog.created_at.desc())
        .limit(50)
        .all()
    )
    return logs
