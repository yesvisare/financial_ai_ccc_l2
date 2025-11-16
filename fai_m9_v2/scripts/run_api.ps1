# ============================================================================
# Start FastAPI server for L3 M9.2: Financial Compliance Risk
# ============================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "L3 M9.2: Financial Compliance Risk API" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set Python path to include src directory
$env:PYTHONPATH = $PWD

# Optional: Enable semantic analysis (uncomment to enable)
# $env:SEMANTIC_ANALYSIS_ENABLED = "true"
# $env:LLM_PROVIDER = "openai"  # or "anthropic"

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  - PYTHONPATH: $env:PYTHONPATH" -ForegroundColor Gray
Write-Host "  - Semantic Analysis: $($env:SEMANTIC_ANALYSIS_ENABLED ?? 'false')" -ForegroundColor Gray
Write-Host ""

Write-Host "Starting API server..." -ForegroundColor Green
Write-Host "  - URL: http://localhost:8000" -ForegroundColor Gray
Write-Host "  - Docs: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host "  - ReDoc: http://localhost:8000/redoc" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start uvicorn server with auto-reload
uvicorn app:app --reload --host 0.0.0.0 --port 8000
