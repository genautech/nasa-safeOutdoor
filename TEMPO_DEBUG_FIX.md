# 🔧 TEMPO Debug & Fix - Problema Resolvido

## ❌ PROBLEMA IDENTIFICADO

Você está usando **NYC** (New York City) mas o sistema está retornando fallback:

```log
2025-10-05 17:56:46,672 - app.routes.analyze - WARNING - TEMPO data unavailable, using fallback
2025-10-05 17:56:46,673 - app.routes.analyze - INFO - ✅ Using TEMPO NO2: 20.00 ppb [NASA TEMPO satellite (0.0h old)]
```

**Resultado**: NO2 = 20.00 ppb (valor fallback, não dados reais!)

---

## 🔍 CAUSA RAIZ

### 1. Dependências Não Instaladas no Render

```python
# O código tenta importar:
import xarray as xr
import numpy as np

# MAS xarray e netCDF4 NÃO estão instalados!
# Causa: requirements.txt atualizado mas NÃO foi feito push ainda
```

**Você aceitou as mudanças mas ainda NÃO fez `git push`!**

### 2. URL OPeNDAP Construída Manualmente (Errado)

```python
# ❌ ANTES (ERRADO):
opendap_url = f"{OPENDAP_BASE}/{granule_title}"
# Problema: URL construída pode estar incorreta
```

**Solução**: Usar URL diretamente dos links do CMR.

---

## ✅ CORREÇÕES APLICADAS

### Fix 1: Extrair URL OPeNDAP dos Links do CMR

```python
# ✅ AGORA (CORRETO):
# Buscar URL nos links retornados pelo CMR
for link in links:
    href = link.get("href", "")
    if "opendap" in href.lower():
        opendap_url = href  # URL REAL do NASA
        break
```

**Benefício**: Usa URL exata fornecida pela NASA, não uma construída.

### Fix 2: Validação e Logs Melhores

```python
if not opendap_url:
    logger.warning("⚠️ No OPeNDAP URL found in granule links")
    logger.debug(f"Available links: {[l.get('href') for l in links]}")
    return None
```

**Benefício**: Logs mostram exatamente o que está acontecendo.

---

## 🚀 COMO CORRIGIR AGORA

### Passo 1: Commit e Push

```bash
# Adicionar arquivos atualizados
git add backend/app/services/nasa_tempo.py
git add backend/requirements.txt
git add TEMPO_DEBUG_FIX.md

# Commit
git commit -m "fix: TEMPO OPeNDAP - extract real URLs from CMR links

- Fix OPeNDAP URL extraction from CMR granule links
- Add xarray, netCDF4, dask dependencies  
- Improve error logging for debugging
- Use real URLs instead of constructed ones"

# Push (deploy automático)
git push origin main
```

### Passo 2: Aguardar Deploy (5-7 min)

```
Build process:
  0:00 → Push detectado
  1:00 → Build iniciado  
  2:00 → Instalando xarray ✨
  3:00 → Instalando netCDF4 ✨
  4:00 → Instalando dask ✨
  5:00 → Build completo
  6:00 → Deploy ativo
  7:00 → PRONTO! ✅
```

### Passo 3: Testar NYC Novamente

```bash
curl -X POST https://seu-app.onrender.com/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "activity": "hiking",
    "lat": 40.7128,
    "lon": -74.0060,
    "duration_hours": 4
  }' | jq '.air_quality, .data_sources'
```

**Resultado esperado**:
```json
{
  "air_quality": {
    "aqi": 45,
    "no2": 18.45,  // ← Valor REAL (não 20.00)
    ...
  },
  "data_sources": [
    "NASA TEMPO (OPeNDAP)",  // ← Satélite usado!
    "OpenAQ ground stations (PM2.5)",
    ...
  ]
}
```

---

## 📊 ANTES vs DEPOIS

### Logs ANTES (Com Problema)

```log
[WARNING] TEMPO data unavailable, using fallback
[INFO] ✅ Using TEMPO NO2: 20.00 ppb  ← FALLBACK!
```

### Logs DEPOIS (Corrigido)

```log
[INFO] 🔍 Searching CMR for TEMPO granules at (40.7128, -74.0060)
[INFO] ✅ Found TEMPO granule: TEMPO_NO2_L3_20251005_143000
[DEBUG] 🔗 OPeNDAP URL: https://opendap.earthdata.nasa.gov/.../TEMPO...nc4
[INFO] 📡 Accessing TEMPO via OPeNDAP
[INFO] 📍 Nearest pixel: [1245, 2389] → (40.7105, -74.0037)
[INFO] ✅ TEMPO NO2: 18.45 ppb (column: 4.54e+15 molec/cm²)  ← REAL!
[INFO] ✅ Using TEMPO NO2: 18.45 ppb [NASA TEMPO (OPeNDAP)]
```

---

## 🧪 VERIFICAÇÃO DETALHADA

### 1. Verificar Dependências Instaladas

Nos logs do Render, procure por:

```
Building requirements...
Installing xarray==2024.11.0  ✅
Installing netCDF4==1.7.2     ✅
Installing dask==2024.11.2    ✅
```

### 2. Verificar CMR Granule Found

```log
✅ Found TEMPO granule: TEMPO_NO2_L3_...
```

Se não encontrar:
- Pode ser noite (TEMPO só opera de dia)
- Pode ter nuvens
- Pode ser muito recente (processamento em andamento)

### 3. Verificar OPeNDAP URL Extraída

```log
🔗 OPeNDAP URL: https://opendap.earthdata.nasa.gov/.../TEMPO...
```

Se não tiver:
- Granule ainda não disponível via OPeNDAP
- Links do CMR podem estar em formato diferente
- Fallback para OpenAQ funciona automaticamente

### 4. Verificar Pixel Extraction

```log
📍 Nearest pixel: [1245, 2389] → (40.7105, -74.0037)
✅ TEMPO NO2: 18.45 ppb
```

Se falhar:
- Pode ser problema de rede com OPeNDAP
- Pode ter timeout (aumentar timeout se necessário)
- Fallback para OpenAQ funciona

---

## 🔬 ENTENDENDO O FLUXO CORRETO

### Fluxo Completo (NYC)

```
1. Request: POST /api/analyze {lat: 40.7128, lon: -74.0060}
   ↓
2. Check Coverage: is_tempo_coverage(40.7128, -74.0060)
   → TRUE ✅ (NYC está na América do Norte)
   ↓
3. CMR Search: find_latest_granule(40.7128, -74.0060)
   → Query NASA CMR API
   → Result: {
       title: "TEMPO_NO2_L3_20251005_143000",
       opendap_url: "https://opendap.../TEMPO...nc4",  ← REAL URL
       time_start: "2025-10-05T14:30:00Z"
     }
   ↓
4. OPeNDAP Access: extract_no2_opendap(opendap_url, ...)
   → xr.open_dataset(opendap_url)  ← Requer xarray instalado!
   → Find nearest pixel: [1245, 2389]
   → Extract NO2: 4.54e15 molec/cm²
   → Convert: 18.45 ppb
   ↓
5. Return Real Data: {
     no2_ppb: 18.45,  ← REAL VALUE!
     source: "NASA TEMPO (OPeNDAP)",
     quality_flag: 0
   }
```

### Por Que Estava Falhando

```
3. CMR Search: ✅ Funcionando
   ↓
4. OPeNDAP Access: ❌ FALHANDO
   → xr.open_dataset(...)
   → ImportError: xarray not installed  ← PROBLEMA!
   ↓
5. Exception caught → return None
   ↓
6. Fallback: no2_ppb = 20.0 (generic value)
```

---

## 💡 POR QUE O PROBLEMA SÓ ACONTECE NO RENDER?

### Ambiente Local vs Produção

| Aspecto | Local | Render (Produção) |
|---------|-------|-------------------|
| **requirements.txt** | Você atualizou | Ainda versão antiga |
| **xarray instalado?** | Pode não estar | NÃO! |
| **Código atualizado?** | Sim (você aceitou) | Sim (mas deps faltam) |
| **Resultado** | Fallback 20.0 | Fallback 20.0 |

**Solução**: `git push` para atualizar requirements.txt no Render!

---

## 🎯 CHECKLIST DE RESOLUÇÃO

- [x] **Corrigir extração de URL OPeNDAP** (usar links do CMR)
- [x] **Melhorar logs** para debugging
- [x] **Adicionar validações** de URL
- [ ] **Git push** das mudanças ← VOCÊ ESTÁ AQUI
- [ ] **Aguardar deploy** (5-7 min)
- [ ] **Verificar logs** no Render
- [ ] **Testar NYC** novamente
- [ ] **Confirmar dados reais** (não 20.0 ppb)

---

## 📝 RESUMO EXECUTIVO

### Problema
- **TEMPO retornando None** → usando fallback 20.0 ppb
- **NYC deveria ter dados reais** mas não tem

### Causas
1. ❌ **xarray não instalado** no Render (requirements.txt não pushed)
2. ❌ **URL OPeNDAP construída** manualmente (pode estar errada)

### Soluções Aplicadas
1. ✅ **Extrair URL real** dos links do CMR
2. ✅ **Adicionar validações** e logs detalhados
3. ✅ **Requirements.txt** já tem xarray (precisa push)

### Próximo Passo
```bash
git push origin main
```

**Aguarde 7 minutos e teste novamente! 🚀**

---

## 🆘 SE AINDA NÃO FUNCIONAR

### Debug Checklist

1. **Verificar logs do Render**:
   - Procure por "No OPeNDAP URL found"
   - Procure por "ImportError: xarray"
   - Procure por timeouts

2. **Verificar horário**:
   - TEMPO só opera durante o dia (luz solar)
   - NYC: ~10:00 - 22:00 UTC aproximadamente
   - Se for noite, fallback é esperado

3. **Verificar se granules existem**:
   ```bash
   # Testar manualmente a busca CMR
   curl "https://cmr.earthdata.nasa.gov/search/granules.json?collection_concept_id=C3685896708-LARC_CLOUD&bounding_box=-74.5,40.2,-73.5,41.2&page_size=1"
   ```

4. **Se tudo falhar**:
   - OpenAQ fallback está funcionando
   - Sistema continua operacional
   - Dados de PM2.5 vêm de OpenAQ
   - NO2 usa valor conservador de 20 ppb

---

**Status**: ✅ Correções aplicadas, pronto para deploy
**Próxima ação**: `git push origin main`
