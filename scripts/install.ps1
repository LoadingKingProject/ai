# Air Mouse Installation Script (Windows PowerShell)
# Installs all dependencies for backend and frontend

Write-Host "Installing Air Mouse Dependencies..." -ForegroundColor Cyan
Write-Host ""

$PYTHON = "$env:USERPROFILE\.local\bin\python3.14.exe"
$PROJECT_ROOT = Split-Path -Parent $PSScriptRoot

# Install Backend Dependencies
Write-Host "[1/2] Installing Backend Dependencies (Python)..." -ForegroundColor Green
Set-Location "$PROJECT_ROOT\backend"

if (Test-Path $PYTHON) {
    & $PYTHON -m pip install -r requirements.txt
} else {
    Write-Host "Using uv to install..." -ForegroundColor Yellow
    uv pip install -r requirements.txt
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "Backend dependencies installed successfully!" -ForegroundColor Green
} else {
    Write-Host "Backend installation failed!" -ForegroundColor Red
}

Write-Host ""

# Install Frontend Dependencies
Write-Host "[2/2] Installing Frontend Dependencies (npm)..." -ForegroundColor Green
Set-Location "$PROJECT_ROOT\frontend"
npm install

if ($LASTEXITCODE -eq 0) {
    Write-Host "Frontend dependencies installed successfully!" -ForegroundColor Green
} else {
    Write-Host "Frontend installation failed!" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Installation Complete!" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Run: .\scripts\dev.ps1 to start" -ForegroundColor Yellow
Write-Host ""

Set-Location $PROJECT_ROOT
