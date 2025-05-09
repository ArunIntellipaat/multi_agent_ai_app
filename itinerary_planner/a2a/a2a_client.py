import os
import uuid
import httpx
from typing import Optional, Dict, Any

# Base URLs for the A2A compliant agent APIs
FLIGHT_SEARCH_API_URL = os.getenv("FLIGHT_SEARCH_API_URL", "http://localhost:8000")
HOTEL_SEARCH_API_URL = os.getenv("HOTEL_SEARCH_API_URL", "http://localhost:8003")

class A2AClientBase:
    async def send_a2a_task(self, user_message: str, task_id: Optional[str] = None) -> Dict[str, Any]:
        raise NotImplementedError

class FlightSearchClient(A2AClientBase):
    def __init__(self, http_client: Optional[httpx.AsyncClient] = None):
        self.http_client = http_client

    async def send_a2a_task(self, user_message: str, task_id: Optional[str] = None) -> Dict[str, Any]:
        task_id = task_id or str(uuid.uuid4())
        payload = {
            "jsonrpc": "2.0",
            "method": "tasks/send",
            "params": {
                "id": task_id,
                "taskId": task_id,
                "message": {
                    "role": "user",
                    "parts": [
                        {"type": "text", "text": user_message}
                    ]
                }
            },
            "id": task_id
        }

        if self.http_client:
            response = await self.http_client.post(f"{FLIGHT_SEARCH_API_URL}/v1/tasks/send", json=payload)
        else:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{FLIGHT_SEARCH_API_URL}/v1/tasks/send", json=payload)

        response.raise_for_status()
        return response.json()

class HotelSearchClient(A2AClientBase):
    def __init__(self, http_client: Optional[httpx.AsyncClient] = None):
        self.http_client = http_client

    async def send_a2a_task(self, user_message: str, task_id: Optional[str] = None) -> Dict[str, Any]:
        task_id = task_id or str(uuid.uuid4())
        payload = {
            "jsonrpc": "2.0",
            "method": "tasks/send",
            "params": {
                "id": task_id,
                "taskId": task_id,
                "message": {
                    "role": "user",
                    "parts": [
                        {"type": "text", "text": user_message}
                    ]
                }
            },
            "id": task_id
        }

        if self.http_client:
            response = await self.http_client.post(f"{HOTEL_SEARCH_API_URL}/v1/tasks/send", json=payload)
        else:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{HOTEL_SEARCH_API_URL}/v1/tasks/send", json=payload)

        response.raise_for_status()
        return response.json()