# Script simplificado para rodar o backend
Write-Host "=== SafeOutdoor Backend ===" -ForegroundColor Green

Set-Location backend

# Ativar venv
Write-Host "Ativando ambiente virtual..." -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1

# Rodar servidor direto (sem reinstalar dependencias)
Write-Host ""
Write-Host "Backend disponivel em: http://localhost:8000" -ForegroundColor Green
Write-Host "Documentacao: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Pressione Ctrl+C para parar" -ForegroundColor Yellow
Write-Host ""

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
