# PowerShell script to start FastAPI server
# L3 M7.1: Financial Document Types & Regulatory Context

Write-Host "Starting L3 M7.1 Financial Compliance Controls API..." -ForegroundColor Green

# Set Python path to include src directory
$env:PYTHONPATH = $PWD

# Load environment variables from .env if it exists
if (Test-Path ".env") {
    Write-Host "Loading environment variables from .env" -ForegroundColor Yellow
    Get-Content .env | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($key, $value, "Process")
        }
    }
} else {
    Write-Host "No .env file found - using defaults" -ForegroundColor Yellow
    Write-Host "Copy .env.example to .env to configure" -ForegroundColor Yellow
}

# Check if EDGAR is enabled
if ($env:EDGAR_ENABLED -eq "true") {
    Write-Host "EDGAR service enabled" -ForegroundColor Green
} else {
    Write-Host "EDGAR service disabled - running in offline mode" -ForegroundColor Yellow
}

# Start uvicorn server
Write-Host "Starting server on http://0.0.0.0:8000" -ForegroundColor Cyan
Write-Host "API documentation available at http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor Cyan

uvicorn app:app --reload --host 0.0.0.0 --port 8000
