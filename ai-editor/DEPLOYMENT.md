# 🚀 PixelMind Cloud Deployment Guide

Complete guide to deploy PixelMind to production using Render (Backend) and Vercel (Frontend).

---

## 📋 Prerequisites

- GitHub Account (repo already created)
- AWS Account (for S3 storage)
- Render Account (render.com)
- Vercel Account (vercel.com)
- PostgreSQL Database
- Redis Instance

---

## 🔹 Step 1: Prepare AWS S3 (Cloud Storage)

### 1.1 Create S3 Bucket

```bash
# Go to AWS Console > S3
# Click "Create Bucket"
# Bucket name: pixelmind-files
# Region: us-east-1
# Block all public access: ✓
# Create bucket
```

### 1.2 Create AWS IAM User

```bash
# Go to AWS > IAM > Users
# Create user: pixelmind-api
# Attach policy: AmazonS3FullAccess
# Create access key
# Save: Access Key ID & Secret Access Key
```

### 1.3 Add to Backend .env

```env
STORAGE_BACKEND=s3
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
AWS_S3_BUCKET=pixelmind-files
AWS_REGION=us-east-1
```

---

## 🔹 Step 2: Deploy Backend to Render

### 2.1 Connect GitHub to Render

1. Go to **render.com** → Sign up/Login
2. Click **New** → **Web Service**
3. Connect GitHub repository
4. Select your repository

### 2.2 Configure Render Service

```yaml
Service Name: pixelmind-api
Runtime: Python 3.11
Build Command: pip install -r requirements.txt && cd backend
Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 2.3 Add Environment Variables

Go to **Environment** tab and add:

```env
DATABASE_URL=postgresql://user:pass@host:5432/pixelmind
SECRET_KEY=your-256-bit-random-key
DEBUG=False
STORAGE_BACKEND=s3
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_S3_BUCKET=pixelmind-files
AWS_REGION=us-east-1
REDIS_URL=redis://your-redis-url:6379/0
FRONTEND_DEPLOY_URL=https://your-frontend.vercel.app
```

### 2.4 Add PostgreSQL Database

1. Go to **Dashboard** → **New** → **PostgreSQL**
2. Database name: `pixelmind`
3. User: `pixelmind_user`
4. Region: Same as backend
5. Copy connection string to `DATABASE_URL`

### 2.5 Add Redis

1. Go to **Dashboard** → **New** → **Redis**
2. Name: `pixelmind-redis`
3. Copy URL to `REDIS_URL`

### 2.6 Deploy

- Click **Deploy**
- Wait for build to complete
- Copy backend URL (e.g., `https://pixelmind-api.onrender.com`)

### 2.7 Create Celery Worker

1. Go to **Dashboard** → **New** → **Background Worker**
2. Select same repository
3. Start Command: `celery -A services.celery_app worker --loglevel=info`
4. Add same environment variables
5. Deploy

---

## 🔹 Step 3: Deploy Frontend to Vercel

### 3.1 Import Project to Vercel

1. Go to **vercel.com** → **Add New** → **Project**
2. Import GitHub repository
3. Select `ai-editor` directory

### 3.2 Configure Vercel

```
Framework: Static Site (No Framework)
Build Command: (leave empty)
Output Directory: frontend
Root Directory: .
```

### 3.3 Add Environment Variables

```env
REACT_APP_API_URL=https://pixelmind-api.onrender.com
```

### 3.4 Deploy

- Click **Deploy**
- Get your frontend URL (e.g., `https://pixelmind.vercel.app`)

### 3.5 Update Backend CORS

Update backend `FRONTEND_DEPLOY_URL` in Render dashboard with Vercel URL.

---

## 🔹 Step 4: Update Frontend API Configuration

Edit `frontend/api.js`:

```javascript
const getAPIUrl = () => {
  if (window.location.hostname === 'vercel.app') {
    return 'https://pixelmind-api.onrender.com/api';
  }
  return 'http://localhost:8000/api';
};
```

---

## 🔹 Step 5: Test Cloud Setup

### 5.1 Test Backend Health

```bash
curl https://pixelmind-api.onrender.com/api/health
# Should return: {"status": "ok", "version": "1.0.0"}
```

### 5.2 Test S3 Upload

1. Open frontend: `https://pixelmind.vercel.app`
2. Upload a file
3. Check AWS S3 console - file should appear in bucket

### 5.3 Test Celery Worker

Upload large file → should process in background → check Render logs

---

## 🔹 Step 6: Security Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Use strong `SECRET_KEY` (256-bit)
- [ ] Enable HTTPS (auto in Render/Vercel)
- [ ] Restrict S3 bucket to private
- [ ] Use environment variables for all secrets
- [ ] Add rate limiting (already configured)
- [ ] Enable CORS only for your domain
- [ ] Monitor logs for errors

---

## 🔹 Step 7: Scaling & Monitoring

### Monitor Backend

- Render Dashboard → Logs
- Check CPU, Memory, Requests

### Monitor S3 Usage

- AWS Console → S3 → Metrics
- Set up CloudWatch alerts

### Auto-Scaling

- Render: Automatic based on traffic
- Vercel: Automatic serverless scaling

---

## 🔹 Troubleshooting

### Error: 502 Bad Gateway

```bash
# Check backend logs in Render
# Ensure DATABASE_URL is correct
# Restart service
```

### Error: CORS Issues

```bash
# Update FRONTEND_DEPLOY_URL in backend
# Restart backend service
```

### Error: S3 Upload Fails

```bash
# Check AWS credentials
# Verify bucket name
# Check IAM permissions
```

### Error: Celery Tasks Not Processing

```bash
# Check Redis connection
# Check Celery worker logs
# Restart worker service
```

---

## 🔹 Local Development Setup

Before deploying, test locally:

```bash
# 1. Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with local values
python -c "from models.database import create_tables; create_tables()"
uvicorn main:app --reload

# 2. Frontend (in new terminal)
cd frontend
# Open index.html in browser or use:
python -m http.server 3000

# 3. Celery Worker (in new terminal)
cd backend
celery -A services.celery_app worker --loglevel=info

# 4. Redis (in new terminal)
redis-server
```

---

## 📱 Production URLs

After deployment:

- **Frontend**: `https://your-frontend.vercel.app`
- **Backend API**: `https://pixelmind-api.onrender.com/api`
- **API Docs**: `https://pixelmind-api.onrender.com/api/docs`

---

## 🔄 CI/CD with GitHub Actions (Optional)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Render
        run: |
          curl https://api.render.com/deploy/srv-${{ secrets.RENDER_SERVICE_ID }}?key=${{ secrets.RENDER_DEPLOY_KEY }}
```

---

## ✅ Final Checklist

- [x] Backend deployed to Render
- [x] Frontend deployed to Vercel
- [x] S3 storage configured
- [x] Database connected
- [x] Redis cache enabled
- [x] Celery workers running
- [x] CORS properly configured
- [x] Environment variables set
- [x] API endpoints tested
- [x] File upload working

---

**🎉 Congratulations! Your AI Editor is now live in the cloud!**
