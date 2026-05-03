import os
import uuid
import shutil
from pathlib import Path
from config.settings import get_settings

settings = get_settings()
BASE = Path(settings.STORAGE_LOCAL_PATH)

def _ensure(path: Path):
    path.mkdir(parents=True, exist_ok=True)

def upload_path(user_id: str, filename: str) -> Path:
    p = BASE / "uploads" / user_id
    _ensure(p)
    return p / filename

def output_path(user_id: str, filename: str) -> Path:
    p = BASE / "outputs" / user_id
    _ensure(p)
    return p / filename

def temp_path(filename: str) -> Path:
    p = BASE / "temp"
    _ensure(p)
    return p / filename

def save_upload(user_id: str, file_bytes: bytes, original_name: str) -> str:
    ext = Path(original_name).suffix.lower()
    unique_name = f"{uuid.uuid4()}{ext}"
    dest = upload_path(user_id, unique_name)
    dest.write_bytes(file_bytes)
    return str(dest)

def delete_file(path: str):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass

def cleanup_user_temp(user_id: str):
    """Delete all temp files for a user after export."""
    for folder in ["uploads", "temp"]:
        p = BASE / folder / user_id
        if p.exists():
            shutil.rmtree(p, ignore_errors=True)
