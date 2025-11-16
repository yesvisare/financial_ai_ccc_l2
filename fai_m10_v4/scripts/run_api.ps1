# Start API server with environment setup
# L3 M10.4: Disaster Recovery & Business Continuity

Write-Host "Starting L3 M10.4: Disaster Recovery API Server..." -ForegroundColor Green

# Set PYTHONPATH to include project root
$env:PYTHONPATH = $PWD

# Load environment variables from .env file if it exists
if (Test-Path ".env") {
    Write-Host "Loading environment variables from .env..." -ForegroundColor Yellow
    Get-Content .env | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            Set-Item -Path "env:$name" -Value $value
        }
    }
} else {
    Write-Host "No .env file found. Using default configuration (services disabled)." -ForegroundColor Yellow
    Write-Host "Copy .env.example to .env and configure credentials to enable services." -ForegroundColor Yellow
}

# Enable services if credentials are configured
# Uncomment these lines and configure .env to enable
# $env:AWS_ENABLED = "true"
# $env:PINECONE_ENABLED = "true"
# $env:POSTGRESQL_ENABLED = "true"

Write-Host ""
Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  AWS Enabled:        $($env:AWS_ENABLED ?? 'false')" -ForegroundColor Cyan
Write-Host "  Pinecone Enabled:   $($env:PINECONE_ENABLED ?? 'false')" -ForegroundColor Cyan
Write-Host "  PostgreSQL Enabled: $($env:POSTGRESQL_ENABLED ?? 'false')" -ForegroundColor Cyan
Write-Host ""

Write-Host "Starting Uvicorn server on http://localhost:8000..." -ForegroundColor Green
Write-Host "API documentation will be available at http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""

# Start the server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
