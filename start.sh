#!/bin/bash

# Reddit Lead Generation Platform - Quick Start Script

echo "🚀 Starting Reddit Lead Generation Platform..."

# Check if running from correct directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo "
🛑 Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup EXIT INT TERM

# Start backend
echo "📦 Starting backend API on port 8000..."
cd backend
uvicorn main:app --reload --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Backend failed to start. Check backend/backend.log for errors."
    exit 1
fi

echo "✅ Backend API is running"

# Start frontend
echo "🎨 Starting frontend on port 3000..."
cd frontend
npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
sleep 5

echo "
✨ Reddit Lead Generation Platform is running!

📍 Access Points:
   - Frontend UI: http://localhost:3000
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

📖 Quick Guide:
   1. Go to http://localhost:3000
   2. Click 'Platforms' to add subreddits
   3. Click 'Users' to view leads

Press Ctrl+C to stop all services.
"

# Keep script running
wait