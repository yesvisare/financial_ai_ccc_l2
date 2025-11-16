# Start API server with environment setup
# L3 M9.4: Human-in-the-Loop for High-Stakes Decisions

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting HITL Workflow API Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set Python path to include current directory
$env:PYTHONPATH = $PWD

# Optional: Enable OpenAI integration (uncomment and set API key in .env)
# $env:OPENAI_ENABLED = "True"

# Start the FastAPI server
Write-Host "Starting server on http://localhost:8000" -ForegroundColor Green
Write-Host "API documentation: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""

uvicorn app:app --reload --host 0.0.0.0 --port 8000
