"""Supabase client initialization and helpers."""
from supabase import create_client, Client
from app.config import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Singleton Supabase client wrapper."""
    
    _instance: Optional[Client] = None
    
    @classmethod
    def get_client(cls) -> Client:
        """Get or create Supabase client instance."""
        if cls._instance is None:
            try:
                cls._instance = create_client(
                    supabase_url=settings.supabase_url,
                    supabase_key=settings.supabase_key
                )
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                raise
        return cls._instance


def get_db() -> Client:
    """Dependency for getting Supabase client in routes."""
    return SupabaseClient.get_client()


# TODO: Add helper functions for common database operations
# Example:
# async def save_trip(trip_data: dict) -> dict:
#     """Save trip analysis to database."""
#     client = get_db()
#     result = client.table("trips").insert(trip_data).execute()
#     return result.data[0]

# async def get_user_trips(user_id: str) -> list[dict]:
#     """Retrieve all trips for a user."""
#     client = get_db()
#     result = client.table("trips").select("*").eq("user_id", user_id).execute()
#     return result.data
