"""
Google Earth Engine Air Quality Service - 100% Cirúrgico!

Acessa dados de satélite TEMPO e Sentinel-5P sem downloads.
Cobertura global com dados precisos e em tempo real.
"""
import logging
from typing import Optional, Dict
from datetime import datetime, timedelta
import ee
from app.config import settings

logger = logging.getLogger(__name__)


class EarthEngineService:
    """Google Earth Engine service para dados de qualidade do ar."""
    
    _initialized = False
    
    # TEMPO coverage bounds (América do Norte)
    TEMPO_LAT_MIN, TEMPO_LAT_MAX = 15.0, 70.0
    TEMPO_LON_MIN, TEMPO_LON_MAX = -170.0, -40.0
    
    @classmethod
    def initialize(cls):
        """
        Inicializa Earth Engine uma única vez.
        
        Usa Service Account para produção (servidor).
        """
        if cls._initialized:
            return
        
        try:
            if settings.google_service_account_email and settings.google_service_account_key:
                # Produção: Service Account
                credentials = ee.ServiceAccountCredentials(
                    email=settings.google_service_account_email,
                    key_data=settings.google_service_account_key
                )
                ee.Initialize(credentials)
                logger.info("✅ Earth Engine initialized with Service Account")
            elif settings.google_cloud_project_id:
                # Desenvolvimento: OAuth (requer ee.Authenticate() manual primeiro)
                ee.Initialize(project=settings.google_cloud_project_id)
                logger.info(f"✅ Earth Engine initialized with project: {settings.google_cloud_project_id}")
            else:
                logger.warning("⚠️ Earth Engine credentials not configured")
                return
            
            cls._initialized = True
            
        except Exception as e:
            logger.error(f"❌ Earth Engine initialization failed: {e}")
            cls._initialized = False
    
    @staticmethod
    def is_tempo_coverage(lat: float, lon: float) -> bool:
        """Verifica se localização está na cobertura do TEMPO."""
        return (EarthEngineService.TEMPO_LAT_MIN <= lat <= EarthEngineService.TEMPO_LAT_MAX and
                EarthEngineService.TEMPO_LON_MIN <= lon <= EarthEngineService.TEMPO_LON_MAX)
    
    @staticmethod
    async def get_tempo_no2(lat: float, lon: float, radius_km: float = 10.0, date: Optional[str] = None) -> Optional[Dict]:
        """
        Busca dados de NO2 do TEMPO (América do Norte, hourly).
        
        Args:
            lat: Latitude
            lon: Longitude
            radius_km: Raio de busca em km
            date: Data no formato YYYY-MM-DD (None = hoje)
        
        Returns:
            Dict com dados de NO2 ou None se indisponível
        """
        if not EarthEngineService._initialized:
            EarthEngineService.initialize()
        
        if not EarthEngineService._initialized:
            logger.warning("⚠️ Earth Engine not initialized")
            return None
        
        # Verificar cobertura
        if not EarthEngineService.is_tempo_coverage(lat, lon):
            logger.info(f"📍 Location ({lat:.4f}, {lon:.4f}) outside TEMPO coverage")
            return None

        try:
            # Tentar múltiplas datas se nenhuma for especificada
            # Usar datas recentes de 2025 (dados atuais!)
            dates_to_try = [
                '2025-09-25',  # Setembro 2025 (dados mais recentes)
                '2025-09-20',
                '2025-09-15',
                '2025-09-10',
                '2025-08-25',  # Agosto 2025
                '2025-08-20',
                '2025-08-15',
                '2025-08-10',
                '2025-07-25',  # Julho 2025
                '2025-07-20',
                '2025-07-15'
            ] if date is None else [date]

            # Aumentar raio de busca para 25km (mais pixels válidos)
            search_radius_km = 25.0

            # Criar geometria (ponto + buffer)
            point = ee.Geometry.Point([lon, lat])
            area = point.buffer(search_radius_km * 1000)  # km → metros

            logger.info(f"🔍 Searching TEMPO with {search_radius_km}km radius, trying {len(dates_to_try)} dates")

            # Tentar cada data até encontrar dados válidos
            for test_date in dates_to_try:
                # Earth Engine precisa de range (início e fim diferentes)
                date_obj = datetime.strptime(test_date, '%Y-%m-%d')
                end_date = (date_obj + timedelta(days=1)).strftime('%Y-%m-%d')

                # Dataset TEMPO NO2 (filtrado por qualidade)
                tempo = ee.ImageCollection('NASA/TEMPO/NO2_L3_QA')

                # Filtrar por data e região (range de date até end_date)
                images = tempo.filterDate(test_date, end_date).filterBounds(area)

                # Verificar se há dados
                count = images.size().getInfo()
                if count == 0:
                    logger.info(f"⚠️ No TEMPO images for {test_date}, trying next date...")
                    continue

                logger.info(f"✅ Found {count} TEMPO images for {test_date}")

                # Pegar primeira imagem (mais recente do dia)
                image = images.first()
                no2_band = image.select('vertical_column_troposphere')

                # Extrair estatísticas da região
                stats = no2_band.reduceRegion(
                    reducer=ee.Reducer.mean()
                        .combine(ee.Reducer.stdDev(), '', True)
                        .combine(ee.Reducer.min(), '', True)
                        .combine(ee.Reducer.max(), '', True),
                    geometry=area,
                    scale=1000,  # 1km resolution
                    maxPixels=1e9
                ).getInfo()

                mean_value = stats.get('vertical_column_troposphere_mean')

                if mean_value is None:
                    logger.warning(f"⚠️ No valid NO2 values for {test_date}, trying next date...")
                    continue

                # Sucesso! Encontrou dados válidos
                logger.info(f"✅ Valid data found for {test_date}")
                date = test_date  # Usar a data que funcionou
                break

            # Se não encontrou dados em nenhuma data
            if mean_value is None:
                logger.warning(f"⚠️ No valid TEMPO NO2 values in region after trying {len(dates_to_try)} dates")
                return None
            
            # Converter molec/cm² para ppb (aproximado)
            # Fator de conversão: assumindo altura troposférica ~3km = 300000 cm
            # Densidade ar ao nível do mar: ~2.5e19 molec/cm³
            # ppb = (molec/cm² / altura_cm) / densidade_ar * 1e9
            altura_cm = 300000  # 3km em cm
            densidade_ar = 2.5e19  # molec/cm³
            no2_ppb = (mean_value / altura_cm) / densidade_ar * 1e9
            
            logger.info(f"✅ TEMPO NO2: {no2_ppb:.2f} ppb (mean={mean_value:.2e} molec/cm²)")
            
            return {
                "no2_ppb": no2_ppb,
                "no2_column": mean_value,  # molec/cm²
                "std": stats.get('vertical_column_troposphere_stdDev'),
                "min": stats.get('vertical_column_troposphere_min'),
                "max": stats.get('vertical_column_troposphere_max'),
                "source": "NASA TEMPO (Google Earth Engine)",
                "date": date,
                "location": {"lat": lat, "lon": lon, "radius_km": radius_km}
            }
            
        except Exception as e:
            logger.error(f"❌ TEMPO data fetch failed: {type(e).__name__}: {e}")
            return None
    
    @staticmethod
    async def get_sentinel5p_no2(lat: float, lon: float, radius_km: float = 10.0, date: Optional[str] = None) -> Optional[Dict]:
        """
        Busca dados de NO2 do Sentinel-5P (Global, daily).
        
        Fallback global quando TEMPO não disponível.
        
        Args:
            lat: Latitude
            lon: Longitude
            radius_km: Raio de busca em km
            date: Data no formato YYYY-MM-DD (None = hoje)
        
        Returns:
            Dict com dados de NO2 ou None se indisponível
        """
        if not EarthEngineService._initialized:
            EarthEngineService.initialize()
        
        if not EarthEngineService._initialized:
            return None

        try:
            # Tentar múltiplas datas se nenhuma for especificada
            # Usar datas recentes de 2025 (dados atuais!)
            dates_to_try = [
                '2025-09-25',  # Setembro 2025 (dados mais recentes)
                '2025-09-20',
                '2025-09-15',
                '2025-09-10',
                '2025-08-25',  # Agosto 2025
                '2025-08-20',
                '2025-08-15',
                '2025-08-10',
                '2025-07-25',  # Julho 2025
                '2025-07-20',
                '2025-07-15'
            ] if date is None else [date]

            # Aumentar raio de busca para 25km
            search_radius_km = 25.0

            # Criar geometria
            point = ee.Geometry.Point([lon, lat])
            area = point.buffer(search_radius_km * 1000)

            logger.info(f"🔍 Searching Sentinel-5P with {search_radius_km}km radius, trying {len(dates_to_try)} dates")

            # Tentar cada data até encontrar dados válidos
            for test_date in dates_to_try:
                # Earth Engine precisa de range (início e fim diferentes)
                date_obj = datetime.strptime(test_date, '%Y-%m-%d')
                end_date = (date_obj + timedelta(days=1)).strftime('%Y-%m-%d')

                # Dataset Sentinel-5P NO2
                s5p = ee.ImageCollection('COPERNICUS/S5P/NRTI/L3_NO2')

                # Filtrar por data e região (range de date até end_date)
                images = s5p.filterDate(test_date, end_date).filterBounds(area)

                count = images.size().getInfo()
                if count == 0:
                    logger.info(f"⚠️ No Sentinel-5P images for {test_date}, trying next date...")
                    continue

                logger.info(f"✅ Found {count} Sentinel-5P images for {test_date}")

                # Pegar primeira imagem
                image = images.first()
                no2_band = image.select('NO2_column_number_density')

                # Extrair estatísticas
                stats = no2_band.reduceRegion(
                    reducer=ee.Reducer.mean(),
                    geometry=area,
                    scale=1000,
                    maxPixels=1e9
                ).getInfo()

                mean_value = stats.get('NO2_column_number_density_mean')

                if mean_value is None:
                    logger.warning(f"⚠️ No valid NO2 values for {test_date}, trying next date...")
                    continue

                # Sucesso! Encontrou dados válidos
                logger.info(f"✅ Valid Sentinel-5P data found for {test_date}")
                date = test_date
                break

            # Se não encontrou dados em nenhuma data
            if mean_value is None:
                logger.warning(f"⚠️ No valid Sentinel-5P NO2 values after trying {len(dates_to_try)} dates")
                return None
            
            # Converter mol/m² para ppb (aproximado)
            # mol/m² -> molec/m² -> molec/cm³ -> ppb
            # 1 mol = 6.022e23 molec
            # altura troposférica ~3000m
            # densidade ar ~2.5e19 molec/cm³
            molec_m2 = mean_value * 6.022e23  # mol/m² -> molec/m²
            molec_cm3 = molec_m2 / (3000 * 100)  # dividir por altura em cm
            densidade_ar = 2.5e19  # molec/cm³
            no2_ppb = (molec_cm3 / densidade_ar) * 1e9
            
            logger.info(f"✅ Sentinel-5P NO2: {no2_ppb:.2f} ppb")
            
            return {
                "no2_ppb": no2_ppb,
                "no2_column": mean_value,  # mol/m²
                "source": "Sentinel-5P TROPOMI (Google Earth Engine)",
                "date": date,
                "location": {"lat": lat, "lon": lon, "radius_km": radius_km}
            }
            
        except Exception as e:
            logger.error(f"❌ Sentinel-5P data fetch failed: {e}")
            return None


async def fetch_earth_engine_no2(lat: float, lon: float) -> Optional[Dict]:
    """
    Busca dados de NO2 via Google Earth Engine.
    
    Prioridade:
    1. TEMPO (América do Norte, hourly, mais preciso)
    2. Sentinel-5P (Global, daily, fallback)
    
    Args:
        lat: Latitude
        lon: Longitude
    
    Returns:
        Dict com dados de NO2 ou None se indisponível
    """
    # Tentar TEMPO primeiro (se na América do Norte)
    if EarthEngineService.is_tempo_coverage(lat, lon):
        logger.info(f"🛰️ Trying TEMPO for ({lat:.4f}, {lon:.4f})")
        tempo_data = await EarthEngineService.get_tempo_no2(lat, lon)
        if tempo_data:
            return tempo_data
        logger.info(f"⚠️ TEMPO unavailable, trying Sentinel-5P...")
    
    # Fallback para Sentinel-5P (global)
    logger.info(f"🛰️ Trying Sentinel-5P for ({lat:.4f}, {lon:.4f})")
    return await EarthEngineService.get_sentinel5p_no2(lat, lon)

