# Script para parar o backend Python
Write-Host "🛑 Parando SafeOutdoor Backend..." -ForegroundColor Yellow

# Encontrar e matar processos Python rodando uvicorn
$processes = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*uvicorn*"
}

if ($processes) {
    $processes | ForEach-Object {
        Write-Host "   Parando processo: $($_.Id)" -ForegroundColor Red
        Stop-Process -Id $_.Id -Force
    }
    Write-Host "✅ Backend parado com sucesso!" -ForegroundColor Green
} else {
    Write-Host "ℹ️  Nenhum processo do backend encontrado rodando." -ForegroundColor Cyan
}
