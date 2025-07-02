import os
import sys
import logging
import datetime
import traceback
import asyncio
from typing import Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from dotenv import load_dotenv
import dateparser
import httpx

from utils import parse_range, derive_free_slots

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("calendar-bot.log"),
        logging.StreamHandler()
    ]
)

# Load .env from backend/
load_dotenv()

app = FastAPI()

# Google Calendar API setup
KEY_PATH = "/etc/secrets/calendar-bot-sa.json" # production path
SCOPES = ["https://www.googleapis.com/auth/calendar"]
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")
AGENT_URL = os.getenv("AGENT_URL", "http://127.0.0.1:8001")

if not CALENDAR_ID:
    logging.critical("GOOGLE_CALENDAR_ID environment variable not set.")
    sys.exit(1)
if not os.path.exists(KEY_PATH):
    KEY_PATH = os.path.join(os.path.dirname(__file__), "credentials", "calendar-bot-sa.json") # fallback path
    if not os.path.exists(KEY_PATH):
        logging.critical(f"Google service account credentials file not found at {KEY_PATH}.")
    sys.exit(1)
try:
    creds = service_account.Credentials.from_service_account_file(KEY_PATH, scopes=SCOPES)
    service = build("calendar", "v3", credentials=creds)
    service.calendars().get(calendarId=CALENDAR_ID).execute()
except Exception as e:
    logging.critical(f"Google Calendar API access failed: {e}")
    sys.exit(1)

class EventRequest(BaseModel):
    details: str

class RunRequest(BaseModel):
    prompt: str

@app.get("/availability")
async def get_availability(range: str) -> dict:
    """Return free slots for a given time range."""
    try:
        start_iso, end_iso = parse_range(range)
        logging.info(f"Parsed range: {range} -> {start_iso} to {end_iso}")
    except Exception as e:
        logging.error(f"Error parsing range: {e}")
        raise HTTPException(status_code=400, detail="Invalid time range.")

    if not start_iso.endswith("Z"):
        start_iso += "Z"
    if not end_iso.endswith("Z"):
        end_iso += "Z"

    body = {
        "timeMin": start_iso,
        "timeMax": end_iso,
        "items": [{"id": CALENDAR_ID}]
    }
    logging.info(f"FreeBusy request body: {body}")
    loop = asyncio.get_running_loop()
    try:
        fb = await loop.run_in_executor(
            None,
            lambda: service.freebusy().query(body=body).execute()
        )
        busy = fb["calendars"][CALENDAR_ID]["busy"]
    except Exception as e:
        tb = traceback.format_exc()
        logging.error(f"Google API error: {e}\n{tb}")
        raise HTTPException(status_code=500, detail="Google Calendar API error.")
    slots = derive_free_slots(busy, start_iso, end_iso)
    return {"slots": slots}

@app.post("/events")
async def create_event(req: EventRequest):
    """Create a calendar event from details string."""
    try:
        parts = dict(item.split(":", 1) for item in req.details.split(";"))
        title = parts.get("Title", parts.get(" Title")).strip()
        start_str = parts.get("Start", parts.get(" Start")).strip()
        duration = int(parts.get("Duration", parts.get(" Duration")).strip())
    except Exception as e:
        logging.error(f"Invalid details format: {req.details} | Error: {e}")
        raise HTTPException(status_code=400, detail="Invalid details format.")

    start_dt = dateparser.parse(start_str, settings={"TIMEZONE": "UTC", "RETURN_AS_TIMEZONE_AWARE": True})
    if not start_dt:
        logging.error(f"Could not parse date: {start_str}")
        raise HTTPException(status_code=400, detail="Could not parse Start date/time")
    start_iso = start_dt.isoformat().replace("+00:00", "Z")
    end_dt = (start_dt + datetime.timedelta(minutes=duration)).isoformat().replace("+00:00", "Z")

    event_body: Dict = {
        "summary": title,
        "start": {"dateTime": start_iso},
        "end": {"dateTime": end_dt},
    }
    loop = asyncio.get_running_loop()
    try:
        created = await loop.run_in_executor(
            None,
            lambda: service.events().insert(calendarId=CALENDAR_ID, body=event_body).execute()
        )
        logging.info(f"Event created: {created.get('id')}")
    except HttpError as e:
        logging.error(f"Google Calendar insert error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "id": created.get("id"),
        "htmlLink": created.get("htmlLink"),
        "summary": created.get("summary"),
        "start": created.get("start"),
        "end": created.get("end")
    }

@app.post("/run")
async def run(req: RunRequest):
    """Run the agent with the given prompt via HTTP."""
    now_utc = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    prompt = f"Current UTC date and time is {now_utc}.\n{req.prompt}"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{AGENT_URL}/run",
                json={"prompt": prompt},
                timeout=60
            )
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPError as e:
        logging.error(f"Agent HTTP error: {e}")
        raise HTTPException(status_code=500, detail=f"Agent HTTP error: {e}")
    except Exception as e:
        tb = traceback.format_exc()
        logging.error(f"Agent error: {e}\n{tb}")
        raise HTTPException(status_code=500, detail=f"Agent error: {e}\n{tb}")

@app.get("/event_details")
async def get_event_details(start: str, end: str):
    """Return event details for a given time range."""
    loop = asyncio.get_running_loop()
    try:
        events_result = await loop.run_in_executor(
            None,
            lambda: service.events().list(
                calendarId=CALENDAR_ID,
                timeMin=start,
                timeMax=end,
                singleEvents=True,
                orderBy="startTime"
            ).execute()
        )
        events = events_result.get("items", [])
        if not events:
            return {"events": []}
        # Return only relevant fields for brevity
        return {
            "events": [
                {
                    "summary": e.get("summary"),
                    "start": e.get("start"),
                    "end": e.get("end"),
                    "description": e.get("description", "")
                }
                for e in events
            ]
        }
    except Exception as e:
        logging.error(f"Error fetching event details: {e}")
        raise HTTPException(status_code=500, detail="Error fetching event details")