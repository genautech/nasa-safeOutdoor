# Script para iniciar o ngrok para o backend SafeOutdoor
# Expõe o servidor FastAPI (porta 8000) para a internet

Write-Host "=== SafeOutdoor - Ngrok Setup ===" -ForegroundColor Cyan
Write-Host ""

# Verificar se o ngrok está autenticado
$ngrokConfig = "$env:USERPROFILE\.ngrok2\ngrok.yml"
if (-not (Test-Path $ngrokConfig)) {
    Write-Host "⚠️  Ngrok não está configurado!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Para configurar o ngrok:" -ForegroundColor White
    Write-Host "1. Acesse: https://dashboard.ngrok.com/signup" -ForegroundColor White
    Write-Host "2. Crie uma conta gratuita" -ForegroundColor White
    Write-Host "3. Copie seu authtoken de: https://dashboard.ngrok.com/get-started/your-authtoken" -ForegroundColor White
    Write-Host "4. Execute: ngrok config add-authtoken SEU_TOKEN_AQUI" -ForegroundColor White
    Write-Host ""
    
    $response = Read-Host "Você já tem um authtoken? (s/n)"
    if ($response -eq "s") {
        $token = Read-Host "Cole seu authtoken"
        ngrok config add-authtoken $token
        Write-Host "✅ Authtoken configurado!" -ForegroundColor Green
        Write-Host ""
    } else {
        Write-Host ""
        Write-Host "Por favor, configure o authtoken e execute este script novamente." -ForegroundColor Yellow
        exit
    }
}

Write-Host "🚀 Iniciando ngrok para o backend (porta 8000)..." -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANTE:" -ForegroundColor Yellow
Write-Host "1. Certifique-se de que o backend está rodando em http://localhost:8000" -ForegroundColor White
Write-Host "2. A URL pública será exibida abaixo" -ForegroundColor White
Write-Host "3. Use a URL HTTPS para testar seu backend remotamente" -ForegroundColor White
Write-Host "4. Pressione Ctrl+C para parar o túnel" -ForegroundColor White
Write-Host ""

# Iniciar ngrok
ngrok http 8000 --log=stdout
