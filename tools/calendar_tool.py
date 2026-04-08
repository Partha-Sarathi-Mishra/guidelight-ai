"""MCP-compliant Google Calendar tool stub.

In production this would connect to the real Google Calendar API via MCP.
For the hackathon demo it provides a deterministic, in-memory calendar that
demonstrates the MCP tool contract.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

# In-memory calendar store (plan_id → list of events)
_calendar_store: dict[str, list[dict[str, Any]]] = {}


def schedule_event(
    plan_id: str,
    title: str,
    start_time: str,
    end_time: str,
    description: str = "",
) -> dict[str, Any]:
    """Schedule a calendar event via the MCP Google Calendar interface.

    Args:
        plan_id: The plan this event belongs to.
        title: Event title.
        start_time: ISO-8601 start time (e.g. "2026-04-07T09:00:00").
        end_time: ISO-8601 end time.
        description: Optional description.

    Returns:
        A dict representing the created calendar event.
    """
    event = {
        "event_id": str(uuid.uuid4())[:8],
        "plan_id": plan_id,
        "title": title,
        "start_time": start_time,
        "end_time": end_time,
        "description": description,
        "created_at": datetime.utcnow().isoformat(),
        "status": "confirmed",
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
    """Remove a calendar event by id."""
    events = _calendar_store.get(plan_id, [])
    for i, ev in enumerate(events):
        if ev["event_id"] == event_id:
            events.pop(i)
            return True
    return False
