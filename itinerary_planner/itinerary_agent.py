import os
import logging
from typing import Optional

import google.generativeai as genai
import httpx

from itinerary_planner.a2a.a2a_client import FlightSearchClient, HotelSearchClient

# Configure the Google Generative AI SDK
api_key = os.getenv("GENAI_API_KEY", "your-api-key-here")
genai.configure(api_key=api_key)

logger = logging.getLogger(__name__)

class ItineraryPlanner:
    """A planner that coordinates between flight and hotel search agents to create itineraries using the google.generativeai SDK."""

    def __init__(self):
        """Initialize the itinerary planner."""
        logger.info("Initializing Itinerary Planner with google.generativeai SDK")

        # Use a shared httpx client with no timeout (for testing only)
        self.http_client = httpx.AsyncClient(timeout=None)

        self.flight_client = FlightSearchClient(http_client=self.http_client)
        self.hotel_client = HotelSearchClient(http_client=self.http_client)

        # Create the Gemini model instance using the SDK
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
        )

    async def create_itinerary(self, user_message: str) -> str:
        """Create an itinerary by interacting with the flight and hotel search agents."""
        
        origin = "New York"  # Placeholder; ideally parsed from user_message
        destination = "Paris"

        # Fetch flight options
        logger.info(f"Fetching flight details for {origin} to {destination}")
        flight_details = await self.flight_client.send_a2a_task(f"Find flights from {origin} to {destination}")

        # Fetch hotel options
        logger.info(f"Fetching hotel details for {destination}")
        hotel_details = await self.hotel_client.send_a2a_task(f"Find hotels in {destination}")

        itinerary = {
            "flights": flight_details,
            "hotels": hotel_details
        }

        # Optional: Use generative model for additional recommendations
        itinerary_summary = await self.model.generate(
            prompt=f"Create a detailed travel itinerary for flights and hotels in {destination}.",
        )

        return itinerary_summary["text"]  # Return generated itinerary as text