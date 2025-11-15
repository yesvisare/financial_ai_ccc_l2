# PowerShell script to run tests for Financial Entity Recognition & Linking
# Windows-compatible script for L3 M8.3

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Financial Entity Recognition & Linking - Test Suite" -ForegroundColor Cyan
Write-Host "  L3 M8.3: Running pytest tests" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Set PYTHONPATH to include the project root
$env:PYTHONPATH = $PWD

# Parse command line arguments
param(
    [switch]$Coverage,
    [switch]$Verbose,
    [string]$TestPath = "tests/"
)

# Build pytest command
$pytestArgs = @()

# Add test path
$pytestArgs += $TestPath

# Add verbose flag if requested
if ($Verbose) {
    $pytestArgs += "-v"
} else {
    $pytestArgs += "-q"
}

# Add coverage if requested
if ($Coverage) {
    Write-Host "[INFO] Running tests with coverage report..." -ForegroundColor Yellow
    $pytestArgs += "--cov=src"
    $pytestArgs += "--cov-report=term-missing"
    $pytestArgs += "--cov-report=html"
} else {
    Write-Host "[INFO] Running tests (use -Coverage flag for coverage report)..." -ForegroundColor Yellow
}

Write-Host ""

# Run pytest
try {
    pytest $pytestArgs
    $exitCode = $LASTEXITCODE

    Write-Host ""
    if ($exitCode -eq 0) {
        Write-Host "[SUCCESS] All tests passed!" -ForegroundColor Green
    } else {
        Write-Host "[FAILURE] Some tests failed. Exit code: $exitCode" -ForegroundColor Red
    }

    if ($Coverage) {
        Write-Host ""
        Write-Host "[INFO] Coverage report saved to htmlcov/index.html" -ForegroundColor Cyan
        Write-Host "[INFO] Open in browser: htmlcov/index.html" -ForegroundColor Cyan
    }

    exit $exitCode

} catch {
    Write-Host "[ERROR] Failed to run tests: $_" -ForegroundColor Red
    Write-Host "[INFO] Make sure pytest is installed: pip install pytest pytest-cov" -ForegroundColor Yellow
    exit 1
}
