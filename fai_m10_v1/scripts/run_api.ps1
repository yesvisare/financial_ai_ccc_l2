# Start API server with environment setup
# SERVICE: OPENAI (auto-detected from script Section 4)

Write-Host "Starting Secure Financial RAG Deployment API..." -ForegroundColor Green

# Set Python path to include src directory
$env:PYTHONPATH = $PWD

# Enable OPENAI service (change to "False" if you don't have an API key yet)
$env:OPENAI_ENABLED = "True"

# Check if .env file exists
if (-Not (Test-Path ".env")) {
    Write-Host "⚠️  .env file not found. Creating from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Created .env file" -ForegroundColor Green
    Write-Host ""
    Write-Host "📝 IMPORTANT: Please edit .env file with your configuration:" -ForegroundColor Cyan
    Write-Host "   1. Set OPENAI_API_KEY (if using OpenAI)"
    Write-Host "   2. Set PINECONE_API_KEY (if using Pinecone)"
    Write-Host "   3. Set AWS_KMS_KEY_ID (for encryption)"
    Write-Host "   4. Configure other AWS settings"
    Write-Host ""
    Write-Host "Press any key to continue (API will start without external services)..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Check if virtual environment exists
if (-Not (Test-Path "venv")) {
    Write-Host "⚠️  Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
    Write-Host ""
    Write-Host "Activating virtual environment..." -ForegroundColor Cyan
    & "venv\Scripts\Activate.ps1"
    Write-Host ""
    Write-Host "Installing dependencies..." -ForegroundColor Cyan
    pip install -r requirements.txt
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "Activating virtual environment..." -ForegroundColor Cyan
    & "venv\Scripts\Activate.ps1"
}

Write-Host ""
Write-Host "Starting FastAPI server..." -ForegroundColor Cyan
Write-Host "  URL: http://localhost:8000" -ForegroundColor White
Write-Host "  Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  ReDoc: http://localhost:8000/redoc" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the API server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
