@echo off
rem AI Study Assistant startup helper
rem This script starts the backend and frontend in separate windows.

set ROOT_DIR=%~dp0

rem Backend setup and launch
start "Backend Server" cmd /k "cd /d "%ROOT_DIR%backend" && if not exist venv python -m venv venv && call venv\Scripts\activate.bat && pip install -r requirements.txt && python app.py"

rem Frontend setup and launch
start "Frontend Dev" cmd /k "cd /d "%ROOT_DIR%frontend" && npm install && npm run dev"

echo Startup commands issued. Two new windows should open for backend and frontend.
pause
