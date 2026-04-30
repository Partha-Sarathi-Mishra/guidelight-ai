"""MCP-compliant Google Calendar tool with REAL Google Calendar API integration.

Uses OAuth2 credentials to create events in the user's actual Google Calendar.
Falls back to in-memory store if credentials are not configured.
"""

from __future__ import annotations

import os
import uuid
import json
from datetime import datetime
from typing import Any
from pathlib import Path

# In-memory calendar store (fallback + local cache)
_calendar_store: dict[str, list[dict[str, Any]]] = {}

# Google Calendar API setup
_gcal_service = None
_SCOPES = ["https://www.googleapis.com/auth/calendar"]
_TOKEN_PATH = Path(__file__).parent.parent / "token.json"
_CREDENTIALS_PATH = Path(__file__).parent.parent / "credentials.json"
# Cloud Run secret mount paths (fallback)
_SECRET_TOKEN_PATH = Path("/secrets/gcal-token/token.json")
_SECRET_CREDENTIALS_PATH = Path("/secrets/gcal-creds/credentials.json")
_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "primary")


def _get_gcal_service():
    """Lazily initialize and return the Google Calendar API service."""
    global _gcal_service
    if _gcal_service is not None:
        return _gcal_service

    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build

        creds = None

        # Check local path first, then Cloud Run secret mount
        token_path = _TOKEN_PATH if _TOKEN_PATH.exists() else _SECRET_TOKEN_PATH

        # Load existing token
        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), _SCOPES)

        # Refresh if expired
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Only write back to local path (secret mount is read-only)
            if _TOKEN_PATH.parent.exists():
                try:
                    _TOKEN_PATH.write_text(creds.to_json())
                except OSError:
                    pass  # Read-only filesystem on Cloud Run

        if not creds or not creds.valid:
            print("[Calendar] No valid credentials found. Using in-memory fallback.")
            print(f"[Calendar] Run 'python3 tools/auth_calendar.py' to authenticate.")
            return None

        _gcal_service = build("calendar", "v3", credentials=creds)
        print("[Calendar] Connected to Google Calendar API ✓")
        return _gcal_service

    except ImportError:
        print("[Calendar] google-api-python-client not installed. Using in-memory fallback.")
        return None
    except Exception as e:
        print(f"[Calendar] Failed to initialize: {e}. Using in-memory fallback.")
        return None


def schedule_event(
    plan_id: str,
    title: str,
    start_time: str,
    end_time: str,
    description: str = "",
) -> dict[str, Any]:
    """Schedule a calendar event via Google Calendar API.

    Args:
        plan_id: The plan this event belongs to.
        title: Event title.
        start_time: ISO-8601 start time (e.g. "2026-04-07T09:00:00").
        end_time: ISO-8601 end time.
        description: Optional description/category.

    Returns:
        A dict representing the created calendar event.
    """
    event_id = str(uuid.uuid4())[:8]
    gcal_event_id = None

    # Try to create in real Google Calendar
    service = _get_gcal_service()
    if service:
        try:
            # Ensure timezone info is present
            tz = os.getenv("TZ", "Asia/Kolkata")
            gcal_body = {
                "summary": title,
                "description": f"[Guidelight AI] {description}\nPlan: {plan_id}",
                "start": {
                    "dateTime": start_time,
                    "timeZone": tz,
                },
                "end": {
                    "dateTime": end_time,
                    "timeZone": tz,
                },
                "reminders": {
                    "useDefault": False,
                    "overrides": [
                        {"method": "popup", "minutes": 10},
                    ],
                },
                "colorId": _category_color(description),
            }

            created = service.events().insert(
                calendarId=_CALENDAR_ID, body=gcal_body
            ).execute()
            gcal_event_id = created.get("id")
            print(f"  [GCal] Created: {title} @ {start_time} (id: {gcal_event_id})")
        except Exception as e:
            print(f"  [GCal] Failed to create event '{title}': {e}")

    # Always store locally too (for UI rendering)
    event = {
        "event_id": event_id,
        "gcal_event_id": gcal_event_id,
        "plan_id": plan_id,
        "title": title,
        "start_time": start_time,
        "end_time": end_time,
        "description": description,
        "created_at": datetime.utcnow().isoformat(),
        "status": "confirmed",
        "synced": gcal_event_id is not None,
    }
    _calendar_store.setdefault(plan_id, []).append(event)
    return event


def list_events(plan_id: str) -> list[dict[str, Any]]:
    """List all calendar events for a plan."""
    return _calendar_store.get(plan_id, [])


def check_conflicts(plan_id: str) -> list[dict[str, Any]]:
    """Detect overlapping events for a plan. Returns list of conflict pairs."""
    events = sorted(_calendar_store.get(plan_id, []), key=lambda e: e["start_time"])
    conflicts: list[dict[str, Any]] = []
    for i in range(len(events) - 1):
        if events[i]["end_time"] > events[i + 1]["start_time"]:
            conflicts.append({"event_a": events[i]["title"], "event_b": events[i + 1]["title"]})
    return conflicts


def delete_event(plan_id: str, event_id: str) -> bool:
    """Remove a calendar event by id (both locally and from Google Calendar)."""
    events = _calendar_store.get(plan_id, [])
    for i, ev in enumerate(events):
        if ev["event_id"] == event_id:
            # Delete from Google Calendar if synced
            if ev.get("gcal_event_id"):
                service = _get_gcal_service()
                if service:
                    try:
                        service.events().delete(
                            calendarId=_CALENDAR_ID, eventId=ev["gcal_event_id"]
                        ).execute()
                    except Exception as e:
                        print(f"  [GCal] Failed to delete: {e}")
            events.pop(i)
            return True
    return False


def _category_color(category: str) -> str:
    """Map category to Google Calendar color ID."""
    color_map = {
        "medication": "11",    # Red
        "meal": "5",           # Banana yellow
        "rest": "2",           # Green/sage
        "appointment": "3",    # Purple/grape
        "exercise": "6",       # Orange/tangerine
        "personal": "7",       # Cyan/peacock
        "general": "9",        # Blue/blueberry
    }
    return color_map.get(category.lower().strip(), "9")
