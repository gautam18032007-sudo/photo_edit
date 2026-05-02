from sqlalchemy.orm import Session
from models.project import ActivityLog

def log(db: Session, user_id: str, action: str, detail: str = None, ip: str = None):
    entry = ActivityLog(user_id=user_id, action=action, detail=detail, ip_address=ip)
    db.add(entry)
    db.commit()
