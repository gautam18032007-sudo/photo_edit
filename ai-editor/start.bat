@echo off
echo PixelMind AI Editor — Starting...
cd /d "%~dp0backend"

if not exist ".venv" (
  echo Creating virtual environment...
  python -m venv .venv
)

call .venv\Scripts\activate.bat
pip install -q -r requirements-dev.txt

echo.
echo Starting server on http://localhost:8000
echo Frontend:  http://localhost:8000/
echo API Docs:  http://localhost:8000/api/docs
echo.

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
