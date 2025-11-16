# Start FastAPI server for L3 M10.2: Monitoring Financial RAG Performance
# Windows PowerShell script

Write-Host "Starting Financial RAG Monitoring API..." -ForegroundColor Green

# Set Python path to include project root
$env:PYTHONPATH = $PWD

# Optional: Enable monitoring services (all disabled by default for local dev)
# Uncomment to enable:
# $env:PROMETHEUS_ENABLED = "True"
# $env:PAGERDUTY_ENABLED = "True"
# $env:AWS_S3_ENABLED = "True"

# Set log level
$env:LOG_LEVEL = "INFO"

Write-Host "Environment configured:" -ForegroundColor Yellow
Write-Host "  - PYTHONPATH: $env:PYTHONPATH"
Write-Host "  - LOG_LEVEL: INFO"
Write-Host "  - Prometheus: Disabled (local mode)"
Write-Host "  - PagerDuty: Disabled (local mode)"
Write-Host "  - AWS S3: Disabled (local mode)"
Write-Host ""

Write-Host "Starting uvicorn server on http://localhost:8000" -ForegroundColor Cyan
Write-Host "API docs available at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

# Start uvicorn with hot reload
uvicorn app:app --reload --host 0.0.0.0 --port 8000
