# Start API server with environment setup
# L3_M10.3: Managing Financial Knowledge Base Drift
# Services auto-detected from script Section 4: OPENAI (primary), PINECONE (secondary)

Write-Host "Starting L3_M10.3 Drift Detection API..." -ForegroundColor Green

# Set PYTHONPATH to include project root
$env:PYTHONPATH = $PWD

# Enable services (set to "True" if you have API keys configured)
# Default: False for offline demo mode
$env:OPENAI_ENABLED = "False"
$env:PINECONE_ENABLED = "False"

# Optional: Set API keys if you want to enable services
# Uncomment and fill in your keys:
# $env:OPENAI_API_KEY = "your_openai_api_key_here"
# $env:PINECONE_API_KEY = "your_pinecone_api_key_here"
# $env:PINECONE_ENVIRONMENT = "your_pinecone_environment_here"

# Application settings
$env:DRIFT_THRESHOLD = "0.85"
$env:RETRAINING_BATCH_SIZE = "50"
$env:LOG_LEVEL = "INFO"

Write-Host "Environment configured:" -ForegroundColor Cyan
Write-Host "  OPENAI_ENABLED: $env:OPENAI_ENABLED"
Write-Host "  PINECONE_ENABLED: $env:PINECONE_ENABLED"
Write-Host "  DRIFT_THRESHOLD: $env:DRIFT_THRESHOLD"
Write-Host "  LOG_LEVEL: $env:LOG_LEVEL"
Write-Host ""

# Start Uvicorn server
Write-Host "Starting uvicorn server at http://0.0.0.0:8000" -ForegroundColor Green
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

uvicorn app:app --reload --host 0.0.0.0 --port 8000
