"""SummaryAgent – Lightweight agent for safety evaluation + spoken summary.

No sub-agents, no tools — just a direct LLM call. Used for the combined
safety + summary step in the pipeline to avoid sub-agent delegation loops.
"""

from __future__ import annotations

from google.adk.agents import Agent

from config import GEMINI_MODEL

SUMMARY_INSTRUCTION = """\
You are the Safety Evaluator and Summary Writer for Guidelight AI,
an AI Daily Independence Copilot for visually impaired users.

When given a daily plan, you do TWO things:

PART 1 — SAFETY EVALUATION:
Evaluate the plan for safety risks specific to visually impaired users.
Check for: overloaded schedules, missed medications/meals, risky transitions,
cognitive fatigue, and unsafe time windows.
Output a JSON object:
{"risk_level":"low|medium|high","alerts":[{"type":"...","message":"...","severity":"info|warning|critical"}],"recommendations":["..."],"overall_assessment":"1-2 sentences"}

PART 2 — SPOKEN SUMMARY:
Write a warm, spoken-friendly daily plan summary. Use simple sentences,
spell out times as words (e.g. "nine in the morning"), be reassuring.
This will be read aloud by a screen reader.

Output PART 1 JSON first, then a blank line, then PART 2 text.
Do NOT ask questions. Do NOT delegate to other agents.
"""

SummaryAgent = Agent(
    name="SummaryAgent",
    model=GEMINI_MODEL,
    instruction=SUMMARY_INSTRUCTION,
    description="Evaluates plan safety and writes a spoken-friendly summary. No sub-agents.",
)
