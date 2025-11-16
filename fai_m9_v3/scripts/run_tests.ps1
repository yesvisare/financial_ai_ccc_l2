# PowerShell script to run tests for L3 M9.3

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "L3 M9.3: Running Test Suite" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set PYTHONPATH to include current directory
$env:PYTHONPATH = $PWD

Write-Host "Running pytest..." -ForegroundColor Green
Write-Host ""

# Run tests with verbose output
pytest -v tests/

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test run complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To run with coverage report:" -ForegroundColor Yellow
Write-Host "  pytest --cov=src --cov-report=html tests/" -ForegroundColor Gray
Write-Host ""
Write-Host "To run specific test file:" -ForegroundColor Yellow
Write-Host "  pytest tests/test_m9_financial_compliance_risk.py -v" -ForegroundColor Gray
