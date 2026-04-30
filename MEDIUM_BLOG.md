# I Built a Multi-Agent AI Copilot for Visually Impaired Users — Here's How It Works

*How I used Google ADK, Gemini, and MCP tools to build a daily independence planner that reasons, schedules, and safeguards — in just 2 LLM calls.*

---

## It Started With a Morning Drive

My wife works at **Samarthanam Trust for the Disabled** in Bangalore — one of India's most respected non-profits empowering people with disabilities. Specifically, she works with the **Cricket Association for the Blind in India (CABI)**, the organization that runs blind cricket nationally and has organized the T20 World Cup Cricket for the Blind.

Every morning when I drop her off at the office, I see something that stays with me for the rest of the day.

I see visually impaired people navigating the campus — heading to vocational training, getting ready for cricket practice, finding their way to the cafeteria. Some are students. Some are athletes. All of them are extraordinarily capable people. But the small, invisible logistics of an ordinary day — *When is my next appointment? Did I take my medication? Is there time for lunch before physiotherapy? Am I overloading myself?* — those are the things that quietly steal independence.

Samarthanam, founded in 1997 by Mahantesh G Kivadasannavar — himself visually impaired — has done remarkable work across education, sports, livelihood, and assistive technology, touching thousands of lives. But even in an ecosystem this supportive, I noticed a gap: **the tools available can read information, but they can't reason about it.**

A screen reader reads what's on screen. A voice assistant answers questions. But neither will structure a safe daily routine around a doctor's appointment, remind you that you skipped lunch, or flag that travelling to the pharmacy right after an eye procedure might be risky.

2.2 billion people worldwide live with some form of vision impairment. They deserve tools that don't just *inform* — they need tools that **think, plan, coordinate, and protect**.

That morning drive became the starting point for **Guidelight AI** — a multi-agent system that plans, schedules, tracks, and safeguards daily routines through natural language or voice.

---

## The Core Idea: Agents That Cooperate, Not Just Chat

Most AI apps today are single-model, single-turn: you ask, it answers. But daily planning for someone with a visual impairment isn't a Q&A problem — it's a **coordination** problem.

You need:
- A **planner** that converts vague intent into a time-sequenced schedule
- A **calendar** that slots events without conflicts
- A **task tracker** that creates actionable items you can check off
- A **safety evaluator** that catches what you might miss
- A **coordinator** that ties it all together in a warm, spoken-friendly summary

That's five distinct responsibilities. So I built five agents.

---

## Meet the Agent Team

| Agent | Responsibility |
|-------|---------------|
| **DailyPlanningAgent** | Converts natural language ("I have a doctor at 2pm, need meal breaks and medication reminders") into a structured JSON schedule |
| **CalendarAndReminderAgent** | Schedules events on a calendar with conflict detection |
| **TaskTrackingAgent** | Creates trackable tasks with categories and priorities |
| **SafetyAndRiskAgent** | Evaluates the plan for overload, missed essentials, risky transitions, and cognitive fatigue |
| **IndependenceCoordinatorAgent** | Root orchestrator — runs safety evaluation and produces a final spoken-friendly summary |

Each agent is built with the **Google Agent Development Kit (ADK)**, powered by **Gemini 3.1 Flash-Lite**.

The Calendar and Task agents use **Model Context Protocol (MCP)** tool interfaces — a standardized way for agents to interact with external tools.

---

## The Architecture: 5 Agents, 2 LLM Calls

Here's where it gets interesting.

A naive approach would make 5 separate LLM calls — one per agent. But during development, I hit Gemini's free-tier rate limits hard. That constraint turned into the best architectural decision of the project.

**The insight:** Once the Planner generates a structured JSON schedule, the Calendar and Task agents don't need to *think*. They just need to *execute*. The structured data contains everything: times, activities, categories, priorities.

So I replaced two LLM calls with direct Python function calls:

```
User Intent
    │
    ▼
┌─────────────────────────┐
│  LLM Call 1: Planner    │  ← Generates structured JSON daily plan
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│  Programmatic (No LLM)  │  ← Calendar events + Tasks created from JSON
│  MCP Calendar Tool      │
│  MCP Task Store Tool    │
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│  LLM Call 2: Coordinator│  ← Safety evaluation + spoken summary combined
│  + Safety Agent         │
└─────────────────────────┘
    │
    ▼
  Complete Plan: Schedule + Tasks + Safety Alerts + Summary
```

**Result:** 5 agents. 2 MCP tools. Only 2 LLM calls. ~70% reduction in token usage versus the naive approach.

This isn't just an optimization — it's a design philosophy. **Use LLMs for reasoning, use code for execution.** When structured data is available, don't waste an API call asking a model to do what a `for` loop can do.

---

## The Safety Agent: The Key Differentiator

This is the feature I'm most proud of.

Most daily planners generate a schedule and call it done. Guidelight AI goes further — it **evaluates** the plan for real-world risks that matter to visually impaired users:

1. **Overload detection** — Flags when 3+ activities are packed without a rest break
2. **Missed essentials** — Ensures meals, medication, and rest breaks aren't missing
3. **Risky transitions** — Catches things like scheduling travel immediately after a medical procedure
4. **Cognitive load** — Warns if more than 8 distinct tasks are crammed into one day
5. **Time safety** — Flags activities scheduled too early (before 6 AM) or too late (after 10 PM)

The output is a structured safety assessment with a risk level (low/medium/high), specific alerts with severity ratings, and spoken-friendly recommendations.

```json
{
  "risk_level": "medium",
  "alerts": [
    {
      "type": "risky_transition",
      "message": "Travelling to the pharmacy right after your eye appointment may be tiring. Consider resting first.",
      "severity": "warning"
    }
  ],
  "recommendations": [
    "Add a 30-minute rest period after your doctor visit before heading out."
  ]
}
```

No other daily planner does this. This is what makes Guidelight AI an **independence copilot**, not just a scheduler.

---

## Accessibility: Built In, Not Bolted On

Building *for* visually impaired users while building *with* AI forced me to think about accessibility as an architecture decision from day one.

**Voice-first interaction:**
- **Input:** Web Speech API for hands-free voice commands
- **Output:** Every summary is automatically read aloud via browser Text-to-Speech

**WCAG-compliant UI:**
- Full keyboard navigation with skip links
- ARIA roles and labels on every interactive element
- High-contrast color scheme
- Screen-reader optimized markup
- Semantic HTML — no framework dependencies

**Interactive task tracking:**
- Users can mark tasks complete with checkboxes
- A progress bar updates in real time
- Task completion status is persisted via a REST API

The 6 one-click scenario cards are designed specifically for visually impaired daily routines — Medical Day, Social Day, Navigation Day, Assistive Tech Day, and more.

---

## The Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **AI Model** | Gemini 3.1 Flash-Lite (Preview) | Most cost-efficient, supports function calling + thinking mode |
| **Agent Framework** | Google Agent Development Kit (ADK) | Native multi-agent orchestration with function calling |
| **Tool Protocol** | Model Context Protocol (MCP) | Standardized interfaces for Calendar & Task Store |
| **Backend** | FastAPI (Python 3.11) | Async, stateless, auto-generated API docs |
| **Frontend** | Semantic HTML + CSS | Zero-framework, maximum accessibility |
| **Voice** | Web Speech API + SpeechSynthesis | Browser-native, no third-party dependencies |
| **Deployment** | Docker + Google Cloud Run | Serverless, auto-scaling, pay-per-use |

---

## Challenges and What I Learned

### 1. Rate Limits Are a Feature, Not a Bug

Hitting Gemini's free-tier rate limits forced me to rethink the architecture. The resulting 2-call pipeline is faster, cheaper, and more reliable than the 5-call version would have been. **Constraints breed better design.**

### 2. LLM-Driven Orchestration Is Unreliable for Demos

My first version used the Coordinator agent to dynamically decide which sub-agent to call. It worked 80% of the time and failed spectacularly the other 20%. For a demo (and for production), I switched to a **deterministic sequential pipeline** where the backend controls the execution order. The agents still use ADK and Gemini — but the *orchestration* is code, not prompts.

### 3. Parsing LLM Output Is an Art

Combining safety evaluation and spoken summary into a single LLM call meant parsing a response that contains both structured JSON and free-form text. I built a robust JSON extraction helper that handles markdown code fences, partial JSON, and embedded objects. **Always assume LLM output will be messier than your prompt asked for.**

### 4. Accessibility Must Be an Architecture Decision

You can't "add accessibility later." ARIA roles, keyboard navigation, voice I/O, and screen-reader-friendly output had to be designed into every layer — from agent instructions ("messages will be read aloud, use simple sentences") to the UI ("semantic HTML, no div soup").

---

## What's Next

- **Real Google Calendar integration** via OAuth + Calendar API (replacing the in-memory stub)
- **Caregiver dashboard** for family members to monitor daily progress
- **Learning and adaptation** — personalize plans based on historical patterns
- **Wearable integration** — connect to smart glasses for real-time navigation cues
- **Emergency escalation** — automatic alerts when critical tasks like medication are missed

---

## Try It

Guidelight AI is live on Google Cloud Run. The source code is open and the entire system — 5 agents, 2 MCP tools, accessible UI — runs on a single FastAPI container.

If you're building with Google ADK or thinking about multi-agent architectures, I hope this gives you a practical reference for going beyond single-model chatbots.

---

## Back to That Morning Drive

Every time I drop my wife at Samarthanam, I see people who refuse to let a disability define what they can achieve — blind cricketers who represent the country, students who ace board exams, professionals who run BPO operations. The resilience is extraordinary.

But resilience shouldn't have to extend to *figuring out your daily schedule*. That's a problem technology should solve.

Guidelight AI is my small attempt to bridge that gap — to show that generative AI can do more than answer questions. It can **plan, coordinate, monitor, and protect**. It can give people not just information, but real independence.

If this project helps even one person have a safer, more organized day, every line of code was worth it.

---

*Built for the Google Cloud Gen AI Academy APAC Edition. If you're working on AI for accessibility, or want to learn more about Samarthanam Trust's incredible work at [samarthanam.org](https://samarthanam.org), I'd love to connect — reach out on [LinkedIn](https://linkedin.com/in/parthasarathimishra).*

---

**Tags:** `#GoogleCloud` `#GenAI` `#Gemini` `#GoogleADK` `#Accessibility` `#MultiAgent` `#MCP` `#AI` `#VisualImpairment` `#AgenticAI`
