# Script simplificado para rodar o backend localmente
Write-Host "=== SafeOutdoor Backend Local ===" -ForegroundColor Green

Set-Location backend

# Ativar venv
.\venv\Scripts\Activate.ps1

# Rodar o servidor
Write-Host "Backend rodando em http://localhost:8000" -ForegroundColor Cyan
Write-Host "Pressione Ctrl+C para parar" -ForegroundColor Yellow
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
