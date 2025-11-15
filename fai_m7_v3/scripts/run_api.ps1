# Start FastAPI server for L3 M7.3: Financial Document Parsing & Chunking
# Windows PowerShell script

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "L3 M7.3: Financial Document Parsing & Chunking API" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Cyan

# Set PYTHONPATH to current directory
$env:PYTHONPATH = $PWD
Write-Host "PYTHONPATH set to: $env:PYTHONPATH" -ForegroundColor Yellow

# Optional: Enable EDGAR service (requires SEC User-Agent)
# Uncomment the lines below and set your company name and email
# $env:EDGAR_ENABLED = "True"
# $env:SEC_USER_AGENT = "YourCompany yourteam@company.com"

# Optional: Enable OpenAI and Pinecone (for vector database features)
# $env:OPENAI_ENABLED = "False"
# $env:PINECONE_ENABLED = "False"

Write-Host ""
Write-Host "Starting FastAPI server..." -ForegroundColor Green
Write-Host "API will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API docs available at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start uvicorn server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
