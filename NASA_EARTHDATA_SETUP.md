# 🔐 NASA EARTHDATA - CONFIGURAÇÃO COMPLETA

## ✅ PROBLEMA IDENTIFICADO

```
❌ OSError: [Errno -77] NetCDF: Access failure
❌ HTTP Basic: Access denied
```

**Causa**: OPeNDAP da NASA requer autenticação via NASA EarthData.

**Solução**: Configurar credenciais NASA (5 minutos).

---

## 📋 PASSO A PASSO COMPLETO

### PASSO 1: Criar Conta NASA EarthData (GRÁTIS)

1. **Acesse**: https://urs.earthdata.nasa.gov/users/new

2. **Preencha o formulário**:
   ```
   Username:     [escolha um username único]
   Email:        [seu email]
   Password:     [senha forte]
   First Name:   [seu nome]
   Last Name:    [seu sobrenome]
   ```

3. **Aceite os termos** e clique em **"Register for Earthdata Login"**

4. **Verifique seu email** e ative a conta

5. **Faça login**: https://urs.earthdata.nasa.gov/

6. **IMPORTANTE**: Guarde suas credenciais:
   ```
   Username: _______________
   Password: _______________
   ```

---

### PASSO 2: Configurar no Render

1. **Vá no Dashboard do Render**: https://dashboard.render.com

2. **Selecione seu serviço** (backend SafeOutdoor)

3. **Clique em "Environment"** (menu lateral)

4. **Adicione as seguintes variáveis**:

   ```
   Nome da Variável: NASA_EARTHDATA_USER
   Valor: seu_username_nasa_aqui
   ```

   ```
   Nome da Variável: NASA_EARTHDATA_PASSWORD
   Valor: sua_senha_nasa_aqui
   ```

5. **Clique em "Save Changes"**

6. **Render fará redeploy automático** (~3-5 minutos)

---

### PASSO 3: Push do Código Atualizado

O código já foi atualizado para usar as credenciais!

```bash
git add backend/app/services/nasa_tempo.py
git add backend/requirements.txt
git add NASA_EARTHDATA_SETUP.md

git commit -m "feat: add NASA EarthData authentication for TEMPO OPeNDAP

- Add NASA_EARTHDATA_USER and NASA_EARTHDATA_PASSWORD env vars
- Use pydap for authenticated OPeNDAP sessions
- Add pydap dependency
- Now extracts REAL pixel data from TEMPO satellite"

git push origin main
```

---

### PASSO 4: Aguardar Deploy

```
Deploy Timeline:

0:00  → Push detectado
1:00  → Build iniciado
2:00  → Instalando pydap (nova dependency)
3:00  → Installing outras deps
4:00  → Build completo
5:00  → Deploy com novas env vars
6:00  → PRONTO! ✅
```

---

### PASSO 5: Testar

```bash
# Testar NYC (deve usar TEMPO agora!)
curl -X POST https://seu-app.onrender.com/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "activity": "hiking",
    "lat": 40.7128,
    "lon": -74.0060,
    "duration_hours": 4
  }' | jq '.air_quality.no2, .data_sources'
```

**Resultado esperado**:
```json
18.45  // ← NO2 REAL de satélite!
[
  "NASA TEMPO (OPeNDAP)",  // ← FUNCIONANDO!
  "OpenAQ ground stations (PM2.5)",
  ...
]
```

---

## 📊 LOGS ESPERADOS (Sucesso)

```log
[INFO] 🛰️ Fetching NASA TEMPO data for (40.7128, -74.0060)...
[INFO] 🔍 Searching CMR for TEMPO granules
[INFO] ✅ Found TEMPO granule: TEMPO_NO2_L3_V04_20251005T133045Z_S004.nc
[DEBUG] 🔗 OPeNDAP URL: https://opendap.earthdata.nasa.gov/.../TEMPO...
[INFO] 📡 Accessing TEMPO via OPeNDAP
[INFO] 📊 Dataset opened, variables: ['vertical_column_troposphere', ...]
[INFO] 🌍 Grid shape: lat=(2048,), lon=(4096,)
[INFO] 📍 Nearest pixel: [1245, 2389] → (40.7105, -74.0037)
[INFO] ✅ Found NO2 in variable: vertical_column_troposphere
[INFO] ✅ TEMPO NO2: 18.45 ppb (column: 4.54e+15 molec/cm²)
[INFO] ✅ TEMPO data retrieved successfully!
```

---

## ⚠️ TROUBLESHOOTING

### Erro 1: "NASA EarthData credentials not configured"

```log
❌ NASA EarthData credentials not configured!
```

**Solução**:
- Verificar se variáveis foram adicionadas no Render
- Verificar nomes exatos: `NASA_EARTHDATA_USER` e `NASA_EARTHDATA_PASSWORD`
- Fazer redeploy manual se necessário

### Erro 2: "Invalid credentials"

```log
❌ Authentication failed
```

**Solução**:
- Verificar username e password estão corretos
- Fazer login em https://urs.earthdata.nasa.gov/ para confirmar
- Verificar se conta foi ativada por email

### Erro 3: "pydap not found"

```log
ModuleNotFoundError: No module named 'pydap'
```

**Solução**:
- Verificar se `pydap==3.5.0` está em requirements.txt
- Fazer novo push se necessário
- Aguardar build completo

---

## 🔒 SEGURANÇA

### ✅ BOAS PRÁTICAS

1. **Nunca comite credenciais no código**
   - ✅ Usamos environment variables
   - ✅ Credentials apenas no Render dashboard

2. **Use senhas fortes**
   - Mínimo 12 caracteres
   - Mix de letras, números, símbolos

3. **Rotacione senhas periodicamente**
   - Mude senha NASA a cada 6 meses
   - Atualize no Render

### ❌ NÃO FAÇA

- ❌ Não coloque credenciais em código
- ❌ Não compartilhe credenciais publicamente
- ❌ Não use mesma senha de outros serviços

---

## 📚 REFERÊNCIAS

### NASA EarthData

- **Login**: https://urs.earthdata.nasa.gov/
- **Documentação**: https://urs.earthdata.nasa.gov/documentation
- **TEMPO Data**: https://www-air.larc.nasa.gov/missions/tempo/

### pydap (Python OPeNDAP Client)

- **GitHub**: https://github.com/pydap/pydap
- **Docs**: https://pydap.github.io/pydap/
- **NASA URS**: https://pydap.github.io/pydap/client.html#authentication

---

## ✅ CHECKLIST FINAL

Antes de testar, confirme:

- [ ] Conta NASA EarthData criada ✅
- [ ] Email verificado ✅
- [ ] Credenciais salvas ✅
- [ ] `NASA_EARTHDATA_USER` no Render ✅
- [ ] `NASA_EARTHDATA_PASSWORD` no Render ✅
- [ ] Código commitado e pushed ✅
- [ ] Deploy completo no Render ✅
- [ ] Aguardou 5-7 minutos ✅
- [ ] Testou endpoint ✅

---

## 🎉 RESULTADO FINAL

Com tudo configurado:

```
┌─────────────────────────────────────────┐
│  NYC Request (40.7128, -74.0060)        │
├─────────────────────────────────────────┤
│                                         │
│  1. Check TEMPO coverage → YES ✅       │
│  2. Find TEMPO granule → FOUND ✅       │
│  3. OPeNDAP with auth → SUCCESS ✅      │
│  4. Extract pixel → 18.45 ppb ✅        │
│  5. Return real data → DONE ✅          │
│                                         │
│  Result: REAL SATELLITE DATA! 🛰️        │
│                                         │
└─────────────────────────────────────────┘
```

---

## 💬 PERGUNTAS FREQUENTES

**Q: A conta NASA é grátis?**
A: Sim! 100% gratuita.

**Q: Tem limite de requests?**
A: Não há limite oficial publicado. Use com moderação.

**Q: Funciona fora dos EUA?**
A: Sim! OPeNDAP funciona globalmente.

**Q: E se esquecer a senha?**
A: Reset em https://urs.earthdata.nasa.gov/password/new

**Q: Precisa reautenticar?**
A: Não. Credentials são salvas no Render.

---

**Status**: ✅ Guia completo pronto!
**Tempo estimado**: 5-10 minutos total
**Dificuldade**: Fácil 🟢
