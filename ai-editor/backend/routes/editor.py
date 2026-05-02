from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from models.database import get_db
from models.user import User
from utils.dependencies import get_current_user
from services.image_service import apply_adjustments, ai_auto_enhance, remove_background, apply_blur, detect_faces
from services.audio_service import noise_reduction, trim_silence, adjust_volume, analyze_audio
from services.instruction_service import parse_instruction
from utils.storage import save_upload, output_path
import tempfile, os

router = APIRouter(prefix="/editor", tags=["editor"])

# ── Image endpoints ──
@router.post("/image/enhance")
async def enhance_image(
    file: UploadFile = File(...),
    brightness: float = Form(1.0),
    contrast: float = Form(1.0),
    saturation: float = Form(1.0),
    sharpness: float = Form(1.0),
    noise_reduction: bool = Form(False),
    user: User = Depends(get_current_user),
):
    data = await file.read()
    with tempfile.NamedTemporaryFile(suffix=os.path.splitext(file.filename)[1], delete=False) as tmp:
        tmp.write(data)
        in_path = tmp.name
    out_path = in_path + "_out.jpg"
    settings = dict(brightness=brightness, contrast=contrast, saturation=saturation, sharpness=sharpness, noise_reduction=noise_reduction)
    apply_adjustments(in_path, out_path, settings)
    os.unlink(in_path)
    return FileResponse(out_path, media_type="image/jpeg", filename="enhanced.jpg")

@router.post("/image/ai-enhance")
async def ai_enhance(file: UploadFile = File(...), user: User = Depends(get_current_user)):
    data = await file.read()
    with tempfile.NamedTemporaryFile(suffix=os.path.splitext(file.filename)[1], delete=False) as tmp:
        tmp.write(data)
        in_path = tmp.name
    out_path = in_path + "_ai.jpg"
    result = ai_auto_enhance(in_path, out_path)
    os.unlink(in_path)
    return {"output_path": out_path, "ai_results": result}

@router.post("/image/remove-bg")
async def remove_bg(file: UploadFile = File(...), user: User = Depends(get_current_user)):
    data = await file.read()
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp.write(data)
        in_path = tmp.name
    out_path = in_path + "_nobg.png"
    result = remove_background(in_path, out_path)
    os.unlink(in_path)
    return FileResponse(result, media_type="image/png", filename="no_background.png")

@router.post("/image/detect-faces")
async def faces(file: UploadFile = File(...), user: User = Depends(get_current_user)):
    data = await file.read()
    with tempfile.NamedTemporaryFile(suffix=os.path.splitext(file.filename)[1], delete=False) as tmp:
        tmp.write(data)
        in_path = tmp.name
    faces = detect_faces(in_path)
    os.unlink(in_path)
    return {"faces": faces, "count": len(faces)}

# ── Audio endpoints ──
@router.post("/audio/analyze")
async def audio_analyze(file: UploadFile = File(...), user: User = Depends(get_current_user)):
    data = await file.read()
    with tempfile.NamedTemporaryFile(suffix=os.path.splitext(file.filename)[1], delete=False) as tmp:
        tmp.write(data)
        in_path = tmp.name
    result = analyze_audio(in_path)
    os.unlink(in_path)
    return result

@router.post("/audio/denoise")
async def denoise(file: UploadFile = File(...), strength: float = Form(0.75), user: User = Depends(get_current_user)):
    data = await file.read()
    with tempfile.NamedTemporaryFile(suffix=os.path.splitext(file.filename)[1], delete=False) as tmp:
        tmp.write(data)
        in_path = tmp.name
    out_path = in_path + "_clean.wav"
    noise_reduction(in_path, out_path, strength)
    os.unlink(in_path)
    return FileResponse(out_path, media_type="audio/wav", filename="denoised.wav")

# ── Instruction endpoint ──
@router.post("/instruct")
def run_instruction(instruction: str = Form(...), user: User = Depends(get_current_user)):
    result = parse_instruction(instruction)
    return result
