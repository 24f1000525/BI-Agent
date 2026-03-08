#!/bin/bash

# Setup script for GenAI Data Intelligence Dashboard
# Run with: bash setup.sh

echo ""
echo "================================"
echo "GenAI Data Intelligence Dashboard"
echo "Setup Script"
echo "================================"
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

# Create virtual environment
echo "🔄 Creating virtual environment..."
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

# Install requirements
echo "🔄 Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo "✅ Dependencies installed"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "🔄 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your OPENAI_API_KEY"
    echo ""
else
    echo "✅ .env file already exists"
fi
echo ""

# Generate sample data
echo "🔄 Generating sample CSV files..."
python generate_sample_data.py
echo ""

echo "================================"
echo "✅ Setup Complete!"
echo "================================"
echo ""
echo "📝 Next steps:"
echo "1. Edit .env and add your OpenAI API Key"
echo "2. Run: streamlit run app.py"
echo ""
echo "📚 For help, see README.md or QUICKSTART.md"
echo ""
