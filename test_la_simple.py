"""
Teste simples via backend rodando
"""
import sys
import io

# Fix encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Coordenadas dos logs
LA_LAT = 34.0536909
LA_LON = -118.242766

# Bounds do TEMPO (do código)
TEMPO_LAT_MIN, TEMPO_LAT_MAX = 15.0, 70.0
TEMPO_LON_MIN, TEMPO_LON_MAX = -170.0, -40.0

print("=== TESTE COORDENADAS LA ===")
print(f"Latitude: {LA_LAT}")
print(f"Longitude: {LA_LON}")
print()

print("TEMPO Coverage Bounds:")
print(f"  Latitude: {TEMPO_LAT_MIN} to {TEMPO_LAT_MAX}")
print(f"  Longitude: {TEMPO_LON_MIN} to {TEMPO_LON_MAX}")
print()

# Check latitude
lat_ok = TEMPO_LAT_MIN <= LA_LAT <= TEMPO_LAT_MAX
print(f"Latitude check: {LA_LAT} in [{TEMPO_LAT_MIN}, {TEMPO_LAT_MAX}]? {lat_ok}")

# Check longitude
lon_ok = TEMPO_LON_MIN <= LA_LON <= TEMPO_LON_MAX
print(f"Longitude check: {LA_LON} in [{TEMPO_LON_MIN}, {TEMPO_LON_MAX}]? {lon_ok}")

print()
if lat_ok and lon_ok:
    print("RESULTADO: LA ESTA dentro da cobertura do TEMPO")
else:
    print("RESULTADO: LA NAO ESTA na cobertura do TEMPO")
    if not lat_ok:
        print(f"  -> Latitude {LA_LAT} esta fora do range")
    if not lon_ok:
        print(f"  -> Longitude {LA_LON} esta fora do range")

# Análise dos logs
print()
print("=== ANALISE DOS LOGS ===")
print("1. Found 11 TEMPO images for 2024-09-10 -> OK")
print("2. No valid TEMPO NO2 values in region -> PROBLEMA AQUI")
print()
print("Conclusao: TEMPO encontra imagens mas pixels estao vazios/invalidos")
print("Possíveis causas:")
print("  - Nuvens sobre LA nessa data")
print("  - Dados de qualidade ruim (QA filtrou)")
print("  - Raio de busca muito pequeno (10km)")
