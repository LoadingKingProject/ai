#!/bin/bash
# Air Mouse Development Script (Unix/Linux/macOS)
# Starts both backend and frontend servers simultaneously

echo -e "\033[36mStarting Air Mouse Development Environment...\033[0m"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$SCRIPT_DIR/.."

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "\033[33mShutting down servers...\033[0m"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM

# Start Backend (Python FastAPI)
echo -e "\033[32m[1/2] Starting Backend Server (Python FastAPI)...\033[0m"
cd "$PROJECT_DIR/backend" && python main.py &
BACKEND_PID=$!

# Wait a moment for backend to initialize
sleep 2

# Start Frontend (Vite React)
echo -e "\033[32m[2/2] Starting Frontend Server (Vite React)...\033[0m"
cd "$PROJECT_DIR/frontend" && npm run dev &
FRONTEND_PID=$!

echo ""
echo -e "\033[36m========================================\033[0m"
echo -e "\033[37m  Air Mouse Development Environment\033[0m"
echo -e "\033[36m========================================\033[0m"
echo ""
echo -e "\033[33m  Backend:  http://localhost:8000\033[0m"
echo -e "\033[33m  Frontend: http://localhost:3000\033[0m"
echo -e "\033[33m  Health:   http://localhost:8000/health\033[0m"
echo ""
echo -e "\033[90m  Press Ctrl+C to stop both servers\033[0m"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
