@echo off
rem AI Study Assistant benchmark launcher

set ROOT_DIR=%~dp0

rem Start backend server in a separate terminal
start "Backend Server" cmd /k "cd /d "%ROOT_DIR%backend" && call "%ROOT_DIR%venv\Scripts\activate" && uvicorn api.main:app --reload"

rem Wait a few seconds and then run benchmark runner in another terminal
start "Benchmark Runner" cmd /k "cd /d "%ROOT_DIR%" && timeout /t 10 /nobreak >nul && call "%ROOT_DIR%venv\Scripts\activate" && python backend\benchmark_runner.py"

exit
