# Run tests with pytest
# L3 M10.4: Disaster Recovery & Business Continuity

Write-Host "Running L3 M10.4: Disaster Recovery Test Suite..." -ForegroundColor Green

# Set PYTHONPATH to include project root
$env:PYTHONPATH = $PWD

Write-Host ""
Write-Host "Executing pytest..." -ForegroundColor Cyan
Write-Host ""

# Run pytest with verbose output
pytest -v tests/

# Check exit code
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ All tests passed!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ Some tests failed. Check output above." -ForegroundColor Red
    exit $LASTEXITCODE
}
