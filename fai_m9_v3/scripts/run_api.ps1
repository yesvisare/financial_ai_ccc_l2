# PowerShell script to start the FastAPI server for L3 M9.3
# SERVICE auto-detected from script Section 4: ANTHROPIC

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "L3 M9.3: Regulatory Constraints API" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set PYTHONPATH to include current directory
$env:PYTHONPATH = $PWD

# Optional: Enable ANTHROPIC service for M9.1 integration
# Uncomment and set API key to enable:
# $env:ANTHROPIC_ENABLED = "True"
# $env:ANTHROPIC_API_KEY = "your_anthropic_api_key_here"

Write-Host "Service Configuration:" -ForegroundColor Yellow
Write-Host "  ANTHROPIC: $env:ANTHROPIC_ENABLED (Optional - for M9.1 integration)" -ForegroundColor Gray
Write-Host ""

Write-Host "Starting FastAPI server..." -ForegroundColor Green
Write-Host "API will be available at: http://localhost:8000" -ForegroundColor Green
Write-Host "API docs available at: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start uvicorn server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
