from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from models.database import get_db
from services import auth_service
from utils.activity_log import log

router = APIRouter(prefix="/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class OTPRequest(BaseModel):
    email: EmailStr
    otp: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ResendRequest(BaseModel):
    email: EmailStr

@router.post("/register", status_code=201)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    user = auth_service.register_user(db, body.email, body.password, body.full_name)
    return {"message": "OTP sent to your email. Please verify.", "user_id": user.id}

@router.post("/verify-otp")
def verify_otp(body: OTPRequest, request: Request, db: Session = Depends(get_db)):
    user = auth_service.verify_otp(db, body.email, body.otp)
    log(db, user.id, "otp_verified", ip=request.client.host)
    return {"message": "Email verified. You can now log in."}

@router.post("/login")
def login(body: LoginRequest, request: Request, db: Session = Depends(get_db)):
    tokens = auth_service.login_user(db, body.email, body.password)
    return tokens

@router.post("/resend-otp")
def resend(body: ResendRequest, db: Session = Depends(get_db)):
    auth_service.resend_otp(db, body.email)
    return {"message": "New OTP sent."}
