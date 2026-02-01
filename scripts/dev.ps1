# Air Mouse Development Script (Windows PowerShell)
# Starts both backend and frontend servers simultaneously

Write-Host "Starting Air Mouse Development Environment..." -ForegroundColor Cyan
Write-Host ""

# Path to virtual environment python
$VENV_PYTHON = "$PSScriptRoot\..\backend\.venv\Scripts\python.exe"

# Check if venv exists
if (-not (Test-Path $VENV_PYTHON)) {
    Write-Host "Virtual environment not found at: $VENV_PYTHON" -ForegroundColor Red
    Write-Host "Please run 'uv venv' inside backend folder first." -ForegroundColor Yellow
    exit 1
}

# Start Backend (Python FastAPI)
Write-Host "[1/2] Starting Backend Server (Python FastAPI)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\..\backend'; Write-Host 'Backend Server' -ForegroundColor Yellow; & '$VENV_PYTHON' main.py"

# Wait a moment for backend to initialize
Start-Sleep -Seconds 3

# Start Frontend (Vite React)
Write-Host "[2/2] Starting Frontend Server (Vite React)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\..\frontend'; Write-Host 'Frontend Server' -ForegroundColor Yellow; npm run dev"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Air Mouse Development Environment" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor Yellow
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor Yellow
Write-Host "  Health:   http://localhost:8000/health" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Press Ctrl+C in each window to stop" -ForegroundColor Gray
Write-Host ""
