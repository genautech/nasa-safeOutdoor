# Google Earth Engine - Setup Completo

## Por Que Earth Engine?

✅ **100% Cirúrgico** - Sem downloads de arquivos grandes (800MB+)  
✅ **Acesso direto** aos dados TEMPO e Sentinel-5P  
✅ **Cobertura global** - América do Norte (TEMPO) + Mundial (Sentinel-5P)  
✅ **Gratuito** para uso não-comercial (250 requests/dia)  
✅ **API simples** - Muito mais fácil que earthaccess, xarray, netCDF4  

---

## Passo 1: Registrar no Earth Engine (5 minutos)

### Criar Conta Google Earth Engine

1. Acesse: **https://code.earthengine.google.com/register**
2. Faça login com sua conta Google
3. Selecione **"Unpaid usage"** (gratuito, não-comercial)
4. Aceite os termos de uso
5. Crie um projeto Cloud (ex: `my-air-quality-project`)

**✅ Pronto! Você tem acesso ao Earth Engine gratuitamente!**

---

## Passo 2: Configuração Local (Desenvolvimento)

### Instalar Dependência

```bash
cd backend
pip install earthengine-api
```

### Autenticar (Primeira vez apenas)

```bash
python -c "import ee; ee.Authenticate()"
```

**O que acontece:**
1. Abre navegador automaticamente
2. Você faz login com Google
3. Autoriza o aplicativo
4. Credenciais salvas em `~/.config/earthengine/credentials`
5. Próximas vezes: não precisa autenticar de novo! ✅

### Configurar .env

Edite `backend/.env`:

```env
# Google Earth Engine
GOOGLE_CLOUD_PROJECT_ID=my-air-quality-project  # Nome do seu projeto
```

---

## Passo 3: Testar Localmente

### Reiniciar Backend

```powershell
.\backend-start.ps1
```

### Testar NYC

```bash
curl "http://localhost:8000/api/analyze" -X POST -H "Content-Type: application/json" -d "{\"activity\":\"hiking\",\"lat\":40.7829,\"lon\":-73.9654,\"duration_hours\":4}"
```

**Logs esperados:**
```
✅ Earth Engine initialized with project: my-air-quality-project
🛰️ Trying TEMPO for (40.7829, -73.9654)
✅ Found 8 TEMPO images for 2025-10-05
✅ TEMPO NO2: 15.3 ppb (mean=8.69e+15 molec/cm²)
```

---

## Passo 4: Deploy no Render (Produção)

### Opção A: OAuth (Desenvolvimento - NÃO RECOMENDADO)

❌ Não funciona em servidor sem navegador

### Opção B: Service Account (Produção - RECOMENDADO)

#### 1. Criar Service Account

1. Acesse: **https://console.cloud.google.com/iam-admin/serviceaccounts**
2. Selecione seu projeto (`my-air-quality-project`)
3. Clique em **"Create Service Account"**
4. Nome: `safeoutdoor-ee-service`
5. Role: **"Earth Engine Resource Writer"**
6. Clique em **"Create"**

#### 2. Baixar Chave JSON

1. Na lista de Service Accounts, clique nos 3 pontos
2. **"Manage keys"** → **"Add Key"** → **"Create new key"**
3. Tipo: **JSON**
4. Salva arquivo `ee-service-account.json`

#### 3. Adicionar Variáveis no Render

No painel do Render, vá em **Environment Variables**:

```
GOOGLE_SERVICE_ACCOUNT_EMAIL=safeoutdoor-ee-service@my-air-quality-project.iam.gserviceaccount.com

GOOGLE_SERVICE_ACCOUNT_KEY={"type":"service_account","project_id":"my-air-quality-project","private_key_id":"abc123...","private_key":"-----BEGIN PRIVATE KEY-----\n..."}
```

**⚠️ IMPORTANTE:**
- `GOOGLE_SERVICE_ACCOUNT_KEY` deve ser o conteúdo completo do arquivo JSON **em uma linha**
- Mantenha as aspas e barras (`\n`)

#### 4. Deploy

```bash
git add .
git commit -m "feat: implementar Google Earth Engine para TEMPO"
git push
```

**Render vai:**
1. Instalar `earthengine-api`
2. Inicializar com Service Account
3. TEMPO funcionando! ✅

---

## O Que o Sistema Faz Agora

### Prioridade de Dados NO2:

```
1. TEMPO (América do Norte, hourly, ~10km)
   ↓ Se falhar ou fora da cobertura
2. Sentinel-5P (Global, daily, ~7km)
   ↓ Se falhar
3. OpenAQ (Estações terrestres, global)
```

### Cobertura TEMPO:
- **Região:** América do Norte (15°N-70°N, 170°W-40°W)
- **Cidades:** NYC ✅, LA ✅, Chicago ✅, Toronto ✅, México ✅

### Cobertura Sentinel-5P:
- **Região:** Global 🌍
- **Todas as cidades do mundo** ✅

---

## Troubleshooting

### Erro: "Please specify a project"

**Solução:** Adicione `GOOGLE_CLOUD_PROJECT_ID` no `.env`

### Erro: "User credentials not found"

**Solução (local):** Rode novamente:
```bash
python -c "import ee; ee.Authenticate(force=True)"
```

**Solução (Render):** Use Service Account (Passo 4B)

### Erro: "Computation timed out"

**Solução:** O radius_km está muito grande. O código já usa 10km por padrão (ótimo).

### Erro: "No TEMPO data for this date"

**Possíveis causas:**
1. Fora da cobertura (ex: Europa, Ásia)
2. Data muito antiga (TEMPO começou em Agosto 2023)
3. Sem dados naquele dia específico

**Solução:** Sistema automaticamente usa Sentinel-5P como fallback ✅

---

## Limites e Quotas

### Gratuito (Unpaid Usage)
- **250 requests/dia** por usuário
- Processamento ilimitado no servidor Google
- Sem custo de armazenamento
- **Suficiente para desenvolvimento e projetos pequenos**

### Comercial (Pago)
- Quotas maiores
- SLA garantido
- Suporte prioritário

---

## Vantagens vs. Solução Anterior (earthaccess)

| Aspecto | earthaccess | Google Earth Engine |
|---------|-------------|-------------------|
| **Setup** | Complexo (Bearer token, .netrc) | Simples (OAuth ou Service Account) |
| **Autenticação** | Travava em AWS metadata | Funciona sempre ✅ |
| **Download** | 800MB por request 😱 | Zero download ✅ |
| **Dependências** | 6 libs pesadas | 1 lib leve ✅ |
| **Velocidade** | Lento (download) | Rápido ✅ |
| **Cobertura** | Só TEMPO | TEMPO + Sentinel-5P ✅ |
| **Fallback** | Não | Automático ✅ |

---

## Recursos

- **Earth Engine Docs:** https://developers.google.com/earth-engine
- **Dataset Catalog:** https://developers.google.com/earth-engine/datasets
- **TEMPO Dataset:** https://developers.google.com/earth-engine/datasets/catalog/NASA_TEMPO_NO2_L3_QA
- **Sentinel-5P Dataset:** https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S5P_NRTI_L3_NO2

---

## Próximos Passos (Opcional)

### Adicionar Mais Poluentes

O Earth Engine também tem:
- **O3** (Ozônio): `COPERNICUS/S5P/NRTI/L3_O3`
- **SO2** (Dióxido de Enxofre): `COPERNICUS/S5P/NRTI/L3_SO2`
- **CO** (Monóxido de Carbono): `COPERNICUS/S5P/NRTI/L3_CO`
- **HCHO** (Formaldeído): `COPERNICUS/S5P/NRTI/L3_HCHO`

Basta adicionar funções similares em `earth_engine_service.py`!

---

**🎉 Agora você tem dados de satélite NASA de forma cirúrgica e eficiente!**

