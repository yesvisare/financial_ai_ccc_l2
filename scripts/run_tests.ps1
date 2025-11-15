# PowerShell script to run pytest tests
# L3 M7.1: Financial Document Types & Regulatory Context

Write-Host "Running L3 M7.1 Financial Compliance Controls Tests..." -ForegroundColor Green

# Set Python path to include src directory
$env:PYTHONPATH = $PWD

# Run pytest with verbose output
Write-Host "Executing pytest..." -ForegroundColor Cyan

pytest -v tests/

# Check exit code
if ($LASTEXITCODE -eq 0) {
    Write-Host "`nAll tests passed!" -ForegroundColor Green
} else {
    Write-Host "`nSome tests failed. Review output above." -ForegroundColor Red
    exit $LASTEXITCODE
}
