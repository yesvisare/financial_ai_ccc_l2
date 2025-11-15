# Run tests for L3 M7.3: Financial Document Parsing & Chunking
# Windows PowerShell script

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "L3 M7.3: Financial Document Parsing & Chunking Tests" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan

# Set PYTHONPATH to current directory
$env:PYTHONPATH = $PWD
Write-Host "PYTHONPATH set to: $env:PYTHONPATH" -ForegroundColor Yellow
Write-Host ""

# Run pytest with verbose output
Write-Host "Running tests..." -ForegroundColor Green
pytest -v tests/

# Check exit code
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Green
    Write-Host "All tests passed!" -ForegroundColor Green
    Write-Host "=" * 60 -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Red
    Write-Host "Some tests failed. Please review the output above." -ForegroundColor Red
    Write-Host "=" * 60 -ForegroundColor Red
}
