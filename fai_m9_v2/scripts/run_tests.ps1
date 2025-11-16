# ============================================================================
# Run test suite for L3 M9.2: Financial Compliance Risk
# ============================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "L3 M9.2: Financial Compliance Risk Tests" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set Python path to include src directory
$env:PYTHONPATH = $PWD

# Force offline mode for tests (no external API calls)
$env:OFFLINE = "true"
$env:SEMANTIC_ANALYSIS_ENABLED = "false"

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  - PYTHONPATH: $env:PYTHONPATH" -ForegroundColor Gray
Write-Host "  - OFFLINE: $env:OFFLINE" -ForegroundColor Gray
Write-Host "  - SEMANTIC_ANALYSIS_ENABLED: $env:SEMANTIC_ANALYSIS_ENABLED" -ForegroundColor Gray
Write-Host ""

Write-Host "Running pytest..." -ForegroundColor Green
Write-Host ""

# Run pytest with verbose output
pytest tests/ -v --tb=short

# Check exit code
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✓ All tests passed!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "✗ Some tests failed. See output above." -ForegroundColor Red
    exit $LASTEXITCODE
}
