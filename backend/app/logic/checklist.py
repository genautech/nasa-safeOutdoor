"""Gear checklist generation logic."""
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


def generate_checklist(activity: str, risk_data: dict, weather: dict) -> list:
    """
    Generate gear/preparation checklist based on conditions.
    
    Args:
        activity: Activity type (hiking, camping, cycling, etc.)
        risk_data: Risk analysis data (aqi, pm25, uv_index, etc.)
        weather: Weather conditions (temp, wind, precipitation, etc.)
    
    Returns:
        List of checklist items:
        [
            {
                "item": "Water (3L minimum)",
                "required": true,
                "reason": "High temperatures forecast",
                "category": "hydration"
            },
            ...
        ]
    """
    activity = activity.lower()
    
    # Get base checklist for activity
    base_items = get_base_checklist(activity)
    checklist = list(base_items)
    
    # Extract conditions
    aqi = risk_data.get("aqi", 50)
    pm25 = risk_data.get("pm25", 15.0)
    uv_index = risk_data.get("uv_index", 5.0)
    elevation = risk_data.get("elevation", 0)
    
    temp_c = weather.get("temp_c", weather.get("temp", 20))
    wind_speed = weather.get("wind_speed_kmh", weather.get("wind_speed", 10))
    precipitation = weather.get("precipitation_mm", 0)
    humidity = weather.get("humidity", 50)
    
    # Add conditional items based on conditions
    
    # === Air Quality Items ===
    if aqi > 150:
        checklist.append({
            "item": "N95 or P100 respirator mask",
            "required": True,
            "reason": f"Air quality is unhealthy (AQI {aqi})",
            "category": "respiratory"
        })
    elif aqi > 100:
        checklist.append({
            "item": "N95 mask (especially for sensitive individuals)",
            "required": False,
            "reason": f"Air quality is moderate to unhealthy (AQI {aqi})",
            "category": "respiratory"
        })
    
    if aqi > 150:
        checklist.append({
            "item": "Eye drops or protective eyewear",
            "required": False,
            "reason": "Poor air quality can irritate eyes",
            "category": "respiratory"
        })
    
    # === Temperature Items ===
    if temp_c > 35:
        checklist.extend([
            {
                "item": "Extra water (4-6L minimum)",
                "required": True,
                "reason": f"Extreme heat forecast ({temp_c}°C)",
                "category": "hydration"
            },
            {
                "item": "Electrolyte tablets or sports drinks",
                "required": True,
                "reason": "High risk of dehydration and electrolyte loss",
                "category": "hydration"
            },
            {
                "item": "Cooling towel or bandana",
                "required": False,
                "reason": "Helps manage body temperature",
                "category": "clothing"
            },
            {
                "item": "Wide-brimmed hat",
                "required": True,
                "reason": "Protection from intense sun",
                "category": "clothing"
            }
        ])
    elif temp_c > 30:
        checklist.extend([
            {
                "item": "Extra water (3L minimum)",
                "required": True,
                "reason": f"High temperatures forecast ({temp_c}°C)",
                "category": "hydration"
            },
            {
                "item": "Hat with sun protection",
                "required": True,
                "reason": "Prevent heat exhaustion",
                "category": "clothing"
            }
        ])
    
    if temp_c < -10:
        checklist.extend([
            {
                "item": "Insulated winter jacket (down or synthetic)",
                "required": True,
                "reason": f"Extreme cold forecast ({temp_c}°C)",
                "category": "clothing"
            },
            {
                "item": "Winter gloves (with liners)",
                "required": True,
                "reason": "Prevent frostbite",
                "category": "clothing"
            },
            {
                "item": "Balaclava or face mask",
                "required": True,
                "reason": "Protect face from freezing temperatures",
                "category": "clothing"
            },
            {
                "item": "Insulated boots (rated for temperature)",
                "required": True,
                "reason": "Prevent frostbite on feet",
                "category": "clothing"
            },
            {
                "item": "Emergency bivouac sack",
                "required": True,
                "reason": "Emergency shelter in extreme cold",
                "category": "safety"
            }
        ])
    elif temp_c < 0:
        checklist.extend([
            {
                "item": "Winter jacket and layers",
                "required": True,
                "reason": f"Below freezing temperatures ({temp_c}°C)",
                "category": "clothing"
            },
            {
                "item": "Gloves and warm hat",
                "required": True,
                "reason": "Protect extremities from cold",
                "category": "clothing"
            },
            {
                "item": "Hand warmers",
                "required": False,
                "reason": "Additional warmth for hands",
                "category": "comfort"
            }
        ])
    elif temp_c < 10:
        checklist.extend([
            {
                "item": "Light jacket or fleece",
                "required": True,
                "reason": f"Cool temperatures ({temp_c}°C)",
                "category": "clothing"
            },
            {
                "item": "Long sleeves base layer",
                "required": False,
                "reason": "Layering for warmth",
                "category": "clothing"
            }
        ])
    
    # === UV Protection ===
    if uv_index >= 11:
        checklist.extend([
            {
                "item": "Sunscreen SPF 50+ (reapply every 2 hours)",
                "required": True,
                "reason": f"Extreme UV index ({uv_index})",
                "category": "sun_protection"
            },
            {
                "item": "UV-blocking sunglasses",
                "required": True,
                "reason": "Protect eyes from intense UV",
                "category": "sun_protection"
            },
            {
                "item": "Sun-protective clothing (UPF 50+)",
                "required": True,
                "reason": "Minimize skin exposure to UV",
                "category": "clothing"
            },
            {
                "item": "Lip balm with SPF",
                "required": False,
                "reason": "Protect lips from sun damage",
                "category": "sun_protection"
            }
        ])
    elif uv_index >= 8:
        checklist.extend([
            {
                "item": "Sunscreen SPF 50+",
                "required": True,
                "reason": f"Very high UV index ({uv_index})",
                "category": "sun_protection"
            },
            {
                "item": "Sunglasses with UV protection",
                "required": True,
                "reason": "Protect eyes from UV damage",
                "category": "sun_protection"
            },
            {
                "item": "Hat with brim or neck flap",
                "required": True,
                "reason": "Shield face and neck from sun",
                "category": "clothing"
            }
        ])
    elif uv_index >= 6:
        checklist.append({
            "item": "Sunscreen SPF 30+",
            "required": True,
            "reason": f"High UV index ({uv_index})",
            "category": "sun_protection"
        })
    
    # === Wind Protection ===
    if wind_speed > 60:
        checklist.extend([
            {
                "item": "Sturdy windproof shell jacket",
                "required": True,
                "reason": f"Dangerous wind speeds ({wind_speed} km/h)",
                "category": "clothing"
            },
            {
                "item": "Goggles or protective eyewear",
                "required": True,
                "reason": "Protect eyes from wind and debris",
                "category": "safety"
            }
        ])
    elif wind_speed > 40:
        checklist.append({
            "item": "Windproof jacket",
            "required": True,
            "reason": f"High winds forecast ({wind_speed} km/h)",
            "category": "clothing"
        })
    elif wind_speed > 25:
        checklist.append({
            "item": "Light windbreaker",
            "required": False,
            "reason": f"Moderate winds ({wind_speed} km/h)",
            "category": "clothing"
        })
    
    # === Rain Protection ===
    if precipitation > 50:
        checklist.extend([
            {
                "item": "Waterproof rain jacket and pants",
                "required": True,
                "reason": f"Heavy rain forecast ({precipitation}mm)",
                "category": "rain_gear"
            },
            {
                "item": "Waterproof backpack cover or dry bags",
                "required": True,
                "reason": "Protect gear from getting soaked",
                "category": "rain_gear"
            },
            {
                "item": "Extra dry clothes in waterproof bag",
                "required": True,
                "reason": "Change if primary clothes get wet",
                "category": "clothing"
            },
            {
                "item": "Waterproof boots or gaiters",
                "required": True,
                "reason": "Keep feet dry",
                "category": "rain_gear"
            }
        ])
    elif precipitation > 20:
        checklist.extend([
            {
                "item": "Rain jacket",
                "required": True,
                "reason": f"Moderate rain forecast ({precipitation}mm)",
                "category": "rain_gear"
            },
            {
                "item": "Waterproof backpack cover",
                "required": False,
                "reason": "Protect gear from rain",
                "category": "rain_gear"
            }
        ])
    elif precipitation > 5:
        checklist.append({
            "item": "Light rain jacket",
            "required": False,
            "reason": f"Light rain possible ({precipitation}mm)",
            "category": "rain_gear"
        })
    
    # === Elevation Items ===
    if elevation > 4000:
        checklist.extend([
            {
                "item": "Altitude sickness medication (Diamox)",
                "required": True,
                "reason": f"Very high altitude ({elevation}m)",
                "category": "medical"
            },
            {
                "item": "Pulse oximeter",
                "required": False,
                "reason": "Monitor oxygen saturation",
                "category": "medical"
            },
            {
                "item": "Extra high-energy snacks",
                "required": True,
                "reason": "Body burns more calories at high altitude",
                "category": "nutrition"
            }
        ])
    elif elevation > 3000:
        checklist.append({
            "item": "Altitude sickness medication (optional)",
            "required": False,
            "reason": f"High altitude ({elevation}m)",
            "category": "medical"
        })
    
    # === Activity-Specific Additions ===
    if activity in ["running", "trail_running", "cycling"] and aqi > 100:
        checklist.append({
            "item": "Consider indoor alternative",
            "required": False,
            "reason": "Aerobic activity in poor air quality is hazardous",
            "category": "safety"
        })
    
    if activity in ["rock_climbing", "mountaineering"] and wind_speed > 40:
        checklist.append({
            "item": "Consider postponing activity",
            "required": False,
            "reason": "Climbing in high winds is extremely dangerous",
            "category": "safety"
        })
    
    # === General Safety Items ===
    if temp_c > 32 or temp_c < -5 or aqi > 150:
        checklist.append({
            "item": "Emergency communication device (satellite phone/PLB)",
            "required": False,
            "reason": "Hazardous conditions increase emergency risk",
            "category": "safety"
        })
    
    # Remove duplicates (keep first occurrence)
    seen_items = set()
    unique_checklist = []
    for item in checklist:
        item_name = item["item"].lower()
        if item_name not in seen_items:
            seen_items.add(item_name)
            unique_checklist.append(item)
    
    # Sort: required first, then by category
    sorted_checklist = sorted(
        unique_checklist,
        key=lambda x: (not x["required"], x["category"], x["item"])
    )
    
    logger.info(f"Generated checklist with {len(sorted_checklist)} items for {activity}")
    return sorted_checklist


def get_base_checklist(activity: str) -> List[Dict]:
    """Get base checklist for specific activity."""
    
    BASE_CHECKLISTS = {
        "hiking": [
            {"item": "Hiking boots or trail shoes", "required": True, "reason": "Proper footwear for terrain", "category": "clothing"},
            {"item": "Backpack (20-30L)", "required": True, "reason": "Carry gear and supplies", "category": "gear"},
            {"item": "Water (2L minimum)", "required": True, "reason": "Stay hydrated", "category": "hydration"},
            {"item": "Trail map or GPS device", "required": True, "reason": "Navigation", "category": "navigation"},
            {"item": "First aid kit", "required": True, "reason": "Emergency medical care", "category": "medical"},
            {"item": "Sunscreen", "required": True, "reason": "Sun protection", "category": "sun_protection"},
            {"item": "Snacks or energy bars", "required": True, "reason": "Maintain energy levels", "category": "nutrition"},
            {"item": "Whistle", "required": False, "reason": "Emergency signaling", "category": "safety"},
            {"item": "Headlamp or flashlight", "required": False, "reason": "If return after dark", "category": "safety"},
            {"item": "Trekking poles", "required": False, "reason": "Stability and reduced joint impact", "category": "gear"}
        ],
        
        "trail_running": [
            {"item": "Trail running shoes", "required": True, "reason": "Proper footwear for terrain", "category": "clothing"},
            {"item": "Hydration vest or handheld bottle", "required": True, "reason": "Stay hydrated while moving", "category": "hydration"},
            {"item": "Phone with emergency contacts", "required": True, "reason": "Emergency communication", "category": "safety"},
            {"item": "Energy gels or chews", "required": True, "reason": "Quick energy during run", "category": "nutrition"},
            {"item": "Sunscreen", "required": True, "reason": "Sun protection", "category": "sun_protection"},
            {"item": "Basic first aid supplies", "required": False, "reason": "Treat minor injuries", "category": "medical"},
            {"item": "Whistle", "required": False, "reason": "Emergency signaling", "category": "safety"}
        ],
        
        "running": [
            {"item": "Running shoes", "required": True, "reason": "Proper footwear", "category": "clothing"},
            {"item": "Water bottle", "required": True, "reason": "Hydration", "category": "hydration"},
            {"item": "Phone", "required": True, "reason": "Emergency communication", "category": "safety"},
            {"item": "Sunscreen", "required": True, "reason": "Sun protection", "category": "sun_protection"}
        ],
        
        "cycling": [
            {"item": "Helmet", "required": True, "reason": "Head protection (legal requirement)", "category": "safety"},
            {"item": "Water bottles (2x)", "required": True, "reason": "Stay hydrated", "category": "hydration"},
            {"item": "Bike repair kit (tire levers, patches)", "required": True, "reason": "Fix flat tires", "category": "gear"},
            {"item": "Spare tube", "required": True, "reason": "Quick tire replacement", "category": "gear"},
            {"item": "Pump or CO2 inflator", "required": True, "reason": "Inflate repaired tire", "category": "gear"},
            {"item": "Multi-tool", "required": True, "reason": "Bike adjustments", "category": "gear"},
            {"item": "Sunscreen", "required": True, "reason": "Sun protection", "category": "sun_protection"},
            {"item": "Sunglasses", "required": False, "reason": "Eye protection and visibility", "category": "sun_protection"},
            {"item": "Phone", "required": True, "reason": "Emergency communication", "category": "safety"},
            {"item": "Energy bars", "required": False, "reason": "Maintain energy on long rides", "category": "nutrition"}
        ],
        
        "camping": [
            {"item": "Tent with rain fly", "required": True, "reason": "Shelter", "category": "shelter"},
            {"item": "Sleeping bag (temperature rated)", "required": True, "reason": "Warmth at night", "category": "shelter"},
            {"item": "Sleeping pad or mattress", "required": True, "reason": "Insulation and comfort", "category": "shelter"},
            {"item": "Camping stove and fuel", "required": True, "reason": "Cook meals", "category": "cooking"},
            {"item": "Cookware and utensils", "required": True, "reason": "Prepare and eat food", "category": "cooking"},
            {"item": "Food (planned meals)", "required": True, "reason": "Nutrition", "category": "nutrition"},
            {"item": "Water filter or purification tablets", "required": True, "reason": "Safe drinking water", "category": "hydration"},
            {"item": "Water containers (3L+)", "required": True, "reason": "Water storage", "category": "hydration"},
            {"item": "Headlamp with extra batteries", "required": True, "reason": "Night visibility", "category": "safety"},
            {"item": "First aid kit (comprehensive)", "required": True, "reason": "Medical emergencies", "category": "medical"},
            {"item": "Multi-tool or knife", "required": True, "reason": "Various tasks", "category": "gear"},
            {"item": "Fire starter (matches/lighter)", "required": True, "reason": "Cooking and warmth", "category": "gear"},
            {"item": "Trash bags", "required": True, "reason": "Leave no trace", "category": "gear"},
            {"item": "Bear canister or bag (if required)", "required": False, "reason": "Food storage in bear country", "category": "safety"}
        ],
        
        "rock_climbing": [
            {"item": "Climbing shoes", "required": True, "reason": "Footwork and grip", "category": "clothing"},
            {"item": "Harness", "required": True, "reason": "Safety system", "category": "safety"},
            {"item": "Helmet", "required": True, "reason": "Head protection from falls/rockfall", "category": "safety"},
            {"item": "Rope (appropriate length/type)", "required": True, "reason": "Protection system", "category": "safety"},
            {"item": "Belay device", "required": True, "reason": "Control rope during belay", "category": "safety"},
            {"item": "Carabiners (locking and non-locking)", "required": True, "reason": "Connect protection", "category": "safety"},
            {"item": "Quickdraws (6-12)", "required": True, "reason": "Clip rope to protection", "category": "safety"},
            {"item": "Chalk bag", "required": False, "reason": "Hand grip", "category": "gear"},
            {"item": "First aid kit", "required": True, "reason": "Emergency medical care", "category": "medical"},
            {"item": "Water (2L+)", "required": True, "reason": "Hydration", "category": "hydration"}
        ],
        
        "mountaineering": [
            {"item": "Mountaineering boots (crampon-compatible)", "required": True, "reason": "Protect feet in harsh conditions", "category": "clothing"},
            {"item": "Crampons", "required": True, "reason": "Ice and snow traction", "category": "gear"},
            {"item": "Ice axe", "required": True, "reason": "Self-arrest and climbing", "category": "gear"},
            {"item": "Helmet", "required": True, "reason": "Rockfall and ice fall protection", "category": "safety"},
            {"item": "Harness and rope", "required": True, "reason": "Glacier travel and protection", "category": "safety"},
            {"item": "Insulated jacket (down or synthetic)", "required": True, "reason": "Warmth at altitude", "category": "clothing"},
            {"item": "Layers (base, mid, shell)", "required": True, "reason": "Temperature regulation", "category": "clothing"},
            {"item": "Goggles and sunglasses", "required": True, "reason": "Snow blindness prevention", "category": "sun_protection"},
            {"item": "Sunscreen SPF 50+", "required": True, "reason": "UV reflection from snow", "category": "sun_protection"},
            {"item": "Headlamp", "required": True, "reason": "Early starts and emergencies", "category": "safety"},
            {"item": "Emergency bivouac gear", "required": True, "reason": "Unexpected night out", "category": "safety"},
            {"item": "First aid kit (comprehensive)", "required": True, "reason": "Medical emergencies", "category": "medical"},
            {"item": "Water (3L+) and insulated bottle", "required": True, "reason": "Prevent freezing", "category": "hydration"}
        ]
    }
    
    return BASE_CHECKLISTS.get(activity.lower(), BASE_CHECKLISTS["hiking"])


class ChecklistGenerator:
    """Generate activity-specific gear checklists based on conditions (legacy class wrapper)."""
    
    # Base checklists per activity
    BASE_CHECKLISTS = {
        "hiking": ["Hiking boots", "Backpack", "Water bottle", "Trail map", "First aid kit", "Sunscreen"],
        "cycling": ["Helmet", "Water bottles", "Bike repair kit", "Spare tube", "Pump", "Sunscreen"],
        "running": ["Running shoes", "Water bottle", "Phone", "Sunscreen"],
        "camping": ["Tent", "Sleeping bag", "Sleeping pad", "Camping stove", "Food", "Water filter", "Headlamp", "First aid kit"]
    }
    
    def generate_checklist(
        self,
        activity: str,
        safety_analysis: dict,
        weather_data: dict,
        duration_hours: int = 4
    ) -> List[str]:
        """
        Generate gear checklist based on activity and conditions.
        
        Args:
            activity: Activity type
            safety_analysis: Safety score and risk data
            weather_data: Weather conditions
            duration_hours: Expected duration
            
        Returns:
            List[str]: Recommended gear items (legacy format)
        """
        # Use new function and convert to simple list format
        full_checklist = generate_checklist(activity, safety_analysis, weather_data)
        
        # Extract just the item names for legacy compatibility
        return [item["item"] for item in full_checklist]
    
    def _add_weather_gear(self, weather_data: dict) -> List[str]:
        """Add weather-specific gear."""
        gear = []
        
        temp = weather_data.get("temp", 70)
        condition = weather_data.get("condition", "clear").lower()
        wind_speed = weather_data.get("wind_speed", 0)
        
        # Temperature-based
        if temp < 40:
            gear.extend(["Winter jacket", "Gloves", "Hat", "Thermal layers"])
        elif temp < 60:
            gear.extend(["Light jacket", "Long sleeves"])
        elif temp > 85:
            gear.extend(["Hat", "Light clothing", "Extra water"])
        
        # Condition-based
        if "rain" in condition or "storm" in condition:
            gear.extend(["Rain jacket", "Waterproof bag", "Extra layers"])
        
        if wind_speed > 15:
            gear.append("Windbreaker")
        
        return gear
    
    def _add_air_quality_gear(self, safety_analysis: dict) -> List[str]:
        """Add air quality protection gear."""
        gear = []
        
        # TODO: Extract AQ data from safety_analysis
        aqi = safety_analysis.get("environmental_metrics", {}).get("airQuality", {}).get("aqi", 50)
        
        if aqi > 100:
            gear.append("N95 mask or respirator")
        
        if aqi > 150:
            gear.extend(["Eye protection", "Consider rescheduling"])
        
        return gear
    
    def _add_duration_gear(self, duration_hours: int) -> List[str]:
        """Add duration-specific gear."""
        gear = []
        
        if duration_hours > 4:
            gear.extend(["Extra food", "Extra water", "Phone charger/battery pack"])
        
        if duration_hours > 8:
            gear.extend(["Headlamp", "Emergency shelter", "Warm layers"])
        
        return gear
    
    def _add_terrain_gear(self, safety_analysis: dict) -> List[str]:
        """Add terrain-specific gear."""
        gear = []
        
        # TODO: Extract elevation/terrain data
        # Example:
        # elevation = safety_analysis.get("elevation_data", {}).get("elevation_m", 0)
        # if elevation > 2500:
        #     gear.extend(["Altitude medication", "Extra layers"])
        
        return gear
    
    def prioritize_checklist(self, checklist: List[str]) -> List[str]:
        """
        Prioritize checklist items (essential first).
        
        Args:
            checklist: Unordered checklist
            
        Returns:
            List[str]: Prioritized checklist
        """
        # TODO: Implement priority logic
        # Essential items first (safety, hydration), then comfort items
        
        essential = ["First aid kit", "Water", "Phone", "Emergency shelter"]
        safety = ["Helmet", "N95 mask", "Headlamp"]
        comfort = []
        
        prioritized = []
        
        for item in checklist:
            if any(e.lower() in item.lower() for e in essential):
                prioritized.insert(0, item)
            elif any(s.lower() in item.lower() for s in safety):
                prioritized.append(item)
            else:
                comfort.append(item)
        
        return prioritized + comfort
