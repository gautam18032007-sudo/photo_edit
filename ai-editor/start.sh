#!/bin/bash
# ═════════════════════════════════════════════
# PIXELMIND - DEVELOPMENT STARTUP (Linux/Mac)
# ═════════════════════════════════════════════

set -e
cd "$(dirname "$0")/backend"

echo ""
echo "🚀 Starting PixelMind Development Environment..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
  echo "❌ Python 3 required. Install from https://python.org"
  exit 1
fi

# Create venv if missing
if [ ! -d ".venv" ]; then
  echo "📦 Creating Python virtual environment..."
  python3 -m venv .venv
fi

source .venv/bin/activate

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install -q -r requirements.txt

# Create .env if missing
if [ ! -f ".env" ]; then
  echo "📝 Creating .env file from template..."
  cp .env.example .env 2>/dev/null || echo "APP_NAME=PixelMind API
DEBUG=False
DATABASE_URL=postgresql://user:password@localhost:5432/pixelmind
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
STORAGE_BACKEND=local
STORAGE_LOCAL_PATH=./storage
REDIS_URL=redis://localhost:6379/0" > .env
  echo "✅ Created .env file"
fi

echo ""
echo "═════════════════════════════════════════════"
echo "🌐 Starting FastAPI Backend (Port 8000)..."
echo "═════════════════════════════════════════════"
echo "📖 API Documentation: http://localhost:8000/api/docs"
echo "🔗 Health Check: http://localhost:8000/api/health"
echo ""

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
echo ""
echo "📝 OTPs will be printed to this console (email not required in dev)"
echo ""

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
