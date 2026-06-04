@echo off
rem AI Study Assistant launcher

set ROOT_DIR=%~dp0

rem Start backend
start "Backend Server" cmd /k "cd /d "%ROOT_DIR%" && call venv\Scripts\activate && cd backend && uvicorn api.main:app --reload"

rem Start frontend
start "Frontend Dev" cmd /k "cd /d "%ROOT_DIR%frontend" && npm run dev"

exit