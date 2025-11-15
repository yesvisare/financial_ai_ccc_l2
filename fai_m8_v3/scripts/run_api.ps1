# PowerShell script to start the Financial Entity Recognition & Linking API
# Windows-compatible script for L3 M8.3

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Financial Entity Recognition & Linking API" -ForegroundColor Cyan
Write-Host "  L3 M8.3: FinBERT + SEC EDGAR + Wikipedia" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Set PYTHONPATH to include the project root
$env:PYTHONPATH = $PWD

# Load environment variables from .env (optional)
if (Test-Path ".env") {
    Write-Host "[INFO] Loading environment from .env file..." -ForegroundColor Yellow
    Get-Content .env | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            Set-Item -Path "env:$key" -Value $value
        }
    }
} else {
    Write-Host "[WARN] No .env file found. Using default configuration." -ForegroundColor Yellow
}

# Optional: Set environment variables for offline mode (default)
# Uncomment to enable Redis/PostgreSQL caching
# $env:REDIS_ENABLED = "True"
# $env:POSTGRES_ENABLED = "True"

# Optional: Enable metadata enrichment (enabled by default)
$env:ENABLE_METADATA_ENRICHMENT = "True"
$env:YFINANCE_ENABLED = "True"

# Set logging level
$env:LOG_LEVEL = "INFO"

Write-Host "[INFO] Starting FastAPI server on http://localhost:8000" -ForegroundColor Green
Write-Host "[INFO] API Documentation: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "[INFO] Press Ctrl+C to stop the server" -ForegroundColor Green
Write-Host ""

# Start the API server with uvicorn
try {
    uvicorn app:app --reload --host 0.0.0.0 --port 8000
} catch {
    Write-Host "[ERROR] Failed to start API server: $_" -ForegroundColor Red
    Write-Host "[INFO] Make sure uvicorn is installed: pip install uvicorn" -ForegroundColor Yellow
    exit 1
}
