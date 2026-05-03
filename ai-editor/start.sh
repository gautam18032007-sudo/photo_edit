#!/bin/bash
# PixelMind AI Editor — Quick Start
# Run from the project root: bash start.sh

set -e
cd "$(dirname "$0")/backend"

echo "🎨 PixelMind AI Editor"
echo "========================"

# Check Python
if ! command -v python3 &> /dev/null; then
  echo "❌ Python 3 required. Install from https://python.org"
  exit 1
fi

# Create venv if missing
if [ ! -d ".venv-linux" ]; then
  echo "📦 Creating virtual environment..."
  python3 -m venv .venv-linux
fi

source .venv-linux/bin/activate

# Install deps
echo "📦 Installing dependencies..."
pip install -q -r requirements-dev.txt

# Create .env if missing
if [ ! -f ".env" ]; then
  cp .env.example .env 2>/dev/null || echo "APP_NAME=PixelMind API
DEBUG=true
DATABASE_URL=sqlite:///./pixelmind.db
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
OTP_EXPIRE_MINUTES=10
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USER=
SMTP_PASSWORD=
FROM_EMAIL=noreply@pixelmind.app
STORAGE_BACKEND=local
STORAGE_LOCAL_PATH=./storage" > .env
  echo "✅ Created .env with SQLite config"
fi

echo ""
echo "🚀 Starting server on http://localhost:8000"
echo "   Frontend:  http://localhost:8000/"
echo "   API docs:  http://localhost:8000/api/docs"
echo "   Health:    http://localhost:8000/api/health"
echo ""
echo "📝 OTPs will be printed to this console (email not required in dev)"
echo ""

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
