# PowerShell script to start the FastAPI server
# L3 M8.2: Real-Time Financial Data Enrichment

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "L3 M8.2: Financial Data Enrichment API" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Set environment variables (optional services - all can be disabled)
$env:PYTHONPATH = $PWD
$env:REDIS_ENABLED = "false"  # Set to "true" if Redis is available
$env:OPENAI_ENABLED = "false"  # Set to "true" if OpenAI key is configured
$env:PINECONE_ENABLED = "false"  # Set to "true" if Pinecone is configured

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  REDIS_ENABLED: $env:REDIS_ENABLED"
Write-Host "  OPENAI_ENABLED: $env:OPENAI_ENABLED"
Write-Host "  PINECONE_ENABLED: $env:PINECONE_ENABLED"
Write-Host ""

Write-Host "Starting API server..." -ForegroundColor Green
Write-Host "API will be available at: http://localhost:8000" -ForegroundColor Green
Write-Host "Documentation: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start uvicorn server
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
