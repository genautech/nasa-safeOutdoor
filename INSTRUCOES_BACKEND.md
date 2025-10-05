# 🚀 Como Rodar o Backend Localmente

## Opção 1: Script Automático (RECOMENDADO)
```powershell
.\backend-start.ps1
```

## Opção 2: Comandos Manuais
Abra o PowerShell no diretório do projeto e execute:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## URLs Importantes
- **Backend API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Para Parar o Backend
Pressione `Ctrl+C` no terminal onde o backend está rodando

## Instalar Dependências (só precisa fazer 1 vez)
Se for a primeira vez ou se adicionar novas dependências:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Troubleshooting

### Erro: "No module named uvicorn"
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install uvicorn fastapi
```

### Porta 8000 já em uso
```powershell
# Encontrar o processo
netstat -ano | findstr :8000

# Matar o processo (substitua <PID> pelo número que apareceu)
taskkill /PID <PID> /F
```

### Backend não inicia
Verifique se o arquivo `.env` existe em `backend/.env` com todas as API keys configuradas.
