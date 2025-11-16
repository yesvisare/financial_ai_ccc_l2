# Run tests with pytest
# L3_M10.3: Managing Financial Knowledge Base Drift

Write-Host "Running tests for L3_M10.3..." -ForegroundColor Green

# Set PYTHONPATH to include project root
$env:PYTHONPATH = $PWD

# Run tests in offline mode (no API calls required)
$env:OPENAI_ENABLED = "False"
$env:PINECONE_ENABLED = "False"

Write-Host "Running pytest with coverage..." -ForegroundColor Cyan
Write-Host ""

# Run pytest with verbose output and coverage
pytest tests/ -v --cov=src --cov-report=term-missing

Write-Host ""
Write-Host "Test run complete!" -ForegroundColor Green
