# PixelMind — AI-Powered Photo, Video & Audio Editor

A full-stack, cloud-native web platform for professional AI-assisted media editing. Built with FastAPI, PostgreSQL, AWS S3, and Celery for scalable processing.

---

## ✨ Features

✅ **Photo Editing**
- AI auto-enhancement
- Brightness, contrast, saturation control
- Background removal
- Face detection & enhancement
- Noise reduction

✅ **Video Editing**
- Trim, crop, rotate
- Effects and transitions
- Audio extraction
- Format conversion

✅ **Audio Editing**
- Noise removal
- Equalization
- Voice enhancement
- Format conversion

✅ **Cloud Processing**
- AWS S3 storage
- Celery background jobs
- Redis caching
- Scalable architecture

---

## 🗂 Project Structure

```
ai-editor/
├── frontend/
│   ├── index.html              ← Landing page + editor UI
│   ├── api.js                  ← API client with authentication
│   └── styles/
├── backend/
│   ├── main.py                 ← FastAPI entry point
│   ├── requirements.txt         ← Python dependencies
│   ├── .env.example             ← Environment template
│   ├── config/
│   │   └── settings.py          ← Configuration management
│   ├── models/
│   │   ├── database.py          ← SQLAlchemy ORM setup
│   │   ├── user.py              ← User model
│   │   └── project.py           ← Project model
│   ├── routes/
│   │   ├── auth.py              ← Authentication endpoints
│   │   ├── projects.py          ← Project CRUD
│   │   ├── editor.py            ← Editing endpoints
│   │   └── users.py             ← User profile endpoints
│   ├── services/
│   │   ├── celery_app.py        ← Celery configuration
│   │   ├── image_service.py     ← Image processing
│   │   ├── audio_service.py     ← Audio processing
│   │   ├── video_service.py     ← Video processing
│   │   └── tasks.py             ← Background tasks
│   └── utils/
│       ├── storage.py           ← S3 + Local storage (dual)
│       ├── security.py          ← JWT & hashing
│       ├── email.py             ← Email notifications
│       └── dependencies.py       ← Dependency injection
├── Procfile                     ← Render deployment config
├── render.yaml                  ← Infrastructure as Code (IaC)
├── vercel.json                  ← Vercel frontend config
├── DEPLOYMENT.md                ← Cloud deployment guide
└── .gitignore                   ← Git exclusions
```

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- PostgreSQL
- Redis
- Node.js (optional)

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your local settings

# Initialize database
python -c "from models.database import create_tables; create_tables()"

# Start API server
uvicorn main:app --reload --port 8000
```

Backend runs at: **http://localhost:8000**
API Docs: **http://localhost:8000/api/docs**

### 2. Frontend Setup

```bash
cd frontend

# Option A: Open directly in browser
open index.html

# Option B: Use local server
python -m http.server 3000
# Visit http://localhost:3000
```

### 3. Background Job Processing (Celery)

```bash
# In a new terminal
cd backend
celery -A services.celery_app worker --loglevel=info
```

### 4. Redis Cache

```bash
# Make sure Redis is running
redis-server
```

---

## 📡 API Endpoints

**Authentication**
- `POST /api/auth/register` - Create account
- `POST /api/auth/login` - Get JWT tokens
- `GET /api/auth/me` - Current user info

**Projects**
- `POST /api/projects` - Create project
- `GET /api/projects` - List projects
- `GET /api/projects/{id}` - Get project
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project

**Image Processing**
- `POST /api/editor/process/image` - Apply effects
- `POST /api/editor/image/enhance` - Manual adjustments
- `POST /api/editor/image/ai-enhance` - AI auto-enhance
- `POST /api/editor/image/remove-bg` - Background removal
- `POST /api/editor/image/detect-faces` - Face detection

**Video & Audio**
- `POST /api/editor/process/video` - Video effects
- `POST /api/editor/process/audio` - Audio effects
- `POST /api/editor/export` - Export file

---

## 🏗 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | HTML5 + CSS3 + Vanilla JavaScript |
| **Backend** | FastAPI (Python 3.11) |
| **Database** | PostgreSQL 15 |
| **Cache** | Redis 7 |
| **Storage** | AWS S3 (production) / Local (dev) |
| **Job Queue** | Celery + Redis |
| **Image Processing** | OpenCV + Pillow |
| **Audio Processing** | Librosa + SoundFile |
| **Deployment** | Render (backend) + Vercel (frontend) |

---

## ☁️ Cloud Deployment

### Option 1: Deploy to Render + Vercel (Recommended)

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for complete step-by-step guide covering:
- AWS S3 setup
- Render backend deployment
- PostgreSQL on Render
- Redis on Render
- Vercel frontend deployment
- GitHub integration
- Environment variables
- Security configuration

### Option 2: Docker Deployment

```dockerfile
# Build image
docker build -t pixelmind:latest -f backend/Dockerfile .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  -e STORAGE_BACKEND="s3" \
  pixelmind:latest
```

### Option 3: Railway / Heroku / DigitalOcean

Similar to Render setup. Refer to `render.yaml` for environment structure.

---

## 🔐 Environment Variables

Create `.env` file from `.env.example`:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/pixelmind

# Security
SECRET_KEY=your-256-bit-random-secret-key
DEBUG=False

# AWS S3
STORAGE_BACKEND=s3
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_S3_BUCKET=pixelmind-files

# Redis/Celery
REDIS_URL=redis://localhost:6379/0

# Email
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# URLs
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

---

## 📊 File Storage

The system supports **dual storage**:

**Local (Development)**
```env
STORAGE_BACKEND=local
STORAGE_LOCAL_PATH=./storage
```

**AWS S3 (Production)**
```env
STORAGE_BACKEND=s3
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_S3_BUCKET=pixelmind-files
```

Automatically routes uploads to configured backend in `utils/storage.py`.

---

## 🔄 Workflow: Upload → Process → Download

1. **User uploads file** → Frontend sends to `/editor/upload`
2. **Backend stores** → S3 or local storage
3. **Celery task created** → Background processing starts
4. **AI processing** → OpenCV, Librosa, custom models
5. **Result saved** → New file to storage
6. **Download link** → User receives presigned S3 URL or local path

---

## 🧪 Testing

```bash
# Run API tests
pytest backend/tests/ -v

# Run with coverage
pytest backend/tests/ --cov=backend

# Test specific endpoint
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"pass","name":"Test"}'
```

---

## 📈 Scaling Strategies

### Small Scale (MVP)
- Single Render instance
- Shared PostgreSQL
- Free Redis tier
- Local or S3 storage

### Medium Scale
- Multiple Render instances with load balancing
- Managed PostgreSQL
- Dedicated Redis
- AWS S3 with CloudFront CDN

### Enterprise Scale
- Kubernetes (AWS EKS / Azure AKS)
- RDS Multi-AZ
- ElastiCache (Redis)
- S3 with Lambda for thumbnails
- CloudFront for CDN

---

## 🐛 Troubleshooting

**Issue: 502 Bad Gateway**
```bash
# Check backend logs
tail -f logs/error.log
# Restart service
```

**Issue: S3 Upload Fails**
```bash
# Verify AWS credentials
# Check S3 bucket permissions
# Ensure region matches
```

**Issue: Celery Tasks Not Processing**
```bash
# Check Redis connection
redis-cli ping
# Check Celery worker logs
# Restart worker: celery -A services.celery_app worker
```

**Issue: CORS Errors**
```bash
# Update FRONTEND_URL in backend .env
# Restart backend server
```

---

## 🔒 Security

✅ Implemented:
- JWT authentication with secure tokens
- CORS protection with whitelisted origins
- Rate limiting (60 req/min default)
- Password hashing with bcrypt
- SQL injection prevention (SQLAlchemy ORM)
- HTTPS in production
- Environment variables for secrets
- File upload validation

---

## 📝 License

MIT License - See LICENSE file

---

## 🤝 Contributing

1. Fork repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push branch: `git push origin feature/amazing-feature`
5. Open Pull Request

---

## 📧 Support & Issues

Report bugs at: https://github.com/gautam18032007-sudo/photo_edit/issues

---

## 🎯 Roadmap

- [ ] Mobile app (React Native)
- [ ] Real-time collaboration
- [ ] GPU-accelerated processing
- [ ] Advanced AI models (DALL-E integration)
- [ ] Subscription billing
- [ ] Team workspaces
- [ ] API marketplace

---

**⭐ Give us a star if you find this project helpful!**
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
