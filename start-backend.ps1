# Script para rodar o backend Python localmente
Write-Host "Iniciando SafeOutdoor Backend..." -ForegroundColor Green

# Navegar para o diretorio do backend
Set-Location backend

# Verificar se o venv existe
if (-Not (Test-Path "venv")) {
    Write-Host "Ambiente virtual nao encontrado!" -ForegroundColor Red
    Write-Host "Execute primeiro: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Ativar o ambiente virtual
Write-Host "Ativando ambiente virtual..." -ForegroundColor Cyan
& "venv\Scripts\Activate.ps1"

# Verificar se o .env existe
if (-Not (Test-Path ".env")) {
    Write-Host "Arquivo .env nao encontrado!" -ForegroundColor Red
    exit 1
}

# Instalar dependencias
Write-Host "Verificando dependencias..." -ForegroundColor Cyan
pip install -q -r requirements.txt

# Iniciar o servidor
Write-Host "Iniciando servidor FastAPI na porta 8000..." -ForegroundColor Green
Write-Host "API disponivel em: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Documentacao: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para parar o servidor, pressione Ctrl+C" -ForegroundColor Yellow
Write-Host ""

# Rodar o servidor
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload