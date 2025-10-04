"""Risk score calculation logic."""
import logging
from typing import Optional, Dict, List, Any

logger = logging.getLogger(__name__)


def calculate_safety_score(data: dict) -> dict:
    """
    Calculate overall safety score (0-10) based on multiple factors.
    
    Input data:
    {
        "activity": str,
        "aqi": int,
        "pm25": float,
        "no2": float,
        "weather": {...},
        "elevation": int,
        "uv_index": float
    }
    
    Returns:
    {
        "score": float (0-10),
        "category": str ("Excellent" | "Good" | "Moderate" | "Poor"),
        "risk_factors": [
            {"factor": "Air Quality", "score": 9, "weight": 0.35},
            ...
        ],
        "warnings": ["High UV - sunscreen required", ...]
    }
    """
    # Weights
    AIR_QUALITY_WEIGHT = 0.35
    WEATHER_WEIGHT = 0.25
    UV_WEIGHT = 0.15
    TERRAIN_WEIGHT = 0.15
    ACTIVITY_ADJUSTMENT = 0.10
    
    # Calculate sub-scores (0-10 scale)
    air_score = calculate_air_quality_score(data.get("aqi", 50), data.get("pm25", 15.0))
    weather_score = calculate_weather_score(data.get("weather", {}))
    uv_score = calculate_uv_score(data.get("uv_index", 5.0))
    terrain_score = calculate_terrain_score(data.get("elevation", 0), data.get("activity", "hiking"))
    
    # Weighted average
    total = (
        air_score * AIR_QUALITY_WEIGHT +
        weather_score * WEATHER_WEIGHT +
        uv_score * UV_WEIGHT +
        terrain_score * TERRAIN_WEIGHT
    )
    
    # Activity-specific adjustments
    activity = data.get("activity", "").lower()
    activity_modifier = get_activity_modifier(activity, data)
    total = total * (1.0 + activity_modifier)
    
    # Clamp to 0-10 range
    total = max(0.0, min(10.0, total))
    
    # Determine category
    if total >= 8.5:
        category = "Excellent"
    elif total >= 7.0:
        category = "Good"
    elif total >= 5.0:
        category = "Moderate"
    elif total >= 3.0:
        category = "Poor"
    else:
        category = "Dangerous"
    
    # Generate warnings
    warnings = generate_warnings(data)
    
    # Build risk factors breakdown
    risk_factors = [
        {"factor": "Air Quality", "score": round(air_score, 1), "weight": AIR_QUALITY_WEIGHT},
        {"factor": "Weather", "score": round(weather_score, 1), "weight": WEATHER_WEIGHT},
        {"factor": "UV Exposure", "score": round(uv_score, 1), "weight": UV_WEIGHT},
        {"factor": "Terrain", "score": round(terrain_score, 1), "weight": TERRAIN_WEIGHT}
    ]
    
    result = {
        "score": round(total, 1),
        "category": category,
        "risk_factors": risk_factors,
        "warnings": warnings
    }
    
    logger.info(f"Safety score: {result['score']}/10 ({category}) for {activity}")
    return result


def calculate_air_quality_score(aqi: int, pm25: float) -> float:
    """
    Calculate air quality sub-score (0-10).
    
    AQI Scale:
    0-50: Good (score 9-10)
    51-100: Moderate (score 7-8.9)
    101-150: Unhealthy for sensitive (score 5-6.9)
    151-200: Unhealthy (score 3-4.9)
    201-300: Very unhealthy (score 1-2.9)
    300+: Hazardous (score 0-0.9)
    """
    if aqi <= 50:
        # Linear scale from 9 to 10
        return 9.0 + (50 - aqi) / 50.0
    elif aqi <= 100:
        # Linear scale from 7 to 8.9
        return 7.0 + (100 - aqi) / 50.0 * 1.9
    elif aqi <= 150:
        # Linear scale from 5 to 6.9
        return 5.0 + (150 - aqi) / 50.0 * 1.9
    elif aqi <= 200:
        # Linear scale from 3 to 4.9
        return 3.0 + (200 - aqi) / 50.0 * 1.9
    elif aqi <= 300:
        # Linear scale from 1 to 2.9
        return 1.0 + (300 - aqi) / 100.0 * 1.9
    else:
        # Hazardous: 0-0.9
        return max(0.0, 0.9 - (aqi - 300) / 200.0)


def calculate_weather_score(weather: dict) -> float:
    """
    Calculate weather conditions sub-score (0-10).
    
    Considers: temperature, wind speed, precipitation, humidity
    """
    score = 10.0
    
    temp_c = weather.get("temp_c", weather.get("temp", 20))
    wind_speed_kmh = weather.get("wind_speed_kmh", weather.get("wind_speed", 10))
    precipitation_mm = weather.get("precipitation_mm", 0)
    humidity = weather.get("humidity", 50)
    
    # Temperature penalty (ideal: 15-25°C)
    if temp_c < -10:
        score -= 4.0  # Extreme cold
    elif temp_c < 0:
        score -= 2.5
    elif temp_c < 10:
        score -= 1.5
    elif temp_c > 40:
        score -= 4.0  # Extreme heat
    elif temp_c > 35:
        score -= 3.0
    elif temp_c > 30:
        score -= 1.5
    
    # Wind penalty
    if wind_speed_kmh > 60:
        score -= 3.0  # Dangerous winds
    elif wind_speed_kmh > 40:
        score -= 2.0
    elif wind_speed_kmh > 25:
        score -= 1.0
    
    # Precipitation penalty
    if precipitation_mm > 50:
        score -= 3.0  # Heavy rain
    elif precipitation_mm > 20:
        score -= 2.0
    elif precipitation_mm > 5:
        score -= 1.0
    
    # Humidity penalty (extreme values)
    if humidity > 90:
        score -= 1.0  # Very humid
    elif humidity < 20:
        score -= 1.0  # Very dry
    
    return max(0.0, min(10.0, score))


def calculate_uv_score(uv_index: float) -> float:
    """
    Calculate UV exposure sub-score (0-10).
    
    UV Index Scale:
    0-2: Low (score 10)
    3-5: Moderate (score 8-9)
    6-7: High (score 6-7)
    8-10: Very high (score 4-5)
    11+: Extreme (score 0-3)
    """
    if uv_index <= 2:
        return 10.0
    elif uv_index <= 5:
        # Linear from 8 to 10
        return 8.0 + (5 - uv_index) / 3.0 * 2.0
    elif uv_index <= 7:
        # Linear from 6 to 8
        return 6.0 + (7 - uv_index) / 2.0 * 2.0
    elif uv_index <= 10:
        # Linear from 4 to 6
        return 4.0 + (10 - uv_index) / 3.0 * 2.0
    else:
        # Extreme: 0-4
        return max(0.0, 4.0 - (uv_index - 10) / 3.0)


def calculate_terrain_score(elevation: int, activity: str) -> float:
    """
    Calculate terrain difficulty sub-score (0-10).
    
    Considers elevation and activity type.
    """
    score = 10.0
    
    # Elevation effects (altitude sickness risk)
    if elevation > 4000:
        score -= 4.0  # Very high altitude
    elif elevation > 3000:
        score -= 2.5
    elif elevation > 2500:
        score -= 1.5
    elif elevation > 2000:
        score -= 0.5
    
    # Activity-specific terrain difficulty
    activity = activity.lower()
    
    if activity in ["mountaineering", "rock_climbing", "alpinism"]:
        # More tolerant of high elevation
        score += 1.0
        if elevation > 3000:
            score -= 0.5  # But still penalize extreme altitude
    elif activity in ["trail_running", "running"]:
        # More sensitive to elevation changes
        if elevation > 2000:
            score -= 1.5
    
    return max(0.0, min(10.0, score))


def get_activity_modifier(activity: str, data: dict) -> float:
    """
    Get activity-specific score modifier (-0.2 to +0.2).
    
    Adjusts final score based on activity tolerance to conditions.
    """
    modifier = 0.0
    aqi = data.get("aqi", 50)
    temp = data.get("weather", {}).get("temp_c", 20)
    
    activity = activity.lower()
    
    # Aerobic activities more sensitive to air quality
    if activity in ["running", "cycling", "trail_running"]:
        if aqi > 100:
            modifier -= 0.15  # Penalize poor air quality more
        if temp > 30:
            modifier -= 0.1   # Penalize high heat more
    
    # Technical activities more sensitive to weather
    elif activity in ["rock_climbing", "mountaineering", "alpinism"]:
        wind = data.get("weather", {}).get("wind_speed_kmh", 10)
        if wind > 30:
            modifier -= 0.2  # Wind very dangerous for climbing
    
    # Hiking is generally more tolerant
    elif activity in ["hiking", "trekking", "backpacking"]:
        if aqi < 150 and temp < 35:
            modifier += 0.05  # Slightly more tolerant
    
    # Water activities
    elif activity in ["kayaking", "canoeing", "paddleboarding"]:
        wind = data.get("weather", {}).get("wind_speed_kmh", 10)
        if wind > 25:
            modifier -= 0.2  # Wind very dangerous on water
    
    return max(-0.2, min(0.2, modifier))


def generate_warnings(data: dict) -> List[str]:
    """Generate specific warnings based on conditions."""
    warnings = []
    
    aqi = data.get("aqi", 50)
    pm25 = data.get("pm25", 15.0)
    uv_index = data.get("uv_index", 5.0)
    weather = data.get("weather", {})
    elevation = data.get("elevation", 0)
    activity = data.get("activity", "").lower()
    
    # Air quality warnings
    if aqi > 200:
        warnings.append("⚠️ Air quality is hazardous - outdoor activity not recommended")
    elif aqi > 150:
        warnings.append("⚠️ Air quality unhealthy - limit outdoor exposure and take frequent breaks")
    elif aqi > 100:
        warnings.append("⚠️ Air quality unhealthy for sensitive groups - consider N95 mask")
    
    if pm25 > 35:
        warnings.append("⚠️ High particulate matter - respiratory protection recommended")
    
    # UV warnings
    if uv_index >= 11:
        warnings.append("☀️ Extreme UV - minimize sun exposure, full protection required")
    elif uv_index >= 8:
        warnings.append("☀️ Very high UV - sunscreen SPF 50+, hat, and protective clothing required")
    elif uv_index >= 6:
        warnings.append("☀️ High UV - sunscreen and hat recommended")
    
    # Weather warnings
    temp = weather.get("temp_c", 20)
    if temp > 38:
        warnings.append("🌡️ Extreme heat warning - high risk of heat stroke")
    elif temp > 32:
        warnings.append("🌡️ High temperature - stay hydrated, take frequent breaks in shade")
    elif temp < -15:
        warnings.append("❄️ Extreme cold - risk of frostbite and hypothermia")
    elif temp < 0:
        warnings.append("❄️ Below freezing - dress in layers, protect extremities")
    
    wind = weather.get("wind_speed_kmh", 10)
    if wind > 60:
        warnings.append("💨 Dangerous wind speeds - outdoor activities extremely hazardous")
    elif wind > 40:
        warnings.append("💨 High winds - exercise extreme caution, especially on exposed terrain")
    elif wind > 25:
        warnings.append("💨 Moderate winds - be cautious on ridges and exposed areas")
    
    precip = weather.get("precipitation_mm", 0)
    if precip > 50:
        warnings.append("🌧️ Heavy precipitation forecast - trail conditions may be hazardous")
    elif precip > 20:
        warnings.append("🌧️ Moderate rain expected - bring waterproof gear")
    
    # Elevation warnings
    if elevation > 4000:
        warnings.append("⛰️ Very high altitude - risk of altitude sickness, acclimatize gradually")
    elif elevation > 3000:
        warnings.append("⛰️ High altitude - monitor for symptoms of altitude sickness")
    elif elevation > 2500:
        warnings.append("⛰️ Moderate altitude - stay hydrated and pace yourself")
    
    # Activity-specific warnings
    if activity in ["running", "cycling", "trail_running"] and aqi > 100:
        warnings.append("🏃 Aerobic activity with poor air quality - consider indoor alternative")
    
    if activity in ["rock_climbing", "mountaineering"] and wind > 30:
        warnings.append("🧗 Climbing in high winds is dangerous - consider postponing")
    
    return warnings


class RiskScoreCalculator:
    """Calculate safety scores based on environmental conditions (legacy class wrapper)."""
    
    # Weight factors for different metrics (total = 1.0)
    WEIGHTS = {
        "air_quality": 0.35,
        "weather": 0.25,
        "uv_exposure": 0.15,
        "visibility": 0.10,
        "wildfire": 0.10,
        "elevation": 0.05
    }
    
    def calculate_safety_score(
        self,
        air_quality_data: dict,
        weather_data: dict,
        satellite_data: dict,
        elevation_data: dict,
        activity: str
    ) -> dict:
        """
        Calculate overall safety score (0-100).
        
        Args:
            air_quality_data: AQ metrics (AQI, PM2.5, NO2, etc.)
            weather_data: Weather conditions
            satellite_data: Satellite imagery data
            elevation_data: Elevation and terrain
            activity: Activity type (affects weights)
            
        Returns:
            dict: Safety score, risk level, and component scores
        """
        logger.info(f"Calculating safety score for activity: {activity}")
        
        # Calculate component scores (each 0-100)
        aq_score = self._score_air_quality(air_quality_data)
        weather_score = self._score_weather(weather_data, activity)
        uv_score = self._score_uv_exposure(satellite_data)
        visibility_score = self._score_visibility(satellite_data, weather_data)
        wildfire_score = self._score_wildfire_risk(satellite_data)
        elevation_score = self._score_elevation(elevation_data)
        
        # TODO: Adjust weights based on activity type
        weights = self._adjust_weights_for_activity(activity)
        
        # Calculate weighted overall score
        overall_score = (
            aq_score * weights["air_quality"] +
            weather_score * weights["weather"] +
            uv_score * weights["uv_exposure"] +
            visibility_score * weights["visibility"] +
            wildfire_score * weights["wildfire"] +
            elevation_score * weights["elevation"]
        )
        
        # Determine risk level
        risk_level = self._determine_risk_level(overall_score)
        
        result = {
            "safety_score": int(overall_score),
            "risk_level": risk_level,
            "component_scores": {
                "air_quality": aq_score,
                "weather": weather_score,
                "uv_exposure": uv_score,
                "visibility": visibility_score,
                "wildfire_risk": wildfire_score,
                "elevation": elevation_score
            }
        }
        
        logger.info(f"Safety score: {int(overall_score)} ({risk_level})")
        return result
    
    def _score_air_quality(self, data: dict) -> float:
        """Score air quality (100 = excellent, 0 = hazardous)."""
        aqi = data.get("aqi", 50)
        
        # AQI scale: 0-50 (good), 51-100 (moderate), 101-150 (unhealthy for sensitive groups),
        # 151-200 (unhealthy), 201-300 (very unhealthy), 301+ (hazardous)
        
        if aqi <= 50:
            return 100 - (aqi * 0.2)  # 100-90
        elif aqi <= 100:
            return 90 - ((aqi - 50) * 1.0)  # 90-40
        elif aqi <= 150:
            return 40 - ((aqi - 100) * 0.5)  # 40-15
        elif aqi <= 200:
            return 15 - ((aqi - 150) * 0.2)  # 15-5
        else:
            return max(0, 5 - ((aqi - 200) * 0.05))  # 5-0
    
    def _score_weather(self, data: dict, activity: str) -> float:
        """Score weather conditions based on activity."""
        # TODO: Implement weather scoring logic
        temp = data.get("temp", 70)
        wind_speed = data.get("wind_speed", 5)
        humidity = data.get("humidity", 50)
        
        score = 100.0
        
        # Temperature penalty (ideal range: 50-80°F)
        if temp < 32:
            score -= 50
        elif temp < 50:
            score -= (50 - temp) * 0.5
        elif temp > 95:
            score -= (temp - 95) * 2
        elif temp > 80:
            score -= (temp - 80) * 0.5
        
        # Wind penalty (varies by activity)
        if wind_speed > 25:
            score -= 30
        elif wind_speed > 15:
            score -= (wind_speed - 15) * 1.5
        
        return max(0, min(100, score))
    
    def _score_uv_exposure(self, data: dict) -> float:
        """Score UV exposure risk."""
        # TODO: Extract UV index from satellite data
        uv_index = data.get("goes16", {}).get("uv_index", 5)
        
        if uv_index <= 2:
            return 100
        elif uv_index <= 5:
            return 90 - ((uv_index - 2) * 5)
        elif uv_index <= 7:
            return 75 - ((uv_index - 5) * 10)
        elif uv_index <= 10:
            return 55 - ((uv_index - 7) * 10)
        else:
            return max(0, 25 - ((uv_index - 10) * 5))
    
    def _score_visibility(self, satellite_data: dict, weather_data: dict) -> float:
        """Score visibility conditions."""
        visibility_km = weather_data.get("visibility", 10)
        
        if visibility_km >= 10:
            return 100
        elif visibility_km >= 5:
            return 80 + (visibility_km - 5) * 4
        elif visibility_km >= 2:
            return 50 + (visibility_km - 2) * 10
        else:
            return visibility_km * 25
    
    def _score_wildfire_risk(self, data: dict) -> float:
        """Score wildfire risk from FIRMS data."""
        firms = data.get("firms", {})
        active_fires = firms.get("activeFiresNearby", False)
        
        if active_fires:
            distance = firms.get("nearestFireDistance", 100)
            if distance < 10:
                return 0  # Very dangerous
            elif distance < 50:
                return 30
            else:
                return 70
        
        return 100  # No fires detected
    
    def _score_elevation(self, data: dict) -> float:
        """Score elevation/altitude effects."""
        elevation_m = data.get("elevation_m", 0)
        
        if elevation_m < 1500:
            return 100
        elif elevation_m < 2500:
            return 90
        elif elevation_m < 3500:
            return 75
        else:
            return 50
    
    def _adjust_weights_for_activity(self, activity: str) -> dict:
        """Adjust scoring weights based on activity type."""
        weights = self.WEIGHTS.copy()
        
        # TODO: Customize weights per activity
        if activity.lower() in ["running", "cycling"]:
            weights["air_quality"] = 0.40
            weights["weather"] = 0.30
        elif activity.lower() in ["hiking", "mountaineering"]:
            weights["elevation"] = 0.10
            weights["visibility"] = 0.15
        
        return weights
    
    def _determine_risk_level(self, score: float) -> str:
        """Convert score to risk level category."""
        if score >= 80:
            return "low"
        elif score >= 60:
            return "moderate"
        elif score >= 40:
            return "high"
        else:
            return "very_high"
