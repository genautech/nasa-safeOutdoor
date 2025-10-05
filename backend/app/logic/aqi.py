"""
Air Quality Index (AQI) calculation utilities.

Implements EPA AQI calculation for multiple pollutants including PM2.5 and NO2.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def calculate_aqi_from_pm25(pm25: float) -> int:
    """
    Convert PM2.5 concentration (μg/m³) to AQI.
    
    Based on EPA AQI breakpoints for PM2.5 (24-hour average).
    
    Args:
        pm25: PM2.5 concentration in micrograms per cubic meter
    
    Returns:
        AQI value (0-500+)
    """
    # EPA PM2.5 breakpoints (μg/m³, 24-hour)
    # Format: (concentration_low, concentration_high, aqi_low, aqi_high)
    breakpoints = [
        (0.0, 12.0, 0, 50),        # Good
        (12.1, 35.4, 51, 100),     # Moderate
        (35.5, 55.4, 101, 150),    # Unhealthy for Sensitive Groups
        (55.5, 150.4, 151, 200),   # Unhealthy
        (150.5, 250.4, 201, 300),  # Very Unhealthy
        (250.5, 500.4, 301, 500),  # Hazardous
    ]
    
    for c_lo, c_hi, i_lo, i_hi in breakpoints:
        if c_lo <= pm25 <= c_hi:
            # Linear interpolation formula
            aqi = ((i_hi - i_lo) / (c_hi - c_lo)) * (pm25 - c_lo) + i_lo
            return round(aqi)
    
    # Off the scale (>500.4 μg/m³)
    if pm25 > 500.4:
        return 500
    
    return 0


def calculate_aqi_from_no2(no2_ppb: float) -> int:
    """
    Convert NO2 concentration (ppb) to AQI.
    
    Based on EPA AQI breakpoints for NO2 (1-hour average).
    
    Args:
        no2_ppb: NO2 concentration in parts per billion
    
    Returns:
        AQI value (0-500+)
    """
    # EPA NO2 breakpoints (ppb, 1-hour)
    # Format: (concentration_low, concentration_high, aqi_low, aqi_high)
    breakpoints = [
        (0, 53, 0, 50),          # Good
        (54, 100, 51, 100),      # Moderate
        (101, 360, 101, 150),    # Unhealthy for Sensitive Groups
        (361, 649, 151, 200),    # Unhealthy
        (650, 1249, 201, 300),   # Very Unhealthy
        (1250, 2049, 301, 500),  # Hazardous
    ]
    
    for c_lo, c_hi, i_lo, i_hi in breakpoints:
        if c_lo <= no2_ppb <= c_hi:
            # Linear interpolation formula
            aqi = ((i_hi - i_lo) / (c_hi - c_lo)) * (no2_ppb - c_lo) + i_lo
            return round(aqi)
    
    # Off the scale (>2049 ppb)
    if no2_ppb > 2049:
        return 500
    
    return 0


def calculate_aqi_from_pollutants(pm25: Optional[float], no2: Optional[float]) -> tuple[int, str]:
    """
    Calculate AQI from available pollutants and return dominant pollutant.
    
    Uses the maximum AQI value from all available pollutants.
    This follows EPA's approach where AQI is determined by the worst pollutant.
    
    Args:
        pm25: PM2.5 concentration in μg/m³ (optional)
        no2: NO2 concentration in ppb (optional)
    
    Returns:
        Tuple of (AQI value, dominant pollutant name)
    """
    aqi_values = []
    
    if pm25 is not None and pm25 >= 0:
        pm25_aqi = calculate_aqi_from_pm25(pm25)
        aqi_values.append((pm25_aqi, "pm25"))
        logger.debug(f"PM2.5: {pm25:.1f} μg/m³ → AQI {pm25_aqi}")
    
    if no2 is not None and no2 >= 0:
        no2_aqi = calculate_aqi_from_no2(no2)
        aqi_values.append((no2_aqi, "no2"))
        logger.debug(f"NO2: {no2:.1f} ppb → AQI {no2_aqi}")
    
    if not aqi_values:
        # No valid pollutants - return conservative estimate
        logger.warning("No valid pollutant data, using default AQI 50")
        return 50, "unknown"
    
    # Return maximum AQI (worst pollutant)
    max_aqi, dominant = max(aqi_values, key=lambda x: x[0])
    logger.info(f"Calculated AQI: {max_aqi} (dominant: {dominant})")
    
    return max_aqi, dominant


def get_aqi_category(aqi: int) -> str:
    """
    Get EPA AQI category name from AQI value.
    
    Args:
        aqi: AQI value (0-500+)
    
    Returns:
        Category name
    """
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Moderate"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    elif aqi <= 200:
        return "Unhealthy"
    elif aqi <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"


def get_aqi_color(aqi: int) -> str:
    """
    Get EPA AQI color code from AQI value.
    
    Args:
        aqi: AQI value (0-500+)
    
    Returns:
        Hex color code
    """
    if aqi <= 50:
        return "#00E400"  # Green
    elif aqi <= 100:
        return "#FFFF00"  # Yellow
    elif aqi <= 150:
        return "#FF7E00"  # Orange
    elif aqi <= 200:
        return "#FF0000"  # Red
    elif aqi <= 300:
        return "#8F3F97"  # Purple
    else:
        return "#7E0023"  # Maroon


__all__ = [
    'calculate_aqi_from_pm25',
    'calculate_aqi_from_no2',
    'calculate_aqi_from_pollutants',
    'get_aqi_category',
    'get_aqi_color'
]
