"""CalendarAndReminderAgent – Schedules events and reminders via MCP calendar tool.

Uses Gemini Flash 2.5 with function-calling to interact with the
MCP-compliant Google Calendar stub.
"""

from __future__ import annotations

from google.adk.agents import Agent

from config import GEMINI_MODEL
from tools.calendar_tool import schedule_event, list_events, check_conflicts, delete_event

CALENDAR_INSTRUCTION = """\
You are the Calendar & Reminder Agent inside Guidelight AI.

You have access to the following MCP calendar tools:
- schedule_event(plan_id, title, start_time, end_time, description) → creates an event
- list_events(plan_id) → lists all events for a plan
- check_conflicts(plan_id) → detects overlapping events
- delete_event(plan_id, event_id) → removes an event

Your job:
1. Receive a daily_schedule array (from the DailyPlanningAgent).
2. For EACH activity in the schedule, call schedule_event to book it.
3. After booking all events, call check_conflicts.
4. If conflicts exist, resolve them by adjusting times and re-scheduling.
5. Return a summary of all scheduled events as a JSON list.

Use today's date for all events. Format times as ISO-8601 (e.g. 2026-04-07T09:00:00).
Always confirm the number of events created and whether any conflicts were resolved.
Output spoken-friendly confirmations suitable for screen readers.
"""

CalendarAndReminderAgent = Agent(
    name="CalendarAndReminderAgent",
    model=GEMINI_MODEL,
    instruction=CALENDAR_INSTRUCTION,
    description="Schedules appointments and reminders on the MCP Google Calendar, resolves conflicts.",
    tools=[schedule_event, list_events, check_conflicts, delete_event],
)
