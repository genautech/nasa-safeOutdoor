"""
Teste direto das coordenadas de LA para verificar TEMPO
"""
import ee
from datetime import datetime, timedelta
import sys
import io

# Fix encoding para Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Coordenadas EXATAS do log
LA_LAT = 34.0536909
LA_LON = -118.242766

# Inicializar Earth Engine
try:
    # Usar variável de ambiente ou arquivo do backend
    import os
    os.chdir('backend')
    credentials = ee.ServiceAccountCredentials(
        email='safe-outdoor@safe-outdoor-442601.iam.gserviceaccount.com',
        key_file='safe-outdoor-442601-c19c0d6ac1fd.json'
    )
    ee.Initialize(credentials)
    print("OK Earth Engine initialized")
except Exception as e:
    print(f"ERRO Failed to initialize: {e}")
    exit(1)

# Testar cobertura TEMPO
TEMPO_LAT_MIN, TEMPO_LAT_MAX = 15.0, 70.0
TEMPO_LON_MIN, TEMPO_LON_MAX = -170.0, -40.0

print(f"\n📍 Testing LA: ({LA_LAT}, {LA_LON})")
print(f"TEMPO Coverage: lat {TEMPO_LAT_MIN}-{TEMPO_LAT_MAX}, lon {TEMPO_LON_MIN}-{TEMPO_LON_MAX}")

in_coverage = (TEMPO_LAT_MIN <= LA_LAT <= TEMPO_LAT_MAX and
               TEMPO_LON_MIN <= LA_LON <= TEMPO_LON_MAX)
print(f"In TEMPO coverage? {in_coverage}")

if not in_coverage:
    print("ERRO LA esta FORA da cobertura do TEMPO!")
    exit(0)

# Testar com a data hardcoded
date = '2024-09-10'
date_obj = datetime.strptime(date, '%Y-%m-%d')
end_date = (date_obj + timedelta(days=1)).strftime('%Y-%m-%d')

print(f"\n🗓️ Date range: {date} to {end_date}")

# Criar geometria
point = ee.Geometry.Point([LA_LON, LA_LAT])
radius_km = 10.0
area = point.buffer(radius_km * 1000)

print(f"🎯 Search area: {radius_km}km radius around point")

# Buscar TEMPO
tempo = ee.ImageCollection('NASA/TEMPO/NO2_L3_QA')
images = tempo.filterDate(date, end_date).filterBounds(area)

count = images.size().getInfo()
print(f"\nTEMPO images found: {count}")

if count == 0:
    print("ERRO Nenhuma imagem TEMPO encontrada!")
    exit(0)

# Tentar extrair dados
image = images.first()
no2_band = image.select('vertical_column_troposphere')

print("\nExtracting NO2 statistics...")
try:
    stats = no2_band.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=area,
        scale=1000,
        maxPixels=1e9
    ).getInfo()

    print(f"Stats result: {stats}")

    mean_value = stats.get('vertical_column_troposphere_mean')
    print(f"\nMean NO2 value: {mean_value}")

    if mean_value is None:
        print("ERRO Mean value is None - pixels sem dados validos!")
    else:
        print(f"OK Successfully got NO2 value: {mean_value}")

except Exception as e:
    print(f"ERRO Error extracting stats: {e}")
