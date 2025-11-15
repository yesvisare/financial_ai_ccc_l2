# PowerShell script to run tests
# L3 M8.2: Real-Time Financial Data Enrichment

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "L3 M8.2: Running Test Suite" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Set PYTHONPATH
$env:PYTHONPATH = $PWD

Write-Host "Running pytest..." -ForegroundColor Green
Write-Host ""

# Run pytest with verbose output
pytest tests/ -v --tb=short

# Check exit code
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "======================================" -ForegroundColor Green
    Write-Host "All tests passed successfully!" -ForegroundColor Green
    Write-Host "======================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "======================================" -ForegroundColor Red
    Write-Host "Some tests failed. Please review above." -ForegroundColor Red
    Write-Host "======================================" -ForegroundColor Red
    exit $LASTEXITCODE
}
