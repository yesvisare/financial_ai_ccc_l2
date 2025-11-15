# Start API server with environment setup
# L3 M8.4: Temporal Financial Information Handling

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "L3 M8.4: Temporal Financial Info API" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set Python path to include current directory
$env:PYTHONPATH = $PWD

# Configure Pinecone (Primary Service)
# Set to "True" to enable Pinecone vector database
$env:PINECONE_ENABLED = "False"
# $env:PINECONE_API_KEY = "your_api_key_here"
# $env:PINECONE_ENVIRONMENT = "your_environment_here"
$env:PINECONE_INDEX_NAME = "financial-documents"

# Configure Anthropic (Secondary Service - Optional)
$env:ANTHROPIC_ENABLED = "False"
# $env:ANTHROPIC_API_KEY = "your_api_key_here"

# Configure Redis (Optional - Caching)
$env:REDIS_ENABLED = "False"
$env:REDIS_URL = "redis://localhost:6379"

# Logging
$env:LOG_LEVEL = "INFO"

Write-Host "Environment Configuration:" -ForegroundColor Yellow
Write-Host "  PINECONE_ENABLED:   $env:PINECONE_ENABLED" -ForegroundColor Gray
Write-Host "  ANTHROPIC_ENABLED:  $env:ANTHROPIC_ENABLED" -ForegroundColor Gray
Write-Host "  REDIS_ENABLED:      $env:REDIS_ENABLED" -ForegroundColor Gray
Write-Host ""

if ($env:PINECONE_ENABLED -eq "False") {
    Write-Host "⚠️  WARNING: Pinecone is disabled" -ForegroundColor Yellow
    Write-Host "   API will run in simulation mode" -ForegroundColor Yellow
    Write-Host "   To enable: Edit this script and set PINECONE_ENABLED=True" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Starting FastAPI server..." -ForegroundColor Green
Write-Host "API will be available at: http://localhost:8000" -ForegroundColor Green
Write-Host "API documentation at:     http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Start uvicorn server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
