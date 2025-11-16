# Run tests with pytest
# Tests secure deployment configuration, encryption, IAM/RBAC, and audit logging

Write-Host "Running test suite for Secure Financial RAG Deployment..." -ForegroundColor Green
Write-Host ""

# Set Python path to include src directory
$env:PYTHONPATH = $PWD

# Check if virtual environment exists
if (-Not (Test-Path "venv")) {
    Write-Host "⚠️  Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
    Write-Host ""
    Write-Host "Activating virtual environment..." -ForegroundColor Cyan
    & "venv\Scripts\Activate.ps1"
    Write-Host ""
    Write-Host "Installing dependencies..." -ForegroundColor Cyan
    pip install -r requirements.txt
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "Activating virtual environment..." -ForegroundColor Cyan
    & "venv\Scripts\Activate.ps1"
    Write-Host ""
}

# Run pytest with coverage
Write-Host "Running pytest with coverage..." -ForegroundColor Cyan
Write-Host ""

pytest -v tests/ --cov=src --cov-report=term-missing --cov-report=html

# Check test results
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ All tests passed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Coverage report generated in htmlcov/index.html" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "❌ Some tests failed. Check output above for details." -ForegroundColor Red
    exit 1
}
