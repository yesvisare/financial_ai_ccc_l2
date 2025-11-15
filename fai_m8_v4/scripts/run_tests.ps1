# Run tests with pytest
# L3 M8.4: Temporal Financial Information Handling

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "L3 M8.4: Running Test Suite" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set Python path to include current directory
$env:PYTHONPATH = $PWD

Write-Host "Running pytest..." -ForegroundColor Green
Write-Host ""

# Run pytest with verbose output
pytest tests/ -v --tb=short

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test run complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Optional: Run with coverage
Write-Host "To run with coverage report, use:" -ForegroundColor Yellow
Write-Host "  pytest tests/ --cov=src --cov-report=html" -ForegroundColor Gray
Write-Host ""
