# Configuração do Ngrok - SafeOutdoor

## ✅ Instalação Completa!

O ngrok foi instalado com sucesso no seu sistema (versão 3.30.0).

## 📋 Próximos Passos

### 1. Configurar Authtoken (Obrigatório)

Para usar o ngrok, você precisa de uma conta gratuita:

1. **Criar conta**: Acesse https://dashboard.ngrok.com/signup
2. **Obter authtoken**: Vá para https://dashboard.ngrok.com/get-started/your-authtoken
3. **Configurar**: Execute no terminal:
   ```powershell
   ngrok config add-authtoken SEU_TOKEN_AQUI
   ```

### 2. Usar com SafeOutdoor

#### Método Rápido (Script Automatizado)

```powershell
.\start-ngrok.ps1
```

Este script vai:
- Verificar se você configurou o authtoken
- Iniciar o ngrok na porta 8000 (backend FastAPI)
- Mostrar a URL pública para acessar sua API

#### Método Manual

```powershell
# Expor o backend (porta 8000)
ngrok http 8000

# Expor o frontend (porta 3000) - se necessário
ngrok http 3000
```

## 🎯 Workflow Recomendado

### Para Desenvolvimento:

1. **Terminal 1** - Iniciar o backend:
   ```powershell
   cd backend
   .\venv\Scripts\activate
   uvicorn app.main:app --reload
   ```

2. **Terminal 2** - Iniciar o ngrok:
   ```powershell
   .\start-ngrok.ps1
   ```
   
3. **Terminal 3** - Iniciar o frontend:
   ```powershell
   npm run dev
   ```

4. **Configurar Frontend**: Copie a URL do ngrok (ex: `https://abc123.ngrok.io`) e use no lugar de `http://localhost:8000` para testar remotamente.

## 🔧 Comandos Úteis

```powershell
# Ver versão
ngrok version

# Iniciar com domínio customizado (plano pago)
ngrok http 8000 --domain=seu-dominio.ngrok.app

# Ver túneis ativos
# Acesse: http://localhost:4040

# Parar o túnel
# Pressione Ctrl+C
```

## 📱 Interface Web do Ngrok

Quando o ngrok está rodando, acesse `http://localhost:4040` para ver:
- URL pública do túnel
- Requisições em tempo real
- Histórico de requests
- Replay de requisições

## 🌍 Casos de Uso

### 1. Testar API Remotamente
```powershell
ngrok http 8000
# Use a URL HTTPS fornecida para testar de qualquer lugar
```

### 2. Compartilhar com Equipe
Envie a URL do ngrok para colegas testarem sua API sem precisar configurar nada.

### 3. Testar Webhooks
Ideal para testar integrações que precisam de URLs públicas (ex: pagamentos, APIs externas).

### 4. Testar em Dispositivos Móveis
Use a URL do ngrok para testar sua aplicação em celulares/tablets sem estar na mesma rede.

## ⚙️ Configuração Avançada

### Arquivo de Configuração

O ngrok usa: `%USERPROFILE%\.ngrok2\ngrok.yml`

Exemplo de configuração customizada:
```yaml
version: "2"
authtoken: seu_token_aqui
tunnels:
  backend:
    proto: http
    addr: 8000
  frontend:
    proto: http
    addr: 3000
```

Para iniciar múltiplos túneis:
```powershell
ngrok start backend frontend
```

## 🔒 Segurança

### Plano Gratuito
- ✅ HTTPS automático
- ✅ Túneis seguros
- ⚠️ URL muda a cada execução
- ⚠️ Limite de conexões simultâneas

### Dicas de Segurança
1. Não compartilhe URLs do ngrok publicamente (Twitter, GitHub, etc.)
2. Use autenticação básica se necessário:
   ```powershell
   ngrok http 8000 --basic-auth="usuario:senha"
   ```
3. Feche o túnel quando não estiver usando
4. URLs expiram quando o túnel é fechado

## ❌ Troubleshooting

### "ngrok não é reconhecido"
Se o ngrok não for reconhecido após a instalação, feche e reabra o terminal PowerShell.

### "Please sign up"
Você precisa configurar o authtoken (veja passo 1 acima).

### "Tunnel not found"
O servidor local não está rodando. Certifique-se de que o backend está ativo em `http://localhost:8000`.

### "Too many connections"
Plano gratuito tem limite de conexões. Atualize para um plano pago ou aguarde.

## 📚 Recursos

- **Dashboard**: https://dashboard.ngrok.com
- **Documentação**: https://ngrok.com/docs
- **Status**: https://status.ngrok.com
- **Pricing**: https://ngrok.com/pricing

## 🎓 Dicas Rápidas

1. **URLs temporárias**: No plano gratuito, a URL muda a cada reinício
2. **Múltiplos túneis**: Plano gratuito permite 1 túnel por vez (2 com conta)
3. **Domínios fixos**: Disponível em planos pagos
4. **Logs**: Todos os requests são visíveis em `http://localhost:4040`
5. **Replay**: Você pode reenviar requests da interface web

---

**Status**: ✅ Ngrok instalado e pronto para uso!
**Localização**: `%USERPROFILE%\ngrok\ngrok.exe`
**Versão**: 3.30.0
