"""Guidelight AI – FastAPI Backend.

Exposes the three required API endpoints and serves the accessible demo UI.
Runs each ADK agent sequentially for deterministic, demo-reliable execution.
"""

from __future__ import annotations

import json
import uuid
import asyncio
from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents.daily_planning_agent import DailyPlanningAgent
from agents.calendar_agent import CalendarAndReminderAgent
from agents.task_tracking_agent import TaskTrackingAgent
from agents.safety_agent import SafetyAndRiskAgent
from agents.coordinator_agent import IndependenceCoordinatorAgent
from tools.task_store import get_plan_progress, list_tasks, create_task
from tools.calendar_tool import list_events, schedule_event
from config import HOST, PORT

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Guidelight AI",
    description="AI Daily Independence Copilot for Visually Impaired Users",
    version="1.0.0",
)

# In-memory plan store (plan_id → plan metadata + results)
_plan_store: dict[str, dict[str, Any]] = {}

# ADK session service – shared across all agent runners
session_service = InMemorySessionService()

# One runner per agent for deterministic sequential execution
_agents = {
    "planner": Runner(agent=DailyPlanningAgent, app_name="guidelight_ai", session_service=session_service),
    "calendar": Runner(agent=CalendarAndReminderAgent, app_name="guidelight_ai", session_service=session_service),
    "tasks": Runner(agent=TaskTrackingAgent, app_name="guidelight_ai", session_service=session_service),
    "safety": Runner(agent=SafetyAndRiskAgent, app_name="guidelight_ai", session_service=session_service),
    "coordinator": Runner(agent=IndependenceCoordinatorAgent, app_name="guidelight_ai", session_service=session_service),
}


# ---------------------------------------------------------------------------
# JSON parsing helper
# ---------------------------------------------------------------------------

def _try_parse_json(text: str) -> dict | None:
    """Try to extract and parse a JSON object from agent text output."""
    text = text.strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON object in the text
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
    return None


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------
class DailyIntentRequest(BaseModel):
    intent: str


class DailyIntentResponse(BaseModel):
    plan_id: str
    status: str
    message: str


# ---------------------------------------------------------------------------
# Helper – run a single agent and collect its output
# ---------------------------------------------------------------------------
async def _run_single_agent(
    runner_key: str,
    user_id: str,
    prompt: str,
    max_retries: int = 3,
) -> str:
    """Run one ADK agent with the given prompt and return its text output.
    Retries on rate-limit (429) errors with exponential backoff.
    """
    for attempt in range(max_retries):
        try:
            agent_runner = _agents[runner_key]
            session = await session_service.create_session(
                app_name="guidelight_ai",
                user_id=user_id,
            )
            message = types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            )
            result_text = ""
            tool_calls: list[str] = []
            async for event in agent_runner.run_async(
                user_id=session.user_id,
                session_id=session.id,
                new_message=message,
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        # Capture text responses
                        if part.text:
                            result_text = part.text.strip()
                        # Log function calls (tool use) without warning
                        elif hasattr(part, 'function_call') and part.function_call:
                            fc = part.function_call
                            tool_calls.append(f"{fc.name}({json.dumps(fc.args) if fc.args else ''})")
                        # Capture function responses too
                        elif hasattr(part, 'function_response') and part.function_response:
                            pass  # ADK handles these internally

            # If agent only made tool calls but returned no final text, summarize
            if not result_text and tool_calls:
                result_text = f"Executed {len(tool_calls)} tool calls: " + "; ".join(tool_calls)

            return result_text

        except Exception as exc:
            if "429" in str(exc) and attempt < max_retries - 1:
                wait = (attempt + 1) * 15  # 15s, 30s, 45s
                print(f"[Rate limited] Retrying {runner_key} in {wait}s (attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(wait)
                continue
            raise


# ---------------------------------------------------------------------------
# Helper – run the full deterministic pipeline (optimized: 2 LLM calls)
# ---------------------------------------------------------------------------

def _category_from_activity(text: str) -> str:
    """Guess task/event category from activity description."""
    t = text.lower()
    if any(w in t for w in ("medic", "pill", "drug", "vitamin", "eye drop", "blood pressure")):
        return "medication"
    if any(w in t for w in ("meal", "breakfast", "lunch", "dinner", "cook", "eat", "food", "grocery")):
        return "meal"
    if any(w in t for w in ("rest", "break", "relax", "nap", "audio", "read", "quiet")):
        return "rest"
    if any(w in t for w in ("doctor", "appointment", "hospital", "clinic", "physio", "therapy")):
        return "appointment"
    if any(w in t for w in ("exercise", "walk", "yoga", "stretch", "gym")):
        return "exercise"
    return "general"


def _populate_calendar_and_tasks(plan_id: str, plan_json: str, today: str) -> None:
    """Programmatically create calendar events and tasks from the plan JSON.

    This replaces two LLM calls (Calendar agent + Task agent) with direct
    Python function calls, saving RPM/RPD and tokens.
    """
    parsed = _try_parse_json(plan_json)
    if not parsed or "daily_schedule" not in parsed:
        return

    for item in parsed["daily_schedule"]:
        activity = item.get("activity", "Activity")
        time_str = item.get("time", "08:00")
        end_str = item.get("end_time", "")
        category = item.get("category", "") or _category_from_activity(activity)
        priority = item.get("priority", "normal")

        # Build ISO-8601 times
        start_iso = f"{today}T{time_str}:00"
        if end_str:
            end_iso = f"{today}T{end_str}:00"
        else:
            # Default 30-min duration
            h, m = int(time_str.split(":")[0]), int(time_str.split(":")[1])
            m += 30
            if m >= 60:
                h += 1
                m -= 60
            end_iso = f"{today}T{h:02d}:{m:02d}:00"

        # Create calendar event (MCP tool)
        schedule_event(
            plan_id=plan_id,
            title=activity,
            start_time=start_iso,
            end_time=end_iso,
            description=category,
        )

        # Create task (MCP tool)
        create_task(
            plan_id=plan_id,
            title=activity,
            scheduled_time=start_iso,
            category=category,
            priority=priority,
        )


async def _run_agent_pipeline(plan_id: str, intent: str) -> dict[str, Any]:
    """Execute the optimized pipeline: 2 LLM calls instead of 5.

    Call 1: Planner generates the structured JSON daily plan.
    Call 2: Safety + Summary combined — evaluates risks AND writes the
            spoken-friendly summary in one response.

    Calendar events and tasks are populated programmatically from the JSON.
    """
    user_id = f"user_{plan_id}"
    today = datetime.utcnow().strftime("%Y-%m-%d")

    # ── LLM Call 1: Daily Planning Agent ─────────────────────────────────
    planning_prompt = (
        f"Today is {today}. The user said:\n\"{intent}\"\n\n"
        "Generate a structured JSON daily plan. Output ONLY valid JSON."
    )
    plan_json = await _run_single_agent("planner", user_id, planning_prompt)

    # ── Programmatic: Calendar + Tasks (no LLM needed) ───────────────────
    _populate_calendar_and_tasks(plan_id, plan_json, today)

    # ── LLM Call 2: Safety evaluation + Final summary (combined) ─────────
    combined_prompt = (
        "You are the Independence Coordinator and Safety Agent for Guidelight AI.\n"
        "A visually impaired user asked for help planning their day.\n\n"
        f"Here is their structured daily plan:\n{plan_json}\n\n"
        "Do TWO things in your response, clearly separated:\n\n"
        "PART 1 — SAFETY (output as JSON on its own line):\n"
        "Evaluate the plan for safety risks. Output a JSON object with:\n"
        '{"risk_level":"low|medium|high","alerts":[{"type":"...","message":"...","severity":"info|warning|critical"}],'
        '"recommendations":["..."],"overall_assessment":"1-2 sentences"}\n\n'
        "PART 2 — SUMMARY (after the JSON):\n"
        "Write a warm, spoken-friendly daily plan summary. Use simple sentences, "
        "spell out times as words, be reassuring. This will be read aloud.\n\n"
        "Output PART 1 JSON first, then a blank line, then PART 2 text. "
        "Do NOT ask questions."
    )
    combined_result = await _run_single_agent("coordinator", user_id, combined_prompt)

    # ── Parse combined response ──────────────────────────────────────────
    safety_result = ""
    final_summary = combined_result

    # Try to split safety JSON from summary text
    lines = combined_result.strip().split("\n")
    json_end = -1
    brace_count = 0
    in_json = False
    json_lines = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not in_json and stripped.startswith("{"):
            in_json = True
        if in_json:
            json_lines.append(line)
            brace_count += stripped.count("{") - stripped.count("}")
            if brace_count <= 0:
                json_end = i
                break

    if json_lines:
        safety_result = "\n".join(json_lines)
        # Everything after the JSON block is the summary
        remaining = "\n".join(lines[json_end + 1:]).strip()
        if remaining:
            # Strip any "PART 2" or "SUMMARY" header labels
            for prefix in ("PART 2", "SUMMARY", "---", "**SUMMARY**", "**PART 2**"):
                if remaining.upper().startswith(prefix.upper()):
                    remaining = remaining[len(prefix):].strip().lstrip(":").lstrip("-").strip()
            final_summary = remaining

    return {
        "final_summary": final_summary,
        "safety_raw": safety_result,
    }


# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

@app.post("/daily-intent", response_model=DailyIntentResponse)
async def create_daily_intent(req: DailyIntentRequest):
    """Accept natural-language intent and kick off the multi-agent pipeline."""
    plan_id = str(uuid.uuid4())[:12]

    _plan_store[plan_id] = {
        "plan_id": plan_id,
        "intent": req.intent,
        "status": "processing",
        "created_at": datetime.utcnow().isoformat(),
        "result": None,
    }

    try:
        result = await _run_agent_pipeline(plan_id, req.intent)
        _plan_store[plan_id]["status"] = "completed"
        _plan_store[plan_id]["result"] = result
    except Exception as exc:
        _plan_store[plan_id]["status"] = "error"
        _plan_store[plan_id]["error"] = str(exc)
        raise HTTPException(status_code=500, detail=f"Agent pipeline failed: {exc}")

    return DailyIntentResponse(
        plan_id=plan_id,
        status="completed",
        message="Your daily plan is ready.",
    )


@app.get("/daily-plan/{plan_id}")
async def get_daily_plan(plan_id: str):
    """Retrieve the full daily plan with structured data."""
    if plan_id not in _plan_store:
        raise HTTPException(status_code=404, detail="Plan not found.")

    plan = _plan_store[plan_id]
    result = plan.get("result") or {}

    # Parse safety JSON from agent output
    safety_data = None
    safety_raw = result.get("safety_raw", "")
    if safety_raw:
        safety_data = _try_parse_json(safety_raw)

    return JSONResponse(content={
        "plan_id": plan_id,
        "intent": plan["intent"],
        "status": plan["status"],
        "created_at": plan["created_at"],
        "final_summary": result.get("final_summary", ""),
        "calendar_events": list_events(plan_id),
        "tasks": list_tasks(plan_id),
        "safety": safety_data,
    })


@app.get("/daily-status/{plan_id}")
async def get_daily_status(plan_id: str):
    """Get task-tracking progress for a plan."""
    if plan_id not in _plan_store:
        raise HTTPException(status_code=404, detail="Plan not found.")

    plan = _plan_store[plan_id]
    progress = get_plan_progress(plan_id)
    return JSONResponse(content={
        "plan_id": plan_id,
        "status": plan["status"],
        "progress": progress,
    })


@app.post("/complete-task/{plan_id}/{task_id}")
async def complete_task_endpoint(plan_id: str, task_id: str):
    """Mark a task as completed."""
    if plan_id not in _plan_store:
        raise HTTPException(status_code=404, detail="Plan not found.")
    from tools.task_store import complete_task as _complete
    result = _complete(plan_id, task_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Task not found.")
    return JSONResponse(content=result)


# ---------------------------------------------------------------------------
# Accessible Demo UI – served as a single HTML page
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    """Serve the accessibility-first demo UI."""
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host=HOST, port=PORT, reload=True)
