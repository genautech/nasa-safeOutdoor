# Script para rodar o backend - Execute do diretorio raiz do projeto
Write-Host "=== SafeOutdoor Backend ===" -ForegroundColor Green

# Ir para o diretorio backend
Push-Location backend

try {
    # Ativar ambiente virtual
    Write-Host "Ativando ambiente virtual..." -ForegroundColor Cyan
    & .\venv\Scripts\Activate.ps1
    
    # Instalar dependencias
    Write-Host "Instalando dependencias..." -ForegroundColor Cyan
    pip install --quiet fastapi uvicorn httpx pydantic pydantic-settings python-dotenv openai xarray netCDF4 dask numpy h5py
    
    # Rodar servidor
    Write-Host ""
    Write-Host "Backend disponivel em: http://localhost:8000" -ForegroundColor Green
    Write-Host "Documentacao: http://localhost:8000/docs" -ForegroundColor Green
    Write-Host ""
    Write-Host "Pressione Ctrl+C para parar" -ForegroundColor Yellow
    Write-Host ""
    
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
}
finally {
    Pop-Location
}
