# Run tests for L3 M10.2: Monitoring Financial RAG Performance
# Windows PowerShell script

Write-Host "Running Financial RAG Monitoring Tests..." -ForegroundColor Green

# Set Python path to include project root
$env:PYTHONPATH = $PWD

Write-Host "Environment configured:" -ForegroundColor Yellow
Write-Host "  - PYTHONPATH: $env:PYTHONPATH"
Write-Host ""

Write-Host "Running pytest with verbose output..." -ForegroundColor Cyan
Write-Host ""

# Run pytest with verbose output
pytest tests/test_m10_financial_rag_in_production.py -v --tb=short

Write-Host ""
Write-Host "Test run completed!" -ForegroundColor Green
Write-Host ""
Write-Host "To run with coverage:" -ForegroundColor Yellow
Write-Host "  pytest --cov=src tests/ --cov-report=html"
Write-Host ""
Write-Host "To run specific test:" -ForegroundColor Yellow
Write-Host "  pytest tests/test_m10_financial_rag_in_production.py::TestFinancialRAGMonitor::test_mnpi_detection -v"
