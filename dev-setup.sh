#!/bin/bash
# Development startup script - local setup without Docker

set -e

echo "🚀 Starting NEET Platform Development Environment..."

# Backend setup
echo "📦 Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    python3.11 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip poetry
poetry install

# Copy env file if not exists
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Created .env file - please update with your values"
fi

# Run migrations
echo "🗄️  Running database migrations..."
poetry run alembic upgrade head

# Start backend in background
echo "🚀 Starting FastAPI server..."
poetry run uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

cd ..

# Frontend setup
echo "📦 Setting up frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    npm install
fi

# Copy env file if not exists
if [ ! -f ".env" ]; then
    cp .env.example .env
fi

# Start frontend
echo "🚀 Starting Vite dev server..."
npm run dev &
FRONTEND_PID=$!

cd ..

echo "✅ NEET Platform is running!"
echo "   Backend: http://localhost:8000"
echo "   Frontend: http://localhost:5173"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services..."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

wait $BACKEND_PID $FRONTEND_PID
