# Start API server with environment setup
# SERVICE: PINECONE (vector database) + SENTENCE_TRANSFORMERS (local embeddings)

Write-Host "Starting L3 M8.1 Financial Domain Knowledge API..." -ForegroundColor Green

# Set Python path
$env:PYTHONPATH = $PWD

# Enable Pinecone (optional - set to "False" for offline mode)
# $env:PINECONE_ENABLED = "True"

Write-Host "Environment configured:" -ForegroundColor Cyan
Write-Host "  PYTHONPATH: $env:PYTHONPATH" -ForegroundColor Gray
Write-Host "  PINECONE_ENABLED: $env:PINECONE_ENABLED" -ForegroundColor Gray

Write-Host "`nStarting uvicorn server on http://localhost:8000..." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow

uvicorn app:app --reload --host 0.0.0.0 --port 8000
