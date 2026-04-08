# 🌅 Guidelight AI

**An AI Daily Independence Copilot for Visually Impaired Users**

Guidelight AI is a multi-agent system built with **Google ADK** and **Gemini 3.1 Flash-Lite** that plans, coordinates, monitors, and protects the daily routines of visually impaired users — using natural language or voice input.

> _"Help me plan my day. I have a doctor's appointment at 2pm, need medication reminders, want time to prepare meals, and need breaks between activities."_

The system generates a structured daily plan, populates a calendar, creates trackable tasks, runs a safety assessment, and delivers a warm, spoken-friendly summary — all in **2 LLM calls**.

---

## Key Features

- **Multi-Agent Pipeline** — 5 specialized ADK agents (Planner, Calendar, Tasks, Safety, Coordinator) work in sequence
- **MCP Tool Integration** — Calendar and Task Store follow the Model Context Protocol interface
- **Safety-First Design** — Detects overloaded schedules, missed medications, risky transitions, and cognitive overload
- **Optimized for Rate Limits** — Only 2 LLM calls per plan (down from 5); calendar/tasks populated programmatically
- **Voice Input & TTS** — Speak your plan via Web Speech API; summary is automatically read aloud
- **Interactive Task Checklist** — Mark tasks as complete with a live progress bar
- **Quick Scenarios** — 6 one-click demo scenarios tailored for visually impaired users (Medical Day, Navigation Day, Assistive Tech Day, etc.)
- **Accessible UI** — WCAG-compliant, keyboard-navigable, screen-reader friendly, high contrast
- **Tabbed Results** — Schedule, Tasks, and Safety panels in a compact tabbed layout

---

## System Architecture

```mermaid
graph TD
    User -->|Voice / Text| AccessibleUI
    AccessibleUI --> FastAPI_Backend
    FastAPI_Backend -->|LLM Call 1| DailyPlanningAgent
    DailyPlanningAgent -->|JSON Plan| FastAPI_Backend
    FastAPI_Backend -->|Programmatic| MCP_Calendar[Calendar MCP Tool]
    FastAPI_Backend -->|Programmatic| MCP_Tasks[Task Store MCP Tool]
    FastAPI_Backend -->|LLM Call 2| CoordinatorAgent[Safety + Summary Agent]
    CoordinatorAgent --> FastAPI_Backend
    FastAPI_Backend -->|Structured JSON| AccessibleUI
```

**Key architectural decisions:**

| Component | Technology | Why |
|-----------|-----------|-----|
| Model | Gemini 3.1 Flash-Lite (Preview) | Most cost-efficient, supports function calling + thinking |
| Orchestration | Google ADK | Native multi-agent coordination with function calling |
| Tool Integration | MCP (Model Context Protocol) | Standardized tool interfaces for Calendar & Task Store |
| Backend | FastAPI (stateless) | Fast async API, auto-generated docs |
| Runtime | Google Cloud Run | Serverless, auto-scaling, pay-per-use |
| State | In-memory (demo) / Firestore (prod) | Persistent workflow state across agent steps |

---

## Agent Tree

| # | Agent | Model | Responsibility |
|---|-------|-------|---------------|
| 1 | **IndependenceCoordinatorAgent** | gemini-3.1-flash-lite-preview | Root orchestrator – interprets intent, runs safety eval, produces final summary |
| 2 | **DailyPlanningAgent** | gemini-3.1-flash-lite-preview | Converts natural-language intent into structured JSON daily plan |
| 3 | **CalendarAndReminderAgent** | gemini-3.1-flash-lite-preview | Schedules events & reminders via MCP Calendar (tools called programmatically) |
| 4 | **TaskTrackingAgent** | gemini-3.1-flash-lite-preview | Creates trackable tasks via MCP Task Store (tools called programmatically) |
| 5 | **SafetyAndRiskAgent** | gemini-3.1-flash-lite-preview | Evaluates plan for overload, missed essentials, risky transitions |

> **Optimization:** Agents 3 & 4 are called programmatically (no LLM) since the structured JSON from Agent 2 provides all the data needed. Agents 1 & 5 are combined into a single LLM call. Total: **2 LLM calls per plan**.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/daily-intent` | Submit natural-language intent, runs full agent pipeline |
| `GET` | `/daily-plan/{plan_id}` | Retrieve the complete plan with structured data |
| `GET` | `/daily-status/{plan_id}` | Get task-tracking progress for a plan |
| `POST` | `/complete-task/{plan_id}/{task_id}` | Mark a task as completed |
| `GET` | `/` | Accessible demo UI |

---

## Quick Start

### Prerequisites

- Python 3.11+
- A Google API key with Gemini API enabled

### 1. Clone & install

```bash
cd guidelight-ai
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your Google API key
```

Required in `.env`:
```
GOOGLE_API_KEY=your-api-key-here
GEMINI_MODEL=gemini-3.1-flash-lite-preview
```

### 3. Run locally

```bash
python3 -m uvicorn app:app --host 0.0.0.0 --port 8080 --reload
# → Open http://localhost:8080
```

### 4. Deploy to Cloud Run

```bash
export GOOGLE_CLOUD_PROJECT=your-project-id
export GOOGLE_CLOUD_LOCATION=us-central1
./deploy.sh
```

---

## Project Structure

```
guidelight-ai/
├── agents/
│   ├── __init__.py
│   ├── coordinator_agent.py     # IndependenceCoordinatorAgent (root)
│   ├── daily_planning_agent.py  # DailyPlanningAgent
│   ├── calendar_agent.py        # CalendarAndReminderAgent
│   ├── task_tracking_agent.py   # TaskTrackingAgent
│   └── safety_agent.py          # SafetyAndRiskAgent
├── tools/
│   ├── __init__.py
│   ├── calendar_tool.py         # MCP Google Calendar stub
│   └── task_store.py            # MCP persistent task store stub
├── static/
│   └── index.html               # Accessible demo UI (tabbed layout)
├── app.py                       # FastAPI backend (2-call optimized pipeline)
├── config.py                    # Centralized configuration
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .env.example
├── deploy.sh                    # Cloud Run deployment script
├── DEMO_SCRIPT.md               # Demo narration script
├── DEVPOST.md                   # Devpost submission text
└── README.md
```

---

## Demo Scenarios

Click any scenario card in the UI to instantly populate and run:

| Scenario | Description |
|----------|-------------|
| 🏥 **Medical Day** | Doctor visit, medication reminders, pharmacy call |
| ☕ **Social Day** | Coffee with friend, groceries, family call |
| 🏡 **Restful Day** | Home-focused, audio books, extra rest breaks |
| ⚡ **Busy Day** | Physiotherapy, work call, yoga, errands |
| 🦮 **Navigation Day** | Guide dog walk, mobility training, route practice |
| 🔊 **Assistive Tech Day** | Screen reader setup, braille display, voice assistant |

---

## Accessibility Features

- Semantic HTML only (no frameworks)
- WCAG-compliant high-contrast dark theme
- Large fonts (base 1.1rem, Inter)
- Full keyboard navigation with skip-to-content link
- ARIA labels, roles, and live regions throughout
- Screen-reader friendly spoken summaries
- Voice input via Web Speech API
- Auto text-to-speech for plan summaries
- Ctrl/Cmd+Enter keyboard shortcut

---

## Rate Limit Optimization

| Metric | Before | After |
|--------|--------|-------|
| LLM calls per plan | 5 | **2** |
| Token usage | ~8K input/plan | ~3K input/plan |
| Plans per day (free tier) | ~4 | **~10** |
| Model | gemini-2.5-flash | **gemini-3.1-flash-lite-preview** |

---

## License

MIT
