\
@echo off
REM Minimal runner for Windows Companion
REM 1) Copy config.example.json -> config.json and edit backend url if needed.
REM 2) Create venv and install deps once.

if not exist .venv (
  python -m venv .venv
)

call .venv\Scripts\activate
pip install -r requirements.txt
python companion.py
