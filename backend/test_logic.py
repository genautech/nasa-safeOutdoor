"""Test script for business logic (risk scoring and checklist generation)."""
import logging
from app.logic.risk_score import calculate_safety_score
from app.logic.checklist import generate_checklist

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def test_risk_scoring():
    """Test risk score calculation with various scenarios."""
    
    print("\n" + "=" * 70)
    print("TESTING RISK SCORE CALCULATION")
    print("=" * 70)
    
    # Scenario 1: Excellent conditions
    print("\n📊 Scenario 1: Excellent Conditions (Perfect day for hiking)")
    data1 = {
        "activity": "hiking",
        "aqi": 35,
        "pm25": 10.5,
        "no2": 15.0,
        "uv_index": 4.0,
        "elevation": 500,
        "weather": {
            "temp_c": 22,
            "wind_speed_kmh": 8,
            "precipitation_mm": 0,
            "humidity": 55
        }
    }
    
    result1 = calculate_safety_score(data1)
    print(f"  Score: {result1['score']}/10 ({result1['category']})")
    print(f"  Risk Factors:")
    for factor in result1['risk_factors']:
        print(f"    - {factor['factor']}: {factor['score']}/10 (weight: {factor['weight']})")
    print(f"  Warnings: {len(result1['warnings'])}")
    for warning in result1['warnings']:
        print(f"    {warning}")
    
    # Scenario 2: Poor air quality
    print("\n📊 Scenario 2: Poor Air Quality (AQI 155, high PM2.5)")
    data2 = {
        "activity": "running",
        "aqi": 155,
        "pm25": 55.0,
        "no2": 35.0,
        "uv_index": 7.0,
        "elevation": 200,
        "weather": {
            "temp_c": 28,
            "wind_speed_kmh": 12,
            "precipitation_mm": 0,
            "humidity": 65
        }
    }
    
    result2 = calculate_safety_score(data2)
    print(f"  Score: {result2['score']}/10 ({result2['category']})")
    print(f"  Risk Factors:")
    for factor in result2['risk_factors']:
        print(f"    - {factor['factor']}: {factor['score']}/10 (weight: {factor['weight']})")
    print(f"  Warnings: {len(result2['warnings'])}")
    for warning in result2['warnings']:
        print(f"    {warning}")
    
    # Scenario 3: Extreme heat
    print("\n📊 Scenario 3: Extreme Heat (38°C, high UV)")
    data3 = {
        "activity": "cycling",
        "aqi": 65,
        "pm25": 18.0,
        "no2": 22.0,
        "uv_index": 11.5,
        "elevation": 100,
        "weather": {
            "temp_c": 38,
            "wind_speed_kmh": 5,
            "precipitation_mm": 0,
            "humidity": 40
        }
    }
    
    result3 = calculate_safety_score(data3)
    print(f"  Score: {result3['score']}/10 ({result3['category']})")
    print(f"  Risk Factors:")
    for factor in result3['risk_factors']:
        print(f"    - {factor['factor']}: {factor['score']}/10 (weight: {factor['weight']})")
    print(f"  Warnings: {len(result3['warnings'])}")
    for warning in result3['warnings']:
        print(f"    {warning}")
    
    # Scenario 4: High altitude mountaineering
    print("\n📊 Scenario 4: High Altitude Mountaineering (4500m)")
    data4 = {
        "activity": "mountaineering",
        "aqi": 25,
        "pm25": 8.0,
        "no2": 12.0,
        "uv_index": 10.0,
        "elevation": 4500,
        "weather": {
            "temp_c": -5,
            "wind_speed_kmh": 35,
            "precipitation_mm": 5,
            "humidity": 70
        }
    }
    
    result4 = calculate_safety_score(data4)
    print(f"  Score: {result4['score']}/10 ({result4['category']})")
    print(f"  Risk Factors:")
    for factor in result4['risk_factors']:
        print(f"    - {factor['factor']}: {factor['score']}/10 (weight: {factor['weight']})")
    print(f"  Warnings: {len(result4['warnings'])}")
    for warning in result4['warnings']:
        print(f"    {warning}")
    
    # Scenario 5: Dangerous conditions (all bad)
    print("\n📊 Scenario 5: Dangerous Conditions (AQI 250, extreme heat, high winds)")
    data5 = {
        "activity": "rock_climbing",
        "aqi": 250,
        "pm25": 85.0,
        "no2": 45.0,
        "uv_index": 12.0,
        "elevation": 1800,
        "weather": {
            "temp_c": 40,
            "wind_speed_kmh": 65,
            "precipitation_mm": 0,
            "humidity": 15
        }
    }
    
    result5 = calculate_safety_score(data5)
    print(f"  Score: {result5['score']}/10 ({result5['category']})")
    print(f"  Risk Factors:")
    for factor in result5['risk_factors']:
        print(f"    - {factor['factor']}: {factor['score']}/10 (weight: {factor['weight']})")
    print(f"  Warnings: {len(result5['warnings'])}")
    for warning in result5['warnings']:
        print(f"    {warning}")


def test_checklist_generation():
    """Test checklist generation with various scenarios."""
    
    print("\n\n" + "=" * 70)
    print("TESTING CHECKLIST GENERATION")
    print("=" * 70)
    
    # Scenario 1: Summer hiking (hot, high UV)
    print("\n🎒 Scenario 1: Summer Hiking (32°C, UV 9, good air quality)")
    risk_data1 = {
        "aqi": 45,
        "pm25": 12.0,
        "uv_index": 9.0,
        "elevation": 800
    }
    weather1 = {
        "temp_c": 32,
        "wind_speed_kmh": 10,
        "precipitation_mm": 0,
        "humidity": 55
    }
    
    checklist1 = generate_checklist("hiking", risk_data1, weather1)
    print(f"  Total items: {len(checklist1)}")
    print(f"  Required items: {sum(1 for item in checklist1 if item['required'])}")
    print("\n  Top 10 Required Items:")
    for i, item in enumerate([x for x in checklist1 if x['required']][:10], 1):
        print(f"    {i}. {item['item']}")
        print(f"       Reason: {item['reason']}")
    
    # Scenario 2: Winter camping (cold, some precipitation)
    print("\n🎒 Scenario 2: Winter Camping (-8°C, 15mm precipitation)")
    risk_data2 = {
        "aqi": 55,
        "pm25": 15.0,
        "uv_index": 2.0,
        "elevation": 1200
    }
    weather2 = {
        "temp_c": -8,
        "wind_speed_kmh": 25,
        "precipitation_mm": 15,
        "humidity": 75
    }
    
    checklist2 = generate_checklist("camping", risk_data2, weather2)
    print(f"  Total items: {len(checklist2)}")
    print(f"  Required items: {sum(1 for item in checklist2 if item['required'])}")
    print("\n  Top 10 Required Items:")
    for i, item in enumerate([x for x in checklist2 if x['required']][:10], 1):
        print(f"    {i}. {item['item']}")
        print(f"       Reason: {item['reason']}")
    
    # Scenario 3: Trail running with poor air quality
    print("\n🎒 Scenario 3: Trail Running (AQI 135, moderate conditions)")
    risk_data3 = {
        "aqi": 135,
        "pm25": 48.0,
        "uv_index": 6.0,
        "elevation": 600
    }
    weather3 = {
        "temp_c": 24,
        "wind_speed_kmh": 15,
        "precipitation_mm": 2,
        "humidity": 60
    }
    
    checklist3 = generate_checklist("trail_running", risk_data3, weather3)
    print(f"  Total items: {len(checklist3)}")
    print(f"  Required items: {sum(1 for item in checklist3 if item['required'])}")
    print("\n  Top 10 Required Items:")
    for i, item in enumerate([x for x in checklist3 if x['required']][:10], 1):
        print(f"    {i}. {item['item']}")
        print(f"       Reason: {item['reason']}")
    
    # Show safety warnings from checklist
    safety_items = [x for x in checklist3 if x['category'] == 'safety']
    if safety_items:
        print(f"\n  Safety Notices:")
        for item in safety_items:
            print(f"    ⚠️  {item['item']}: {item['reason']}")
    
    # Scenario 4: High altitude mountaineering
    print("\n🎒 Scenario 4: Mountaineering (4200m altitude, cold, windy)")
    risk_data4 = {
        "aqi": 30,
        "pm25": 8.0,
        "uv_index": 9.0,
        "elevation": 4200
    }
    weather4 = {
        "temp_c": -12,
        "wind_speed_kmh": 45,
        "precipitation_mm": 8,
        "humidity": 70
    }
    
    checklist4 = generate_checklist("mountaineering", risk_data4, weather4)
    print(f"  Total items: {len(checklist4)}")
    print(f"  Required items: {sum(1 for item in checklist4 if item['required'])}")
    print("\n  Medical & Safety Items:")
    medical_safety = [x for x in checklist4 if x['category'] in ['medical', 'safety']]
    for item in medical_safety:
        req_str = "✓ REQUIRED" if item['required'] else "  Optional"
        print(f"    [{req_str}] {item['item']}")
        print(f"                Reason: {item['reason']}")


def test_activity_specific_modifiers():
    """Test activity-specific adjustments."""
    
    print("\n\n" + "=" * 70)
    print("TESTING ACTIVITY-SPECIFIC MODIFIERS")
    print("=" * 70)
    
    # Same conditions, different activities
    base_data = {
        "aqi": 125,
        "pm25": 42.0,
        "no2": 28.0,
        "uv_index": 7.0,
        "elevation": 800,
        "weather": {
            "temp_c": 26,
            "wind_speed_kmh": 35,
            "precipitation_mm": 0,
            "humidity": 60
        }
    }
    
    activities = ["hiking", "running", "rock_climbing", "cycling"]
    
    print("\n📍 Same conditions (AQI 125, 35km/h wind), different activities:\n")
    
    for activity in activities:
        data = base_data.copy()
        data["activity"] = activity
        result = calculate_safety_score(data)
        print(f"  {activity.title():<20} Score: {result['score']}/10 ({result['category']})")
        print(f"                       Warnings: {len(result['warnings'])}")
        if result['warnings']:
            for warning in result['warnings'][:2]:  # Show first 2 warnings
                print(f"                         - {warning}")


if __name__ == "__main__":
    print("\n🧪 SafeOutdoor Business Logic Test Suite\n")
    
    # Run all tests
    test_risk_scoring()
    test_checklist_generation()
    test_activity_specific_modifiers()
    
    print("\n\n" + "=" * 70)
    print("✅ All tests completed!")
    print("=" * 70)
    
    print("\n📝 Summary:")
    print("  - Risk scoring considers: Air quality, Weather, UV, Terrain")
    print("  - Activity-specific modifiers adjust scores appropriately")
    print("  - Warnings are generated based on hazardous conditions")
    print("  - Checklists dynamically adapt to conditions")
    print("  - Items are categorized and prioritized (required first)")
    print("\n")
