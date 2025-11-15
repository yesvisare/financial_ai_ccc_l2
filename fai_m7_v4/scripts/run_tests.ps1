# Run tests with pytest
# L3 M7.4: Audit Trail & Document Provenance

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "L3 M7.4: Running Test Suite" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Set environment variables
$env:PYTHONPATH = $PWD
$env:DATABASE_URL = "sqlite:///:memory:"  # Use in-memory SQLite for tests

Write-Host "Test Configuration:" -ForegroundColor Green
Write-Host "  - Using in-memory SQLite database" -ForegroundColor White
Write-Host "  - No external services required" -ForegroundColor White
Write-Host ""

# Run pytest with verbose output
Write-Host "Running tests..." -ForegroundColor Green
Write-Host ""

pytest -v tests/

# Check exit code
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ All tests passed!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ Some tests failed - see output above" -ForegroundColor Red
    exit $LASTEXITCODE
}
