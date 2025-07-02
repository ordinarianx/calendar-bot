# Tools for the agent to interact with the calendar backend
from langchain.tools import BaseTool
import httpx
import os
import logging

# Environment config
API_URL: str = os.getenv("FASTAPI_URL", "http://127.0.0.1:8000")

class CheckAvailabilityTool(BaseTool):
    name: str = "check_availability"  # type annotation required by Pydantic
    description: str = "Ask for free slots in my calendar."

    async def _arun(self, time_range: str):  # Optional async support
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_URL}/availability", params={"range": time_range}, timeout=10
            )
            return response.json()

    def _run(self, time_range: str):
        # For sync fallback
        import requests
        response = requests.get(
            f"{API_URL}/availability", params={"range": time_range}, timeout=10
        )
        return response.json()

class CreateEventTool(BaseTool):
    name: str = "create_event"
    description: str = (
        "Create a calendar event. "
        "Format event_details as: Title: <title>; Start: <ISO8601 datetime>; Duration: <minutes>. "
        "If the user says things like 'tomorrow', '3 days from now', etc., always convert them to ISO8601 UTC."
        "Example: Title: Meeting; Start: 2025-07-03T10:00:00Z; Duration: 60"
    )

    async def _arun(self, event_details: str):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_URL}/events", json={"details": event_details}, timeout=10
            )
            return response.json()

    def _run(self, event_details: str):
        # For sync fallback
        import requests
        response = requests.post(
            f"{API_URL}/events", json={"details": event_details}, timeout=10
        )
        return response.json()

class GetEventDetailsTool(BaseTool):
    name: str = "get_event_details"
    description: str = (
        "Fetch details of events scheduled in a given time range. "
        "Input should be a time range in ISO8601 format (e.g., 2025-07-03T14:00:00Z/2025-07-03T15:00:00Z). "
        "Returns event summaries, times, and descriptions if present."
    )

    async def _arun(self, time_range: str):
        start, end = time_range.split("/")
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_URL}/event_details", params={"start": start, "end": end}, timeout=10
            )
            return response.json()

    def _run(self, time_range: str):
        start, end = time_range.split("/")
        import requests
        response = requests.get(
            f"{API_URL}/event_details", params={"start": start, "end": end}, timeout=10
        )
        return response.json()
