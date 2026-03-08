@echo off
REM Setup script for GenAI Data Intelligence Dashboard
REM Run this script to set up the application environment

echo.
echo ================================
echo GenAI Data Intelligence Dashboard
echo Setup Script
echo ================================
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

REM Create virtual environment
echo 🔄 Creating virtual environment...
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

REM Install requirements
echo 🔄 Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed
echo.

REM Check if .env exists
if not exist .env (
    echo 🔄 Creating .env file from template...
    copy .env.example .env
    echo ⚠️  Please edit .env and add your OPENAI_API_KEY
    echo.
) else (
    echo ✅ .env file already exists
)
echo.

REM Generate sample data
echo 🔄 Generating sample CSV files...
python generate_sample_data.py
echo.

echo ================================
echo ✅ Setup Complete!
echo ================================
echo.
echo 📝 Next steps:
echo 1. Edit .env and add your OpenAI API Key
echo 2. Run: streamlit run app.py
echo.
echo 📚 For help, see README.md or QUICKSTART.md
echo.
pause
