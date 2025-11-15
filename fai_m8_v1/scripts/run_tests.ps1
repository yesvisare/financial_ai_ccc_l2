# Run tests with pytest
# All tests run in offline mode (no external API calls)

Write-Host "Running L3 M8.1 Test Suite..." -ForegroundColor Green

# Set Python path
$env:PYTHONPATH = $PWD

# Force offline mode for tests
$env:PINECONE_ENABLED = "false"
$env:OFFLINE = "true"

Write-Host "Test environment configured:" -ForegroundColor Cyan
Write-Host "  PYTHONPATH: $env:PYTHONPATH" -ForegroundColor Gray
Write-Host "  OFFLINE: true" -ForegroundColor Gray

Write-Host "`nRunning pytest..." -ForegroundColor Cyan

pytest -v tests/

Write-Host "`nTest run complete!" -ForegroundColor Green
