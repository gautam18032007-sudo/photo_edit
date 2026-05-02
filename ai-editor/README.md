# PixelMind — AI-Powered Photo, Video & Audio Editor

A full-stack web platform for professional AI-assisted media editing.

---

## 🗂 Project Structure

```
ai-editor/
├── frontend/
│   └── index.html          ← Landing page (open directly in browser)
├── backend/
│   ├── main.py             ← FastAPI entry point
│   ├── requirements.txt
│   ├── .env.example        ← Copy to .env and fill in
│   ├── config/settings.py
│   ├── models/             ← SQLAlchemy DB models
│   ├── routes/             ← API endpoint routers
│   ├── services/           ← Business logic + Celery tasks
│   └── utils/              ← JWT, storage, email, logging
├── ai_models/              ← Place PyTorch/TF model files here
└── storage/                ← Local file storage (auto-created)
```

---

## ⚡ Quick Start

### 1. Frontend (Landing Page)
Just open `frontend/index.html` in any browser. No build step required.

### 2. Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database, email, and secret key

# Run database migrations (PostgreSQL must be running)
python -c "from models.database import create_tables; create_tables()"

# Start the API server
uvicorn main:app --reload --port 8000
```

### 3. Celery Worker (Background Processing)

```bash
# In a separate terminal (Redis must be running)
cd backend
celery -A services.celery_app worker --loglevel=info
```

---

## 📡 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/auth/register | Create account |
| POST | /api/auth/verify-otp | Verify email OTP |
| POST | /api/auth/login | Get JWT tokens |
| POST | /api/auth/resend-otp | Resend OTP |
| GET | /api/users/me | Get profile |
| PATCH | /api/users/me | Update profile |
| GET | /api/users/me/activity | Activity log |
| POST | /api/projects/ | Upload + create project |
| GET | /api/projects/ | List projects |
| GET | /api/projects/{id} | Get project |
| POST | /api/projects/{id}/process | Start processing |
| GET | /api/projects/{id}/download | Download output |
| DELETE | /api/projects/{id} | Delete project |
| POST | /api/editor/image/enhance | Manual image adjustments |
| POST | /api/editor/image/ai-enhance | AI auto enhancement |
| POST | /api/editor/image/remove-bg | Background removal |
| POST | /api/editor/image/detect-faces | Face detection |
| POST | /api/editor/audio/analyze | Audio analysis |
| POST | /api/editor/audio/denoise | Noise reduction |
| POST | /api/editor/instruct | Instruction-based editing |

API docs: http://localhost:8000/api/docs

---

## 🏗 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML + CSS + Vanilla JS (or React for dashboard) |
| Backend | FastAPI (Python 3.11+) |
| Database | PostgreSQL + SQLAlchemy |
| Auth | JWT (python-jose) + bcrypt |
| Image AI | Pillow + OpenCV |
| Audio AI | librosa + soundfile |
| Queue | Celery + Redis |
| Storage | Local filesystem (S3-ready) |

---

## 🔐 Security Notes

- All passwords are bcrypt-hashed
- JWT tokens expire (access: 60min, refresh: 7 days)
- OTP expires in 10 minutes
- Files are user-isolated and auto-deleted after export
- Rate limiting: 60 req/min per IP
- Voice cloning requires consent checkbox + activity logging

---

## 📦 Development Phases

- **Phase 1** ✅ Auth + Upload + Image Editing (this codebase)
- **Phase 2** → AI Image Processing (PyTorch models)
- **Phase 3** → Video Editor (FFmpeg integration)
- **Phase 4** → Audio + Voice Cloning
- **Phase 5** → Instruction System (NLP → edits) ✅ (parser built)
