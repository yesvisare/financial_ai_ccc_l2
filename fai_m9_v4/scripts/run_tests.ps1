# Run tests with pytest
# L3 M9.4: Human-in-the-Loop for High-Stakes Decisions

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Running Test Suite" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set Python path to include current directory
$env:PYTHONPATH = $PWD

# Run pytest with verbose output
Write-Host "Running tests in tests/ directory..." -ForegroundColor Green
Write-Host ""

pytest tests/ -v --tb=short

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test run complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
