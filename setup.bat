@echo off
REM Setup script for DataLens AI - GenAI Data Intelligence Dashboard
REM Run this script to set up the application environment (Backend + Frontend)

echo.
echo ========================================
echo DataLens AI - GenAI Data Intelligence
echo Setup Script (Flask + React)
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org
    pause
    exit /b 1
)

echo ✅ Python found
python --version
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed or not in PATH
    echo Please install Node.js 16+ from https://nodejs.org
    pause
    exit /b 1
)

echo ✅ Node.js found
node --version
npm --version
echo.

REM ========================================
REM Backend Setup
REM ========================================
echo ========================================
echo Setting up Backend (Python/Flask)
echo ========================================
echo.

REM Create virtual environment
echo 🔄 Creating Python virtual environment...
if exist venv (
    echo ⚠️  Virtual environment already exists
) else (
    python -m venv venv
    echo ✅ Virtual environment created
)
echo.

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment activated
echo.

REM Upgrade pip
echo 🔄 Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install Python requirements
echo 🔄 Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install Python dependencies
    pause
    exit /b 1
)
echo ✅ Python dependencies installed
echo.

REM Check if .env exists
if not exist .env (
    echo 🔄 Creating .env file from template...
    copy .env.example .env
    echo ⚠️  IMPORTANT: Edit .env and add your GOOGLE_API_KEY
    echo    Get your free API key from: https://aistudio.google.com/app/apikey
    echo.
) else (
    echo ✅ .env file already exists
)
echo.

REM ========================================
REM Frontend Setup
REM ========================================
echo ========================================
echo Setting up Frontend (React/Vite)
echo ========================================
echo.

echo 🔄 Installing Node.js dependencies...
cd frontend
call npm install
if errorlevel 1 (
    echo ❌ Failed to install Node.js dependencies
    cd ..
    pause
    exit /b 1
)
echo ✅ Node.js dependencies installed
cd ..
echo.

echo ========================================
echo ✅ Setup Complete!
echo ========================================
echo.
echo 📝 Next steps:
echo.
echo 1. Edit .env and add your Google Gemini API Key:
echo    GOOGLE_API_KEY=your-api-key-here
echo.
echo 2. Start the application:
echo    - Easy way: Run start.bat
echo    - Manual way:
echo      Terminal 1: venv\Scripts\activate ^&^& python flask_app.py
echo      Terminal 2: cd frontend ^&^& npm run dev
echo.
echo 3. Open http://localhost:5173 in your browser
echo.
echo 📚 For more help, see README.md
echo.
pause
