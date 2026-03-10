#!/bin/bash

# Setup script for DataLens AI - GenAI Data Intelligence Dashboard
# Run with: bash setup.sh or chmod +x setup.sh && ./setup.sh

echo ""
echo "========================================"
echo "DataLens AI - GenAI Data Intelligence"
echo "Setup Script (Flask + React)"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org"
    exit 1
fi

echo "✅ Python found"
python3 --version
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    echo "Please install Node.js 16+ from https://nodejs.org"
    exit 1
fi

echo "✅ Node.js found"
node --version
npm --version
echo ""

# ========================================
# Backend Setup
# ========================================
echo "========================================"
echo "Setting up Backend (Python/Flask)"
echo "========================================"
echo ""

# Create virtual environment
echo "🔄 Creating Python virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists"
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "🔄 Upgrading pip..."
python -m pip install --upgrade pip
echo ""

# Install Python requirements
echo "🔄 Installing Python dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install Python dependencies"
    exit 1
fi
echo "✅ Python dependencies installed"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "🔄 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  IMPORTANT: Edit .env and add your GOOGLE_API_KEY"
    echo "   Get your free API key from: https://aistudio.google.com/app/apikey"
    echo ""
else
    echo "✅ .env file already exists"
fi
echo ""

# ========================================
# Frontend Setup
# ========================================
echo "========================================"
echo "Setting up Frontend (React/Vite)"
echo "========================================"
echo ""

echo "🔄 Installing Node.js dependencies..."
cd frontend
npm install
if [ $? -ne 0 ]; then
    echo "❌ Failed to install Node.js dependencies"
    cd ..
    exit 1
fi
echo "✅ Node.js dependencies installed"
cd ..
echo ""

echo "========================================"
echo "✅ Setup Complete!"
echo "========================================"
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Edit .env and add your Google Gemini API Key:"
echo "   GOOGLE_API_KEY=your-api-key-here"
echo ""
echo "2. Start the application:"
echo "   - Easy way: ./start.sh"
echo "   - Manual way:"
echo "     Terminal 1: source venv/bin/activate && python flask_app.py"
echo "     Terminal 2: cd frontend && npm run dev"
echo ""
echo "3. Open http://localhost:5173 in your browser"
echo ""
echo "📚 For more help, see README.md"
echo ""
