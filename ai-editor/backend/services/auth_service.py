from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.user import User
from utils.security import hash_password, verify_password, generate_otp, otp_expires_at, create_access_token, create_refresh_token
from utils.email import send_otp_email, send_welcome_email
import logging

logger = logging.getLogger(__name__)

def register_user(db: Session, email: str, password: str, full_name: str) -> User:
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    otp = generate_otp()
    user = User(
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
        otp_code=otp,
        otp_expires_at=otp_expires_at(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    send_otp_email(email, otp)
    return user

def verify_otp(db: Session, email: str, otp: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_verified:
        raise HTTPException(status_code=400, detail="Already verified")
    if user.otp_code != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    if datetime.now(timezone.utc) > user.otp_expires_at:
        raise HTTPException(status_code=400, detail="OTP expired — request a new one")
    user.is_active = True
    user.is_verified = True
    user.otp_code = None
    user.otp_expires_at = None
    db.commit()
    send_welcome_email(user.email, user.full_name or "there")
    return user

def login_user(db: Session, email: str, password: str) -> dict:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account not verified — check your email")
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    access = create_access_token({"sub": user.id})
    refresh = create_refresh_token({"sub": user.id})
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}

def resend_otp(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or user.is_verified:
        raise HTTPException(status_code=400, detail="Cannot resend OTP")
    otp = generate_otp()
    user.otp_code = otp
    user.otp_expires_at = otp_expires_at()
    db.commit()
    send_otp_email(email, otp)
