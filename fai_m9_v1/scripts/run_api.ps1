# Start API server with environment setup
# Service auto-detected: ANTHROPIC (primary), OPENAI (embeddings), PINECONE (vector DB)

Write-Host "Starting L3 M9.1: Explainability & Citation Tracking API..." -ForegroundColor Green

# Set Python path
$env:PYTHONPATH = $PWD

# Optional: Enable services (uncomment and set to "True" when configured)
# $env:ANTHROPIC_ENABLED = "True"
# $env:OPENAI_ENABLED = "True"
# $env:PINECONE_ENABLED = "True"

Write-Host "Service Configuration:" -ForegroundColor Cyan
Write-Host "  ANTHROPIC: $($env:ANTHROPIC_ENABLED ?? 'False (disabled)')" -ForegroundColor Yellow
Write-Host "  OPENAI:    $($env:OPENAI_ENABLED ?? 'False (disabled)')" -ForegroundColor Yellow
Write-Host "  PINECONE:  $($env:PINECONE_ENABLED ?? 'False (disabled)')" -ForegroundColor Yellow
Write-Host ""
Write-Host "API will run in OFFLINE mode if no services are enabled" -ForegroundColor Yellow
Write-Host "To enable services, configure API keys in .env file" -ForegroundColor Yellow
Write-Host ""

# Start FastAPI server
Write-Host "Starting uvicorn server on http://localhost:8000..." -ForegroundColor Green
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

uvicorn app:app --reload --host 0.0.0.0 --port 8000
