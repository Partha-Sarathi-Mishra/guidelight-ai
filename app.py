"""Guidelight AI – FastAPI Backend.

Exposes the API endpoints and serves the accessible demo UI.
Runs each ADK agent sequentially for deterministic, demo-reliable execution.
Features: SSE streaming, conversational follow-up, adaptive replanning, SOS.
"""

from __future__ import annotations

import json
import os
import uuid
import asyncio
import time
from datetime import datetime
from pathlib import Path
from typing import Any

_BASE_DIR = Path(__file__).resolve().parent

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google import genai

from agents.daily_planning_agent import DailyPlanningAgent
from agents.calendar_agent import CalendarAndReminderAgent
from agents.task_tracking_agent import TaskTrackingAgent
from agents.safety_agent import SafetyAndRiskAgent
from agents.coordinator_agent import IndependenceCoordinatorAgent
from tools.task_store import get_plan_progress, list_tasks, create_task, get_overdue_tasks
from tools.calendar_tool import list_events, schedule_event, check_conflicts
from config import HOST, PORT, GEMINI_MODEL, GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Guidelight AI",
    description="AI Daily Independence Copilot for Visually Impaired Users",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory plan store (plan_id → plan metadata + results)
_plan_store: dict[str, dict[str, Any]] = {}

# Conversation history per plan (for follow-up chat)
_chat_history: dict[str, list[dict[str, str]]] = {}

# ADK session service – shared across all agent runners
session_service = InMemorySessionService()

# Performance metrics
_metrics: dict[str, list[float]] = {"pipeline_ms": [], "llm_calls": []}

# One runner per agent for deterministic sequential execution
_agents = {
    "planner": Runner(agent=DailyPlanningAgent, app_name="guidelight_ai", session_service=session_service),
    "calendar": Runner(agent=CalendarAndReminderAgent, app_name="guidelight_ai", session_service=session_service),
    "tasks": Runner(agent=TaskTrackingAgent, app_name="guidelight_ai", session_service=session_service),
    "safety": Runner(agent=SafetyAndRiskAgent, app_name="guidelight_ai", session_service=session_service),
    "coordinator": Runner(agent=IndependenceCoordinatorAgent, app_name="guidelight_ai", session_service=session_service),
}

# Direct Gemini client for summary/chat/replan – bypasses ADK Runner overhead
_genai_client = genai.Client(vertexai=True, project=GOOGLE_CLOUD_PROJECT, location=GOOGLE_CLOUD_LOCATION)


async def _call_gemini(prompt: str, max_retries: int = 3) -> str:
    """Call Gemini directly via google-genai (no ADK Runner). Fast & reliable."""
    for attempt in range(max_retries):
        try:
            response = await asyncio.to_thread(
                _genai_client.models.generate_content,
                model=GEMINI_MODEL,
                contents=prompt,
            )
            return response.text.strip()
        except Exception as exc:
            if "429" in str(exc) and attempt < max_retries - 1:
                wait = (attempt + 1) * 15
                print(f"[Rate limited] Retrying Gemini in {wait}s (attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(wait)
                continue
            raise


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


class ChatRequest(BaseModel):
    message: str


class ReplanRequest(BaseModel):
    reason: str
    current_time: str = ""


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
    combined_result = await _call_gemini(combined_prompt)

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
# NEW: Streaming Pipeline (Server-Sent Events)
# ---------------------------------------------------------------------------

@app.post("/daily-intent-stream")
async def create_daily_intent_stream(req: DailyIntentRequest):
    """Stream the agent pipeline progress via SSE for real-time UI updates."""
    plan_id = str(uuid.uuid4())[:12]

    _plan_store[plan_id] = {
        "plan_id": plan_id,
        "intent": req.intent,
        "status": "processing",
        "created_at": datetime.utcnow().isoformat(),
        "result": None,
    }

    async def event_generator():
        user_id = f"user_{plan_id}"
        today = datetime.utcnow().strftime("%Y-%m-%d")
        t_start = time.time()

        try:
            # Step 1: Planning
            yield {"event": "step", "data": json.dumps({"step": "planner", "status": "active"})}
            planning_prompt = (
                f"Today is {today}. The user said:\n\"{req.intent}\"\n\n"
                "Generate a structured JSON daily plan. Output ONLY valid JSON."
            )
            plan_json = await _run_single_agent("planner", user_id, planning_prompt)
            yield {"event": "step", "data": json.dumps({"step": "planner", "status": "done"})}

            # Step 2: Calendar (programmatic)
            yield {"event": "step", "data": json.dumps({"step": "calendar", "status": "active"})}
            _populate_calendar_and_tasks(plan_id, plan_json, today)
            yield {"event": "step", "data": json.dumps({"step": "calendar", "status": "done"})}

            # Step 3: Tasks (programmatic)
            yield {"event": "step", "data": json.dumps({"step": "tasks", "status": "active"})}
            await asyncio.sleep(0.1)  # Small pause for visual feedback
            yield {"event": "step", "data": json.dumps({"step": "tasks", "status": "done"})}

            # Step 4 + 5: Safety + Summary (combined LLM call via SummaryAgent)
            yield {"event": "step", "data": json.dumps({"step": "safety", "status": "active"})}
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
            combined_result = await _call_gemini(combined_prompt)
            yield {"event": "step", "data": json.dumps({"step": "safety", "status": "done"})}
            yield {"event": "step", "data": json.dumps({"step": "summary", "status": "active"})}

            # Parse combined response
            safety_result = ""
            final_summary = combined_result
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
                remaining = "\n".join(lines[json_end + 1:]).strip()
                if remaining:
                    for prefix in ("PART 2", "SUMMARY", "---", "**SUMMARY**", "**PART 2**"):
                        if remaining.upper().startswith(prefix.upper()):
                            remaining = remaining[len(prefix):].strip().lstrip(":").lstrip("-").strip()
                    final_summary = remaining

            elapsed_ms = round((time.time() - t_start) * 1000)
            _metrics["pipeline_ms"].append(elapsed_ms)
            _metrics["llm_calls"].append(2)

            result = {"final_summary": final_summary, "safety_raw": safety_result}
            _plan_store[plan_id]["status"] = "completed"
            _plan_store[plan_id]["result"] = result

            # Initialize chat history with plan context
            _chat_history[plan_id] = [{
                "role": "system",
                "content": f"Plan context: {plan_json}\nSafety: {safety_result}"
            }]

            yield {"event": "step", "data": json.dumps({"step": "summary", "status": "done"})}

            # Final complete event with all data
            safety_data = _try_parse_json(safety_result)
            yield {"event": "complete", "data": json.dumps({
                "plan_id": plan_id,
                "final_summary": final_summary,
                "calendar_events": list_events(plan_id),
                "tasks": list_tasks(plan_id),
                "safety": safety_data,
                "metrics": {"pipeline_ms": elapsed_ms, "llm_calls": 2},
            })}

        except Exception as exc:
            import traceback
            traceback.print_exc()
            _plan_store[plan_id]["status"] = "error"
            _plan_store[plan_id]["error"] = str(exc)
            yield {"event": "error", "data": json.dumps({"error": str(exc)})}

    return EventSourceResponse(event_generator())


# ---------------------------------------------------------------------------
# NEW: Conversational Follow-up Chat
# ---------------------------------------------------------------------------

@app.post("/chat/{plan_id}")
async def chat_with_plan(plan_id: str, req: ChatRequest):
    """Conversational follow-up: ask about your plan, request changes, get guidance."""
    if plan_id not in _plan_store:
        raise HTTPException(status_code=404, detail="Plan not found.")

    plan = _plan_store[plan_id]
    result = plan.get("result") or {}
    tasks = list_tasks(plan_id)
    events = list_events(plan_id)
    progress = get_plan_progress(plan_id)
    overdue = get_overdue_tasks(plan_id)

    # Build context from plan state
    context = (
        "You are Guidelight AI's conversational assistant for visually impaired users.\n"
        "The user has an active daily plan. Here is the current state:\n\n"
        f"Plan Summary: {result.get('final_summary', 'N/A')}\n"
        f"Tasks ({progress['completed']}/{progress['total_tasks']} done): "
        f"{json.dumps([{'title': t['title'], 'time': t['scheduled_time'][11:16], 'status': t['status']} for t in tasks], indent=0)}\n"
        f"Calendar Events: {len(events)} scheduled\n"
        f"Overdue Items: {len(overdue)}\n\n"
    )

    # Add conversation history
    history = _chat_history.get(plan_id, [])
    history_text = "\n".join([f"{m['role']}: {m['content']}" for m in history[-6:]])  # Last 6 messages

    prompt = (
        f"{context}\n"
        f"Conversation history:\n{history_text}\n\n"
        f"User says: \"{req.message}\"\n\n"
        "Respond helpfully. Be conversational, warm, and concise. "
        "If the user asks 'what's next', tell them their next upcoming task. "
        "If they ask to cancel/skip/reschedule something, acknowledge it clearly. "
        "If they seem stressed, be extra reassuring. "
        "Keep responses under 3 sentences. Speak naturally — this will be read aloud."
    )

    response = await _call_gemini(prompt)

    # Store in history
    _chat_history.setdefault(plan_id, []).append({"role": "user", "content": req.message})
    _chat_history[plan_id].append({"role": "assistant", "content": response})

    return JSONResponse(content={
        "response": response,
        "plan_id": plan_id,
        "progress": progress,
    })


# ---------------------------------------------------------------------------
# NEW: Adaptive Replanning
# ---------------------------------------------------------------------------

@app.post("/replan/{plan_id}")
async def adaptive_replan(plan_id: str, req: ReplanRequest):
    """Intelligently restructure remaining plan when circumstances change."""
    if plan_id not in _plan_store:
        raise HTTPException(status_code=404, detail="Plan not found.")

    plan = _plan_store[plan_id]
    tasks = list_tasks(plan_id)
    events = list_events(plan_id)
    current_time = req.current_time or datetime.utcnow().strftime("%H:%M")
    today = datetime.utcnow().strftime("%Y-%m-%d")

    # Separate completed vs remaining
    pending_tasks = [t for t in tasks if t["status"] == "pending"]
    completed_tasks = [t for t in tasks if t["status"] == "completed"]

    replan_prompt = (
        f"You are the Daily Planning Agent for Guidelight AI (visually impaired users).\n"
        f"The current time is {current_time}.\n"
        f"The user's original plan had these REMAINING tasks:\n"
        f"{json.dumps([{'title': t['title'], 'time': t['scheduled_time'][11:16], 'category': t['category'], 'priority': t['priority']} for t in pending_tasks])}\n\n"
        f"Already completed: {[t['title'] for t in completed_tasks]}\n\n"
        f"The user says: \"{req.reason}\"\n\n"
        "Generate a REVISED JSON daily plan for the remaining day starting from now. "
        "Keep all critical items (medication, appointments). "
        "Reschedule lower-priority items as needed. "
        "Maintain rest breaks. Output ONLY valid JSON in the same schema:\n"
        '{"daily_schedule":[{"time":"HH:MM","end_time":"HH:MM","activity":"...","category":"...","priority":"..."}],'
        '"reminders":[],"constraints":[],"assumptions":[]}'
    )

    t_start = time.time()
    new_plan_json = await _run_single_agent("planner", f"replan_{plan_id}", replan_prompt)

    # Clear existing pending calendar events and tasks, repopulate
    from tools.calendar_tool import _calendar_store
    from tools.task_store import _task_store
    _calendar_store[plan_id] = [e for e in _calendar_store.get(plan_id, []) if e["start_time"][:16].replace("T", " ") < f"{today} {current_time}"]
    _task_store[plan_id] = [t for t in _task_store.get(plan_id, []) if t["status"] == "completed"]

    _populate_calendar_and_tasks(plan_id, new_plan_json, today)

    # Run safety on new plan
    safety_prompt = (
        "You are the Safety Agent. Evaluate this REVISED plan for a visually impaired user.\n"
        f"Plan: {new_plan_json}\n"
        f"Reason for replanning: {req.reason}\n"
        "Output only JSON: "
        '{"risk_level":"low|medium|high","alerts":[],"recommendations":[],"overall_assessment":"..."}'
    )
    safety_result = await _call_gemini(safety_prompt)
    safety_data = _try_parse_json(safety_result)

    elapsed_ms = round((time.time() - t_start) * 1000)

    return JSONResponse(content={
        "plan_id": plan_id,
        "status": "replanned",
        "reason": req.reason,
        "calendar_events": list_events(plan_id),
        "tasks": list_tasks(plan_id),
        "safety": safety_data,
        "metrics": {"replan_ms": elapsed_ms, "llm_calls": 2},
    })


# ---------------------------------------------------------------------------
# NEW: Emergency SOS
# ---------------------------------------------------------------------------

@app.get("/sos/{plan_id}")
async def emergency_sos(plan_id: str):
    """Generate a shareable emergency context summary for caregivers."""
    if plan_id not in _plan_store:
        raise HTTPException(status_code=404, detail="Plan not found.")

    plan = _plan_store[plan_id]
    tasks = list_tasks(plan_id)
    events = list_events(plan_id)
    progress = get_plan_progress(plan_id)
    overdue = get_overdue_tasks(plan_id)
    now = datetime.utcnow()

    # Find current/next activity
    current_activity = None
    next_activity = None
    now_str = now.strftime("%H:%M")
    for ev in sorted(events, key=lambda e: e["start_time"]):
        ev_time = ev["start_time"][11:16]
        ev_end = ev["end_time"][11:16]
        if ev_time <= now_str <= ev_end:
            current_activity = ev["title"]
        elif ev_time > now_str and not next_activity:
            next_activity = ev["title"]

    # Medication status
    med_tasks = [t for t in tasks if t["category"] == "medication"]
    med_taken = [t for t in med_tasks if t["status"] == "completed"]
    med_pending = [t for t in med_tasks if t["status"] == "pending"]

    sos_context = {
        "timestamp": now.isoformat(),
        "plan_id": plan_id,
        "current_activity": current_activity or "Between activities",
        "next_activity": next_activity or "No more activities scheduled",
        "progress": f"{progress['completed']}/{progress['total_tasks']} tasks done",
        "overdue_items": [t["title"] for t in overdue],
        "medication_status": {
            "taken": [t["title"] for t in med_taken],
            "pending": [t["title"] for t in med_pending],
        },
        "original_plan_intent": plan.get("intent", ""),
        "spoken_summary": (
            f"Emergency context: The user is currently at '{current_activity or 'between activities'}'. "
            f"They have completed {progress['completed']} of {progress['total_tasks']} planned tasks. "
            f"{'They have ' + str(len(overdue)) + ' overdue items. ' if overdue else ''}"
            f"Medication: {len(med_taken)} taken, {len(med_pending)} pending. "
            f"Next scheduled: {next_activity or 'nothing remaining'}."
        ),
    }

    return JSONResponse(content=sos_context)


# ---------------------------------------------------------------------------
# NEW: Health Check & Metrics
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    """Production-ready health check with performance metrics."""
    avg_pipeline = (
        round(sum(_metrics["pipeline_ms"]) / len(_metrics["pipeline_ms"]))
        if _metrics["pipeline_ms"] else 0
    )
    return JSONResponse(content={
        "status": "healthy",
        "version": "2.0.0",
        "model": GEMINI_MODEL,
        "agents": 5,
        "plans_created": len(_plan_store),
        "avg_pipeline_ms": avg_pipeline,
        "uptime_features": [
            "streaming_sse", "conversational_chat",
            "adaptive_replanning", "emergency_sos",
            "safety_assessment", "voice_io"
        ],
    })


# ---------------------------------------------------------------------------
# Accessible Demo UI – served as a single HTML page
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    """Serve the accessibility-first demo UI."""
    with open(_BASE_DIR / "static" / "index.html", "r") as f:
        return HTMLResponse(content=f.read())


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host=HOST, port=PORT, reload=True)
