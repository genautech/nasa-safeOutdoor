"""AI analysis using OpenAI function calling."""
import logging
from openai import AsyncOpenAI
from app.config import settings
from typing import Optional

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """Generate AI insights using OpenAI."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = "gpt-4o-mini"  # Or "gpt-4" for better quality
    
    async def generate_insights(
        self,
        activity: str,
        location: str,
        safety_data: dict,
        weather_data: dict,
        air_quality_data: dict
    ) -> str:
        """
        Generate AI-powered insights and recommendations.
        
        Args:
            activity: Activity type
            location: Location name/description
            safety_data: Safety score and analysis
            weather_data: Weather conditions
            air_quality_data: Air quality metrics
            
        Returns:
            str: AI-generated insights and recommendations
        """
        logger.info(f"Generating AI insights for {activity} at {location}")
        
        # Build context prompt
        prompt = self._build_prompt(
            activity, location, safety_data, weather_data, air_quality_data
        )
        
        try:
            # TODO: Implement OpenAI API call with function calling
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an outdoor safety expert AI assistant. "
                                  "Provide concise, actionable insights about outdoor conditions "
                                  "for activities. Focus on safety, health, and optimization tips."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            insights = response.choices[0].message.content.strip()
            logger.info(f"Generated {len(insights)} characters of insights")
            return insights
            
        except Exception as e:
            logger.error(f"Error generating AI insights: {e}")
            return self._get_fallback_insights(safety_data)
    
    def _build_prompt(
        self,
        activity: str,
        location: str,
        safety_data: dict,
        weather_data: dict,
        air_quality_data: dict
    ) -> str:
        """Build prompt for OpenAI."""
        aqi = air_quality_data.get("aqi", 50)
        temp = weather_data.get("temp", 70)
        condition = weather_data.get("condition", "clear")
        safety_score = safety_data.get("safety_score", 75)
        risk_level = safety_data.get("risk_level", "moderate")
        
        prompt = f"""Analyze outdoor conditions for {activity} at {location}:

Safety Score: {safety_score}/100 (Risk: {risk_level})
Air Quality: AQI {aqi} (PM2.5: {air_quality_data.get('pm25', 'N/A')})
Weather: {temp}°F, {condition}

Provide:
1. Brief condition summary (2 sentences)
2. Top 2-3 specific safety recommendations
3. Best time suggestion if conditions aren't optimal

Keep response under 200 words, practical and actionable."""
        
        return prompt
    
    async def generate_route_insights(
        self,
        activity: str,
        route_segments: list[dict],
        overall_safety: dict
    ) -> str:
        """
        Generate insights specific to route conditions.
        
        Args:
            activity: Activity type
            route_segments: List of route segment analyses
            overall_safety: Overall safety data
            
        Returns:
            str: Route-specific insights
        """
        # TODO: Implement route-specific AI analysis
        logger.info("Generating route insights")
        
        # Find segments with warnings
        problem_segments = [
            seg for seg in route_segments
            if seg.get("warnings")
        ]
        
        if problem_segments:
            prompt = f"""Analyze this {activity} route with varying conditions:

Route has {len(route_segments)} segments.
{len(problem_segments)} segments have warnings.

Problem areas:
{self._format_problem_segments(problem_segments)}

Provide brief route-specific advice (under 150 words):
1. Critical warnings to note
2. Route timing recommendations
3. Alternative suggestions if needed"""
            
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an outdoor safety expert."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=250
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                logger.error(f"Error generating route insights: {e}")
                return "Route conditions vary. Pay attention to segments with higher AQI and UV exposure."
        
        return "Route conditions are relatively consistent. Maintain hydration and sun protection throughout."
    
    def _format_problem_segments(self, segments: list[dict]) -> str:
        """Format problem segments for prompt."""
        lines = []
        for seg in segments[:3]:  # Limit to top 3
            warnings = ", ".join(seg.get("warnings", []))
            lines.append(f"- {seg['name']}: {warnings}")
        return "\n".join(lines)
    
    def _get_fallback_insights(self, safety_data: dict) -> str:
        """Generate fallback insights when API fails."""
        score = safety_data.get("safety_score", 75)
        risk = safety_data.get("risk_level", "moderate")
        
        if score >= 80:
            return "Conditions are excellent for outdoor activities. Stay hydrated and wear sunscreen."
        elif score >= 60:
            return "Conditions are good overall. Monitor air quality and weather changes. Take breaks as needed."
        elif score >= 40:
            return "Conditions are marginal. Consider shorter duration. Use respiratory protection if sensitive."
        else:
            return "Conditions are challenging. Consider rescheduling or choose indoor alternatives for safety."
