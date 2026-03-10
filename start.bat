@echo off
echo Starting DataLens AI (Flask + React)...

:: Start Flask backend
start "DataLens-Flask" cmd /k "cd /d %~dp0 && venv\Scripts\activate && python flask_app.py"

:: Start React dev server
start "DataLens-React" cmd /k "cd /d %~dp0\frontend && npm run dev"

echo.
echo Flask API: http://localhost:5000
echo React App: http://localhost:5173
echo.
