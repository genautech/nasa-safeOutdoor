# Script de teste rápido do Ngrok

Write-Host "=== Teste de Configuração do Ngrok ===" -ForegroundColor Cyan
Write-Host ""

# Verificar instalação
Write-Host "1. Verificando instalação..." -ForegroundColor Yellow
$ngrokPath = Get-Command ngrok -ErrorAction SilentlyContinue
if ($ngrokPath) {
    Write-Host "   ✅ Ngrok instalado: $($ngrokPath.Source)" -ForegroundColor Green
    $version = ngrok version
    Write-Host "   ✅ Versão: $version" -ForegroundColor Green
} else {
    Write-Host "   ❌ Ngrok não encontrado no PATH" -ForegroundColor Red
    exit
}

Write-Host ""

# Verificar configuração
Write-Host "2. Verificando configuração..." -ForegroundColor Yellow
$ngrokConfig = "$env:USERPROFILE\.ngrok2\ngrok.yml"
if (Test-Path $ngrokConfig) {
    Write-Host "   ✅ Arquivo de configuração encontrado" -ForegroundColor Green
    
    $configContent = Get-Content $ngrokConfig -Raw
    if ($configContent -match "authtoken") {
        Write-Host "   ✅ Authtoken configurado" -ForegroundColor Green
        Write-Host ""
        Write-Host "🎉 Ngrok está pronto para uso!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Para iniciar o ngrok com o backend SafeOutdoor:" -ForegroundColor White
        Write-Host "   .\start-ngrok.ps1" -ForegroundColor Cyan
    } else {
        Write-Host "   ⚠️  Authtoken não encontrado no arquivo de configuração" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Configure o authtoken:" -ForegroundColor White
        Write-Host "   ngrok config add-authtoken SEU_TOKEN" -ForegroundColor Cyan
    }
} else {
    Write-Host "   ⚠️  Arquivo de configuração não encontrado" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Próximos passos:" -ForegroundColor White
    Write-Host "1. Crie uma conta em: https://dashboard.ngrok.com/signup" -ForegroundColor Cyan
    Write-Host "2. Obtenha seu authtoken em: https://dashboard.ngrok.com/get-started/your-authtoken" -ForegroundColor Cyan
    Write-Host "3. Configure: ngrok config add-authtoken SEU_TOKEN" -ForegroundColor Cyan
}

Write-Host ""

# Verificar backend
Write-Host "3. Verificando backend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "   ✅ Backend rodando em http://localhost:8000" -ForegroundColor Green
    Write-Host "   💡 Pronto para expor com ngrok!" -ForegroundColor Cyan
} catch {
    Write-Host "   ⚠️  Backend não está rodando" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Para iniciar o backend:" -ForegroundColor White
    Write-Host "   cd backend" -ForegroundColor Cyan
    Write-Host "   .\venv\Scripts\activate" -ForegroundColor Cyan
    Write-Host "   uvicorn app.main:app --reload" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Leia NGROK_SETUP.md para mais informações!" -ForegroundColor White
