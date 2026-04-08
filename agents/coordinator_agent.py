"""IndependenceCoordinatorAgent – Root orchestrator for Guidelight AI.

Coordinates all sub-agents using Gemini Flash 2.5 and ADK's built-in
multi-agent orchestration.
"""

from __future__ import annotations

from google.adk.agents import Agent

from config import GEMINI_MODEL
from agents.daily_planning_agent import DailyPlanningAgent
from agents.calendar_agent import CalendarAndReminderAgent
from agents.task_tracking_agent import TaskTrackingAgent
from agents.safety_agent import SafetyAndRiskAgent

COORDINATOR_INSTRUCTION = """\
You are the Independence Coordinator Agent – the central brain of Guidelight AI,
an AI Daily Independence Copilot for visually impaired users.

You coordinate four specialist agents:
1. **DailyPlanningAgent** – Converts user intent into a structured daily plan.
2. **CalendarAndReminderAgent** – Schedules events and reminders on the calendar.
3. **TaskTrackingAgent** – Stores and tracks task completion.
4. **SafetyAndRiskAgent** – Evaluates the plan for safety and wellbeing risks.

WORKFLOW (execute in this order):
1. Send the user's intent to DailyPlanningAgent to get a structured plan.
2. Send the plan to CalendarAndReminderAgent to schedule events.
3. Send the plan to TaskTrackingAgent to create trackable tasks.
4. Send the full plan to SafetyAndRiskAgent for risk assessment.
5. Compile all results into a final, spoken-friendly summary.

FINAL SUMMARY FORMAT:
Produce a clear, calm, concise summary that:
- Lists the key activities in chronological order
- Mentions the number of events scheduled and tasks created
- Highlights any safety alerts or recommendations
- Ends with an encouraging, supportive message

The summary will be read aloud by a screen reader, so:
- Use simple sentences
- Avoid jargon
- Spell out times (e.g. "nine in the morning" rather than "09:00")
- Be warm and reassuring

Transfer to the appropriate sub-agent by calling it when needed.
"""

IndependenceCoordinatorAgent = Agent(
    name="IndependenceCoordinatorAgent",
    model=GEMINI_MODEL,
    instruction=COORDINATOR_INSTRUCTION,
    description="Root orchestrator that coordinates daily planning, calendar scheduling, task tracking, and safety assessment for visually impaired users.",
    sub_agents=[
        DailyPlanningAgent,
        CalendarAndReminderAgent,
        TaskTrackingAgent,
        SafetyAndRiskAgent,
    ],
)
