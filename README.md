# Safe Outdoor App 🌤️

Aplicação web para análise de segurança de atividades ao ar livre, combinando dados de qualidade do ar, clima, elevação e recomendações personalizadas por IA.

## 🚀 Stack Tecnológico

- **Frontend**: Next.js 15 + React 18 + TypeScript
- **Backend**: FastAPI (Python) - [Deploy no Render](https://safeoutdoor-backend-3yse.onrender.com)
- **UI**: Tailwind CSS + Radix UI + shadcn/ui
- **APIs**: OpenWeather, OpenAQ, Google Earth Engine, Anthropic Claude

## 📦 Instalação e Desenvolvimento Local

### Frontend (Next.js)

```bash
# Instalar dependências
npm install

# Configurar ambiente
cp .env.example .env.local

# Desenvolvimento (http://localhost:3000)
npm run dev
```

### Backend (FastAPI) - Opcional

O backend já está em produção no Render, mas se quiser rodar localmente:

```bash
# Navegar para pasta do backend
cd backend

# Criar ambiente virtual Python
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Edite .env e adicione suas API keys

# Rodar servidor (http://localhost:8000)
uvicorn app.main:app --reload
```

**Para usar backend local no frontend**, edite `.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🌍 Deploy em Produção

### ⭐ Opção 1: Vercel (RECOMENDADO para Frontend)

A Vercel é a plataforma oficial do Next.js e oferece a melhor performance e integração.

**Passos Rápidos:**

1. **Push para GitHub**
   ```bash
   git add .
   git commit -m "feat: deploy configuration"
   git push origin main
   ```

2. **Deploy na Vercel**
   - Acesse [vercel.com](https://vercel.com) e faça login com GitHub
   - Clique em **"Add New Project"**
   - Selecione seu repositório `safe-outdoor-app`
   - Configure:
     - **Framework Preset**: Next.js (detectado automaticamente)
     - **Root Directory**: `./` (raiz do projeto)
     - **Build Command**: `npm run build` (padrão)
     - **Output Directory**: `.next` (padrão)

3. **Adicionar Variável de Ambiente**
   - Na tela de deploy, clique em **"Environment Variables"**
   - Adicione:
     ```
     Name: NEXT_PUBLIC_API_URL
     Value: https://safeoutdoor-backend-3yse.onrender.com
     ```

4. **Clicar em "Deploy"**

5. **Pronto!** 🎉
   - Deploy leva ~2 minutos
   - Seu app estará disponível em: `https://seu-projeto.vercel.app`
   - Cada push para `main` faz deploy automático

**Vantagens da Vercel:**
- ✅ Deploy automático a cada push
- ✅ Preview deployments automáticos para PRs
- ✅ CDN global (Edge Network) - velocidade máxima
- ✅ SSL/HTTPS automático
- ✅ Logs e analytics integrados
- ✅ Zero configuração para Next.js
- ✅ Domínio customizado gratuito (.vercel.app)

**Configurações Avançadas (Opcional):**
O arquivo `vercel.json` já está configurado, mas você pode customizar:
- Adicionar domínio personalizado em Settings → Domains
- Configurar redirects e rewrites
- Ajustar regiões de deploy (padrão: Washington D.C. - iad1)

### 🔄 Opção 2: Render (Alternativa)

Boa opção se quiser hospedar frontend e backend no mesmo lugar.

**Passos:**

1. **Criar Web Service**
   - Acesse [render.com](https://render.com) e faça login
   - Clique em **"New +"** → **"Web Service"**
   - Conecte seu repositório do GitHub

2. **Configurações**
   ```
   Name: safe-outdoor-frontend
   Environment: Node
   Build Command: npm run build
   Start Command: npm start
   ```

3. **Variáveis de Ambiente**
   ```
   NEXT_PUBLIC_API_URL=https://safeoutdoor-backend-3yse.onrender.com
   ```

4. **Deploy** - Clique em "Create Web Service"

**Nota**: O Render pode ser mais lento para builds do que a Vercel (plano gratuito).

## ⚙️ Configuração de Ambiente

### Variáveis de Ambiente

O app suporta múltiplos ambientes automaticamente:

| Ambiente | Configuração | URL do Backend |
|----------|-------------|----------------|
| **Produção (Vercel/Render)** | Variável de ambiente na plataforma | https://safeoutdoor-backend-3yse.onrender.com |
| **Desenvolvimento Local (backend remoto)** | `.env.local` com valor padrão ou vazio | https://safeoutdoor-backend-3yse.onrender.com (fallback) |
| **Desenvolvimento Local (backend local)** | `.env.local` com `NEXT_PUBLIC_API_URL=http://localhost:8000` | http://localhost:8000 |

**Exemplo `.env.local` para desenvolvimento:**
```bash
# Usar backend em produção (Render)
NEXT_PUBLIC_API_URL=https://safeoutdoor-backend-3yse.onrender.com

# OU usar backend local
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Como funciona:**
- O código usa `process.env.NEXT_PUBLIC_API_URL` primeiro
- Se não estiver configurado, usa `https://safeoutdoor-backend-3yse.onrender.com` como fallback
- Veja a lógica em `lib/api.ts:13`

## 🛠️ Scripts Disponíveis

```bash
npm run dev      # Desenvolvimento (localhost:3000)
npm run build    # Build de produção
npm run start    # Iniciar servidor de produção
npm run lint     # Verificar código
```

## 📁 Estrutura do Projeto

```
safe-outdoor-app/
├── app/              # Páginas Next.js (App Router)
├── components/       # Componentes React reutilizáveis
├── lib/              # Utilitários e configurações
│   └── api.ts        # Cliente API (configuração de URLs)
├── .env.local        # Variáveis de ambiente locais
├── .env.example      # Template de variáveis de ambiente
└── package.json      # Dependências e scripts
```

## 🔗 Links Úteis

- **Backend API**: https://safeoutdoor-backend-3yse.onrender.com
- **API Docs**: https://safeoutdoor-backend-3yse.onrender.com/docs
- **Health Check**: https://safeoutdoor-backend-3yse.onrender.com/health

## 📝 Notas

- O backend no Render pode "hibernar" após inatividade. A primeira requisição pode demorar ~30s enquanto o servidor acorda.
- Para melhor performance, considere upgrade do plano no Render ou migrar para Vercel Edge Functions.
- Todas as API keys do backend estão configuradas no Render (OpenWeather, OpenAQ, Earth Engine, Anthropic).

## 🐛 Troubleshooting

**Erro de CORS?**
- Verifique se o backend está rodando
- Confirme a URL do backend no `.env.local` ou nas variáveis de ambiente do hosting

**Timeout?**
- O backend pode estar hibernando (plano grátis do Render)
- Aguarde ~30s e tente novamente

**Build falhou?**
- Execute `npm install` para garantir que todas as dependências estão instaladas
- Verifique se tem Node.js 18+ instalado

---

Desenvolvido com ❤️ usando Next.js e FastAPI
