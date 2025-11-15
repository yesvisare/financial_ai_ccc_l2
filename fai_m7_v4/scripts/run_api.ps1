# Start API server with environment setup
# L3 M7.4: Audit Trail & Document Provenance

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "L3 M7.4: Audit Trail API Server" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Set environment variables
$env:PYTHONPATH = $PWD
$env:LOG_LEVEL = "INFO"

# Database configuration (PostgreSQL only - no external APIs)
Write-Host "Database Configuration:" -ForegroundColor Green
Write-Host "  - PostgreSQL database (local or managed)" -ForegroundColor White
Write-Host "  - No external API services required" -ForegroundColor White
Write-Host ""

# Check if .env file exists
if (Test-Path ".env") {
    Write-Host "✅ .env file found - loading configuration" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env file not found - using defaults" -ForegroundColor Yellow
    Write-Host "   Create .env from .env.example for custom config" -ForegroundColor Yellow
    Write-Host ""
}

# Start the API server
Write-Host "Starting FastAPI server..." -ForegroundColor Green
Write-Host "API will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API docs available at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

uvicorn app:app --reload --host 0.0.0.0 --port 8000
