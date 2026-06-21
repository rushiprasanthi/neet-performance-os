@echo off
REM Development startup script for Windows

echo 🚀 Starting NEET Platform Development Environment...

REM Backend setup
echo 📦 Setting up backend...
cd backend

if not exist "venv" (
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install --upgrade pip poetry
poetry install

REM Copy env file if not exists
if not exist ".env" (
    copy .env.example .env
    echo ✅ Created .env file - please update with your values
)

REM Run migrations
echo 🗄️  Running database migrations...
poetry run alembic upgrade head

REM Start backend in new window
echo 🚀 Starting FastAPI server...
start "NEET Backend" poetry run uvicorn app.main:app --reload --port 8000

cd ..

REM Frontend setup
echo 📦 Setting up frontend...
cd frontend

if not exist "node_modules" (
    call npm install
)

REM Copy env file if not exists
if not exist ".env" (
    copy .env.example .env
)

REM Start frontend in new window
echo 🚀 Starting Vite dev server...
start "NEET Frontend" npm run dev

cd ..

echo ✅ NEET Platform is starting!
echo    Backend: http://localhost:8000
echo    Frontend: http://localhost:5173
echo    API Docs: http://localhost:8000/docs
echo.
echo Close the console windows to stop services.

pause
