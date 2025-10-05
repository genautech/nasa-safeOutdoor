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
            if date is None:
                date = datetime.utcnow().strftime('%Y-%m-%d')
            
            # Earth Engine precisa de range (início e fim diferentes)
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            end_date = (date_obj + timedelta(days=1)).strftime('%Y-%m-%d')
            
            # Criar geometria (ponto + buffer)
            point = ee.Geometry.Point([lon, lat])
            area = point.buffer(radius_km * 1000)  # km → metros
            
            # Dataset TEMPO NO2 (filtrado por qualidade)
            tempo = ee.ImageCollection('NASA/TEMPO/NO2_L3_QA')
            
            # Filtrar por data e região (range de date até end_date)
            images = tempo.filterDate(date, end_date).filterBounds(area)
            
            # Verificar se há dados
            count = images.size().getInfo()
            if count == 0:
                logger.info(f"⚠️ No TEMPO data for {date} at ({lat:.4f}, {lon:.4f})")
                return None
            
            logger.info(f"✅ Found {count} TEMPO images for {date}")
            
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
                logger.warning(f"⚠️ No valid TEMPO NO2 values in region")
                return None
            
            # Converter molec/cm² para ppb (aproximado)
            # Fator de conversão aproximado para troposfera (~3km)
            no2_ppb = mean_value * 1e-15 * 2.69e10
            
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
            if date is None:
                date = datetime.utcnow().strftime('%Y-%m-%d')
            
            # Earth Engine precisa de range (início e fim diferentes)
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            end_date = (date_obj + timedelta(days=1)).strftime('%Y-%m-%d')
            
            # Criar geometria
            point = ee.Geometry.Point([lon, lat])
            area = point.buffer(radius_km * 1000)
            
            # Dataset Sentinel-5P NO2
            s5p = ee.ImageCollection('COPERNICUS/S5P/NRTI/L3_NO2')
            
            # Filtrar por data e região (range de date até end_date)
            images = s5p.filterDate(date, end_date).filterBounds(area)
            
            count = images.size().getInfo()
            if count == 0:
                logger.info(f"⚠️ No Sentinel-5P data for {date}")
                return None
            
            logger.info(f"✅ Found {count} Sentinel-5P images")
            
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
                return None
            
            # Converter mol/m² para ppb (aproximado)
            # Assumindo altura de coluna troposférica ~3km
            no2_ugm3 = (mean_value * 46.01 * 1e6) / 3000  # μg/m³
            no2_ppb = no2_ugm3 * 0.532  # Fator de conversão aproximado
            
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

