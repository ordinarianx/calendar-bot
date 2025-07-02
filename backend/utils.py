import datetime
from typing import List, Dict, Tuple
import dateparser
import logging


def derive_free_slots(
    busy: List[Dict[str, str]],
    start_iso: str,
    end_iso: str,
    slot_duration_minutes: int = 30
) -> List[Dict[str, str]]:
    """Return free slots between start_iso and end_iso, avoiding busy periods."""
    slots = []
    start = datetime.datetime.fromisoformat(start_iso.replace("Z", "+00:00"))
    end = datetime.datetime.fromisoformat(end_iso.replace("Z", "+00:00"))
    busy_periods = [
        (
            datetime.datetime.fromisoformat(b["start"].replace("Z", "+00:00")),
            datetime.datetime.fromisoformat(b["end"].replace("Z", "+00:00"))
        )
        for b in busy
    ]
    current = start
    while current + datetime.timedelta(minutes=slot_duration_minutes) <= end:
        slot_end = current + datetime.timedelta(minutes=slot_duration_minutes)
        overlap = any(
            not (slot_end <= b_start or current >= b_end)
            for b_start, b_end in busy_periods
        )
        if not overlap:
            slots.append({
                "start": current.isoformat().replace("+00:00", "Z"),
                "end": slot_end.isoformat().replace("+00:00", "Z")
            })
        current += datetime.timedelta(minutes=slot_duration_minutes)
    return slots


def parse_range(natural: str) -> Tuple[str, str]:
    """
    Parse a natural language range (e.g., 'tomorrow', 'next week', '3 days from now')
    into ISO8601 UTC start and end datetimes.
    """
    now = datetime.datetime.utcnow()
    # Try to parse a start date
    start_dt = dateparser.parse(natural, settings={"TIMEZONE": "UTC", "RETURN_AS_TIMEZONE_AWARE": True})
    if not start_dt:
        logging.warning(f"Could not parse date from input: {natural}, defaulting to today.")
        start_dt = now.replace(hour=0, minute=0, second=0, microsecond=0)
    # Heuristic for end date: if 'week' in input, add 7 days; if 'month', add 30; else 1 day
    if "week" in natural.lower():
        end_dt = start_dt + datetime.timedelta(days=7)
    elif "month" in natural.lower():
        end_dt = start_dt + datetime.timedelta(days=30)
    else:
        end_dt = start_dt + datetime.timedelta(days=1)
    return (
        start_dt.replace(hour=0, minute=0, second=0, microsecond=0).isoformat().replace("+00:00", "Z"),
        end_dt.replace(hour=0, minute=0, second=0, microsecond=0).isoformat().replace("+00:00", "Z")
    )
