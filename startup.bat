@echo off
rem AI Study Assistant launcher

set ROOT_DIR=%~dp0

rem Start backend
start "Backend Server" cmd /k "cd /d "%ROOT_DIR%backend" && python app.py"

rem Start frontend
start "Frontend Dev" cmd /k "cd /d "%ROOT_DIR%frontend" && npm run dev"

exit