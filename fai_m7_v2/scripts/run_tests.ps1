# Run test suite with pytest
# M7.2: PII Detection & Financial Data Redaction

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "M7.2: Running Test Suite" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set environment variables
$env:PYTHONPATH = $PWD
$env:PRESIDIO_ENABLED = "True"

Write-Host "Running pytest..." -ForegroundColor Yellow
Write-Host ""

# Run pytest with coverage
pytest tests/ -v --tb=short --color=yes

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✓ All tests passed!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "✗ Some tests failed" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    exit 1
}
