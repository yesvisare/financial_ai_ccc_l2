# Start API server with environment setup
# M7.2: PII Detection & Financial Data Redaction
# Service: Presidio (Self-Hosted)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "M7.2: PII Detection & Redaction API" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set environment variables
$env:PYTHONPATH = $PWD
$env:PRESIDIO_ENABLED = "True"
$env:SPACY_MODEL = "en_core_web_lg"
$env:LOG_LEVEL = "INFO"

Write-Host "Environment Configuration:" -ForegroundColor Yellow
Write-Host "  PRESIDIO_ENABLED: $env:PRESIDIO_ENABLED" -ForegroundColor Green
Write-Host "  SPACY_MODEL: $env:SPACY_MODEL" -ForegroundColor Green
Write-Host "  LOG_LEVEL: $env:LOG_LEVEL" -ForegroundColor Green
Write-Host ""

# Check if Presidio is installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
python -c "import presidio_analyzer; import presidio_anonymizer; import spacy" 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Presidio or spaCy not installed!" -ForegroundColor Red
    Write-Host "Install with:" -ForegroundColor Yellow
    Write-Host "  pip install -r requirements.txt" -ForegroundColor Cyan
    Write-Host "  python -m spacy download en_core_web_lg" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "API will start in OFFLINE mode (mock responses only)" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "✓ Dependencies found" -ForegroundColor Green
    Write-Host ""
}

Write-Host "Starting FastAPI server..." -ForegroundColor Yellow
Write-Host "API will be available at: http://localhost:8000" -ForegroundColor Green
Write-Host "Interactive docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start uvicorn server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
