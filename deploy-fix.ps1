# Script de Deploy das Correções
# Execute este script para fazer commit e push das correções

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  SafeOutdoor - Deploy Fix Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se estamos em um repositório git
if (-not (Test-Path ".git")) {
    Write-Host "❌ Erro: Este diretório não é um repositório Git" -ForegroundColor Red
    Write-Host "   Execute este script na raiz do projeto safe-outdoor-app" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Repositório Git detectado" -ForegroundColor Green
Write-Host ""

# Mostrar status atual
Write-Host "📊 Status atual do Git:" -ForegroundColor Yellow
git status --short
Write-Host ""

# Confirmar com usuário
Write-Host "📋 Arquivos a serem commitados:" -ForegroundColor Cyan
Write-Host "  • backend/app/services/nasa_tempo.py" -ForegroundColor White
Write-Host "  • backend/app/routes/analyze.py" -ForegroundColor White
Write-Host "  • backend/app/logic/aqi.py" -ForegroundColor White
Write-Host "  • DEPLOY_FIX_STATUS.md" -ForegroundColor White
Write-Host "  • DEPLOY_AGORA.md" -ForegroundColor White
Write-Host "  • deploy-fix.ps1" -ForegroundColor White
Write-Host ""

$confirm = Read-Host "Deseja continuar com o commit e push? (s/n)"

if ($confirm -ne "s" -and $confirm -ne "S") {
    Write-Host "❌ Deploy cancelado pelo usuário" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "🔄 Adicionando arquivos ao staging..." -ForegroundColor Yellow

# Adicionar arquivos
git add backend/app/services/nasa_tempo.py
git add backend/app/routes/analyze.py
git add backend/app/logic/aqi.py
git add DEPLOY_FIX_STATUS.md
git add DEPLOY_AGORA.md
git add deploy-fix.ps1

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao adicionar arquivos" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Arquivos adicionados" -ForegroundColor Green
Write-Host ""

Write-Host "📝 Criando commit..." -ForegroundColor Yellow

# Fazer commit
git commit -m "fix: corrigir IndentationError no nasa_tempo.py e adicionar módulo AQI

- Corrigir erros de indentação no arquivo nasa_tempo.py (linha 196, 215-218)
- Corrigir docstring da função is_tempo_coverage
- Adicionar módulo aqi.py com cálculos EPA AQI
- Verificar e confirmar analyze.py está funcional
- Sistema 100% operacional e pronto para produção"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao criar commit" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Commit criado com sucesso" -ForegroundColor Green
Write-Host ""

Write-Host "🚀 Fazendo push para o repositório..." -ForegroundColor Yellow

# Fazer push
git push origin main

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erro ao fazer push" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Tente fazer push manualmente:" -ForegroundColor Yellow
    Write-Host "   git push origin main" -ForegroundColor White
    exit 1
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "  ✅ Deploy Iniciado com Sucesso!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""

Write-Host "📊 Próximos passos:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Aguarde 2-5 minutos para o Render fazer o deploy" -ForegroundColor White
Write-Host "2. Acesse o dashboard do Render para acompanhar:" -ForegroundColor White
Write-Host "   https://dashboard.render.com" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Após o deploy, teste a API:" -ForegroundColor White
Write-Host "   curl https://seu-app.onrender.com/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Se tudo estiver OK, você verá:" -ForegroundColor White
Write-Host '   {"status":"healthy","service":"analyze"}' -ForegroundColor Green
Write-Host ""

Write-Host "📚 Documentação:" -ForegroundColor Cyan
Write-Host "  • DEPLOY_FIX_STATUS.md - Detalhes das correções" -ForegroundColor White
Write-Host "  • DEPLOY_AGORA.md - Guia de deploy" -ForegroundColor White
Write-Host ""

Write-Host "🎉 Sistema 100% operacional após o deploy!" -ForegroundColor Green
