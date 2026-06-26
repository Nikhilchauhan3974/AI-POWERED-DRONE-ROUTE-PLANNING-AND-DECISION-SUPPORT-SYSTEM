@echo off
cd /d "D:\CFAI Project"
echo Starting Backend Server...
python -m uvicorn backend.main:app --reload
pause
