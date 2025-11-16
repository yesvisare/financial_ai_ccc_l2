# Run tests with pytest

Write-Host "Running L3 M9.1: Explainability & Citation Tracking Tests..." -ForegroundColor Green
Write-Host ""

# Set Python path
$env:PYTHONPATH = $PWD

# Run pytest with verbose output
Write-Host "Executing pytest..." -ForegroundColor Cyan
pytest tests/ -v --tb=short

# Check exit code
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "All tests passed!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Some tests failed. See output above for details." -ForegroundColor Red
    exit $LASTEXITCODE
}
