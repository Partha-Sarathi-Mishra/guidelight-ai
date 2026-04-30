# Guidelight AI – Demo Script (3 Minutes)

**Total Duration:** 3:00  
**Recording tool:** QuickTime (Cmd+Shift+5) or OBS  
**Resolution:** 1920×1080, browser full-screen  
**URL:** http://localhost:8080 (local) or Cloud Run URL (deployed)

> 💡 **Pre-record tips:**
> - Open the URL before recording. Do one dry run.
> - Keep narration calm, clear, and slightly slow — you're presenting an accessibility product.
> - Have a plan already generated in another tab as backup (in case of API latency).

---

## 🎬 SCENE 1 — Hook + Problem (0:00 – 0:25)

**SCREEN:** Show the landing page hero section with badges: Gemini 2.5 Flash, 5 AI Agents, MCP Tools, Real-time Streaming.  
**ACTION:** Slowly scroll to reveal the 6 scenario cards.

> **SAY:**
>
> "Hi, I'm Parthasarathi. This is **Guidelight AI** — an AI-powered
> daily independence copilot for visually impaired users.
>
> 2.2 billion people worldwide have vision impairment. Assistive tools
> today can *read* — but they can't *reason*, *plan*, or *watch out
> for your safety*.
>
> Guidelight AI changes that. Built with **Google ADK**, **MCP tools**,
> and **Gemini 2.5 Flash on Vertex AI** — it plans, schedules, tracks,
> and *safeguards* your entire day using 5 specialized AI agents."

---

## 🎬 SCENE 2 — Live Demo: SSE Pipeline (0:25 – 1:00)

**ACTION:** Click the **"🏥 Medical Day"** scenario card. Text auto-fills.

> **SAY:**
>
> "Let me show you. I'll click the Medical Day scenario — a real-world
> request from a visually impaired user with medications, a doctor visit,
> and daily routines."

**ACTION:** Click **🚀 Plan My Day**.  
**SCREEN:** Watch the **5-step animated SSE pipeline** stream in real-time.

> **SAY:**
>
> "Watch the pipeline — it streams in real-time using Server-Sent Events.
> Under the hood, **5 ADK agents** orchestrate the plan. But here's the
> optimization — we reduced it to just **2 LLM calls**. Calendar events
> and tasks are created *programmatically* through MCP tools — zero
> extra API calls. That's a 70% token reduction."

**SCREEN:** Results appear. Point out:
- ⚡ **Metrics bar** — pipeline time in ms, 2 LLM calls, 5 agents
- 📆 **GCal sync badge** — "X/Y synced to Google Calendar"
- 🛡️ **Safety banner** (green/yellow/red) above all results

> **SAY:**
>
> "Notice three things: the metrics bar shows real performance data —
> under 3 seconds, just 2 LLM calls. The green banner is our **Safety
> Agent** — it assessed this plan and found it safe. And those calendar
> events? They're synced to an **actual Google Calendar** via OAuth2."

---

## 🎬 SCENE 3 — Walk Through Results (1:00 – 1:40)

### Schedule Tab (1:00 – 1:10)
**ACTION:** Schedule tab should be default.  
**SCREEN:** Color-coded timeline.

> **SAY:**
>
> "The schedule shows a color-coded timeline — medication in red,
> meals in green, rest in blue, appointments in purple. Each event
> is also in the user's real Google Calendar with reminders."

### Tasks Tab + Interactive Checklist (1:10 – 1:25)
**ACTION:** Click **✅ Tasks** tab. Check off 2-3 tasks.

> **SAY:**
>
> "Tasks are an interactive checklist powered by the MCP Task Store.
> Watch the progress bar update in real-time as I complete tasks.
> This gives users a tangible sense of accomplishment through their day."

### Safety Tab (1:25 – 1:40)
**ACTION:** Click **🛡️ Safety** tab.

> **SAY:**
>
> "This is our **key differentiator** — the Safety Agent. It detects
> five categories of risk: overloaded schedules, missed medications,
> risky transitions, cognitive fatigue, and unsafe time windows.
>
> No other daily planner does this. This is what makes Guidelight an
> *independence copilot*, not just a scheduler."

---

## 🎬 SCENE 4 — Advanced v2.0 Features (1:40 – 2:20)

### Conversational Chat (1:40 – 1:55)
**ACTION:** Click **💬 Chat** tab. Type: `What's my next task?`

> **SAY:**
>
> "After creating a plan, users can have a **conversation** with their
> copilot. 'What's next?' — and it tells you, in a warm, spoken-friendly
> tone. You can also say 'Skip my 3pm task' or 'Am I on track?'"

### Adaptive Replanning (1:55 – 2:10)
**ACTION:** Click **🔄 Adjust Plan** → Type: `My doctor appointment moved to 4pm`  
**ACTION:** Click **⚡ Replan**.

> **SAY:**
>
> "Real life doesn't follow a plan. With **adaptive replanning**, you
> say 'My appointment moved to 4pm' — and the AI restructures your
> entire remaining day. Critical items like medications are never dropped.
> This uses 2 more LLM calls: one to replan, one for safety re-evaluation."

### Emergency SOS (2:10 – 2:20)
**ACTION:** Click **🆘 SOS** button. SOS modal appears with full context.

> **SAY:**
>
> "And for emergencies — one tap on SOS generates a **shareable context
> summary** for caregivers: current activity, medication status, what's
> overdue. You can copy it to clipboard or have it read aloud."

---

## 🎬 SCENE 5 — Voice + Accessibility (2:20 – 2:35)

**ACTION:** Click **✨ New Plan**. Click **🎙️ Speak** button and say:
*"Plan a relaxing day with a morning walk, lunch, and reading time."*

> **SAY:**
>
> "The entire system is **voice-first**. Speak your plan — the Web
> Speech API transcribes it. Summaries are automatically read aloud
> via text-to-speech. The UI is WCAG 2.1 AA: keyboard-navigable,
> high-contrast, screen-reader friendly. Accessibility isn't a feature
> — it's the foundation."

---

## 🎬 SCENE 6 — Architecture + Close (2:35 – 3:00)

**SCREEN:** Briefly show the README architecture diagram or a slide.

> **SAY:**
>
> "The architecture: **Gemini 2.5 Flash on Vertex AI**, orchestrated by
> **Google ADK** with 5 agents and 2 MCP tools — Calendar and Task Store.
> The Calendar tool integrates with **real Google Calendar API** via OAuth2.
>
> *(point to diagram)*
>
> Only **2 LLM calls** for a full plan. Real-time SSE streaming.
> Conversational follow-up. Adaptive replanning. Emergency SOS.
> Safety-first design.
>
> Guidelight AI proves that generative AI can do more than answer
> questions — it can *plan*, *coordinate*, *monitor*, and *protect*.
>
> Real independence. Not just information. Thank you."

---

## ⚡ QUICK CHECKLIST BEFORE RECORDING

- [ ] Open http://localhost:8080 in Chrome (full-screen: Cmd+Shift+F)
- [ ] Refresh page to clear previous results
- [ ] Test microphone (System Preferences → Sound → Input)
- [ ] Test speakers (for TTS readout in the video)
- [ ] Have VS Code open with architecture diagram as backup
- [ ] **Pre-warm:** Generate one plan before recording to warm up Vertex AI
- [ ] Start QuickTime: Cmd+Shift+5 → Record Entire Screen
- [ ] Speak clearly, slightly slow, 1-second pauses between scenes

## ⏱️ TIMING SUMMARY

| Scene | Time | Duration | What's on Screen | Key Buzzwords |
|-------|------|----------|-----------------|---------------|
| 1. Hook + Problem | 0:00–0:25 | 25s | Hero + badges + scenario cards | Vertex AI, ADK, MCP, 5 agents |
| 2. SSE Pipeline | 0:25–1:00 | 35s | Streaming pipeline → metrics + safety banner + GCal sync | 2 LLM calls, SSE, 70% token reduction |
| 3a. Schedule | 1:00–1:10 | 10s | Color-coded timeline | Google Calendar API, OAuth2 |
| 3b. Tasks | 1:10–1:25 | 15s | Checklist + progress bar | MCP Task Store, real-time |
| 3c. Safety | 1:25–1:40 | 15s | Safety card + risk alerts | **Key differentiator**, 5 risk categories |
| 4a. Chat | 1:40–1:55 | 15s | Conversational follow-up | Context-aware, spoken-friendly |
| 4b. Replan | 1:55–2:10 | 15s | Replan modal → updated schedule | Adaptive, preserves critical items |
| 4c. SOS | 2:10–2:20 | 10s | Emergency context modal | Caregiver sharing, medication status |
| 5. Voice + A11y | 2:20–2:35 | 15s | Mic input → TTS readout | WCAG 2.1 AA, voice-first |
| 6. Architecture | 2:35–3:00 | 25s | Diagram + closing | Full stack recap, impact statement |

---

## 🏆 JUDGE IMPACT PHRASES TO USE

Use these naturally during the demo — they map to hackathon scoring criteria:

| Criterion | Phrase to Say |
|-----------|--------------|
| **Gen AI Usage** | "5 agents orchestrated by Google ADK, powered by Gemini 2.5 Flash on Vertex AI" |
| **Innovation** | "The only AI planner with a dedicated Safety Agent — it detects risks no scheduler checks for" |
| **Technical Depth** | "2 LLM calls per plan, MCP tool integration, real Google Calendar OAuth2 sync" |
| **Impact** | "Real independence for 2.2 billion people with vision impairment" |
| **Completeness** | "SSE streaming, conversational chat, adaptive replanning, emergency SOS — all working end-to-end" |
| **Optimization** | "70% token reduction by calling Calendar and Task tools programmatically instead of through the LLM" |

---

## 🎯 BACKUP PLAN

If Vertex AI is slow or errors during live recording:
1. **Pre-record the pipeline section** separately and splice in
2. Use the **non-streaming fallback endpoint** (`/daily-intent`) which is more reliable
3. Have a **pre-generated plan** — navigate to it via `/daily-plan/{plan_id}` in the URL
4. The app gracefully falls back to in-memory calendar if Google Calendar API has issues
