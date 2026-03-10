#!/bin/bash
echo "Starting DataLens AI (Flask + React)..."

# Start Flask backend
source venv/bin/activate
python flask_app.py &
FLASK_PID=$!
echo "Flask API started (PID $FLASK_PID): http://localhost:5000"

# Start React dev server
cd frontend && npm run dev &
REACT_PID=$!
echo "React App started (PID $REACT_PID): http://localhost:5173"

echo ""
echo "Press Ctrl+C to stop both servers"

wait
