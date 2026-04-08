# Guidelight AI – Devpost Submission

## Project Title

**Guidelight AI – Multi-Agent Productivity Assistant for Visually Impaired Users**

---

## Inspiration

Over 2.2 billion people worldwide live with some form of vision impairment. While screen readers and basic assistive tools exist, they can **read** information but cannot **reason** about it. A visually impaired person planning their day must juggle fragmented tools that don't coordinate with each other. We built Guidelight AI to solve this with a multi-agent system that plans, schedules, tracks, and safeguards daily routines — all through natural language or voice.

---

## What it does

Guidelight AI is a **multi-agent productivity assistant** that turns plain-language input into a complete, safe daily plan:

1. **Generates a structured daily schedule** with time-sequenced activities, meals, medication reminders, and rest breaks
2. **Populates a visual calendar timeline** with color-coded events by category (medication, meals, appointments, rest, exercise)
3. **Creates an interactive task checklist** with a live progress bar — users can mark tasks complete as they go
4. **Runs a safety assessment** — flags overloaded schedules, missed medication, risky transitions, and cognitive overload, with a risk level badge and recommendations
5. **Delivers a spoken-friendly summary** automatically read aloud via browser TTS
6. **Accepts voice input** via Web Speech API — fully hands-free operation

The UI provides **6 one-click demo scenarios** tailored for visually impaired users:
- 🏥 Medical Day — doctor visit, medication, pharmacy call
- ☕ Social Day — coffee with friend, groceries, family call
- 🏡 Restful Day — home-focused, audio books, extra rest
- ⚡ Busy Day — physiotherapy, work call, yoga, errands
- 🦮 Navigation Day — guide dog walk, mobility training, route practice
- 🔊 Assistive Tech Day — screen reader setup, braille display, voice assistant

---

## How we built it

### Multi-Agent Architecture (Google ADK)

Five specialized agents built with the **Google Agent Development Kit (ADK)**:

| Agent | Role |
|-------|------|
| **IndependenceCoordinatorAgent** | Root orchestrator — runs safety evaluation and produces the final spoken-friendly summary |
| **DailyPlanningAgent** | Converts natural-language intent into a structured JSON daily schedule with constraints and assumptions |
| **CalendarAndReminderAgent** | MCP Calendar tool — schedules events with conflict detection (called programmatically from plan JSON) |
| **TaskTrackingAgent** | MCP Task Store tool — creates trackable tasks with categories and priorities (called programmatically) |
| **SafetyAndRiskAgent** | Evaluates plan for overload, missed essentials, risky transitions, cognitive load, and time safety |

### Optimized Pipeline (2 LLM Calls)

To minimize token usage and rate limit impact, the pipeline is optimized:

- **LLM Call 1 (Planner):** Generates the structured JSON daily plan
- **Programmatic (no LLM):** Calendar events and tasks are populated directly from the JSON — no need for LLM-driven tool calling
- **LLM Call 2 (Coordinator):** Combines safety evaluation + spoken summary into a single response

This reduces API calls from 5 to **2 per plan request**, cutting token usage by ~70%.

### Technology Stack

| Component | Technology |
|-----------|-----------|
| Model | **Gemini 3.1 Flash-Lite** (Preview) — most cost-efficient, supports function calling + thinking |
| Framework | Google Agent Development Kit (ADK) — native multi-agent orchestration |
| Tools | Model Context Protocol (MCP) — Calendar and Task Store with in-memory backends |
| Backend | FastAPI (Python 3.11) — async, stateless, 5 API endpoints |
| Frontend | Semantic HTML + CSS — tabbed results layout, no frameworks |
| Voice | Web Speech API (input) + SpeechSynthesis (TTS output) |
| Deployment | Docker + Google Cloud Run |

### API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/daily-intent` | Submit intent, runs the full agent pipeline |
| `GET` | `/daily-plan/{plan_id}` | Retrieve plan with calendar events, tasks, safety data |
| `GET` | `/daily-status/{plan_id}` | Task progress stats |
| `POST` | `/complete-task/{plan_id}/{task_id}` | Mark a task as done |
| `GET` | `/` | Accessible demo UI |

---

## Challenges we ran into

- **Rate limits:** Free-tier Gemini quota forced us to optimize from 5 LLM calls down to 2, replacing two agent calls with programmatic tool execution
- **Non-deterministic orchestration:** LLM-driven sub-agent dispatch was unreliable for demos, so we designed a strict sequential pipeline
- **Combined response parsing:** Merging safety JSON + spoken summary into one LLM call required robust JSON extraction from mixed text output
- **Accessibility-first design:** ARIA roles, keyboard navigation, skip links, and screen-reader-friendly spoken output had to be designed from the start

---

## Accomplishments we're proud of

- **5 ADK agents** with clear responsibilities, using MCP-compliant tool interfaces
- **2-call optimized pipeline** — 60% fewer API calls, ~70% fewer tokens vs naive approach
- A genuinely **accessible UI** — keyboard-navigable, voice input/output, high-contrast, tabbed layout
- **Interactive task completion** — users mark tasks done, progress bar updates live
- **Safety Agent** that proactively flags risks like missed medication, schedule overload, and risky transitions
- **6 scenario cards** specifically designed for visually impaired daily routines

---

## What we learned

- Multi-agent systems need deterministic orchestration for reliable demos — LLM-driven dispatch is too unpredictable
- Many LLM calls can be replaced with programmatic logic when structured data (JSON) is available
- Accessibility must be an architecture decision, not an afterthought
- Gemini 3.1 Flash-Lite provides excellent cost/performance for agentic workflows with function calling

---

## What's next for Guidelight AI

- **Real Google Calendar integration** via OAuth + Calendar API (replacing the in-memory stub)
- **Caregiver dashboard** — secondary interface for family members to monitor daily progress
- **Learning & adaptation** — personalize plans based on historical patterns
- **Wearable integration** — connect to smart glasses for real-time navigation
- **Emergency escalation** — automatic alerts when critical tasks like medication are missed

---

## Built With

- Google Agent Development Kit (ADK)
- Gemini 3.1 Flash-Lite (Preview)
- Model Context Protocol (MCP)
- Python 3.11
- FastAPI
- Web Speech API
- Semantic HTML / CSS
- Docker / Google Cloud Run

---

## Try it out

- **Repository:** [github.com/your-username/guidelight-ai](https://github.com/your-username/guidelight-ai)
- **Live Demo:** Deployed on Google Cloud Run (see README for URL)
