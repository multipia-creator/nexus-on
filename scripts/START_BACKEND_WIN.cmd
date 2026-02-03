\
@echo off
cd /d %~dp0..\backend
if not exist .venv (
  python -m venv .venv
)
call .venv\Scripts\activate
pip install -r requirements.txt
set CORS_ORIGINS=http://localhost:5173
uvicorn app.main:app --reload --port 8000
