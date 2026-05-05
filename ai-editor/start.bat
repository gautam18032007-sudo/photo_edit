@echo off
REM ═════════════════════════════════════════════
REM PIXELMIND - DEVELOPMENT STARTUP (Windows)
REM ═════════════════════════════════════════════

echo.
echo 🚀 Starting PixelMind Development Environment...
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Install Python 3.11+ from python.org
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
cd /d "%~dp0backend"
if not exist ".venv" (
    echo 📦 Creating Python virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install dependencies
echo 📚 Installing Python dependencies...
pip install -q -r requirements.txt

REM Setup environment file
if not exist ".env" (
    echo 📝 Creating .env file from template...
    copy .env.example .env
    echo ✅ Created .env - Please edit it with your settings
)

echo.
echo ═════════════════════════════════════════════
echo 🌐 Starting FastAPI Backend (Port 8000)...
echo ═════════════════════════════════════════════
echo 📖 API Documentation: http://localhost:8000/api/docs
echo.

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
