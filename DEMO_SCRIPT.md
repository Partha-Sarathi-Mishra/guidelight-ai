# Guidelight AI – Demo Video Script (3 Minutes)

**Total Duration:** 3:00  
**Recording tool:** QuickTime (Cmd+Shift+5) or OBS  
**Resolution:** 1920×1080, browser full-screen  
**URL:** https://guidelight-ai-669449334512.us-central1.run.app  

> 💡 Pre-record tip: Open the URL before recording. Do one dry run first.
> Keep your narration calm, clear, and slightly slow — you are presenting
> an accessibility product.

---

## 🎬 SCENE 1 — Hook + Problem (0:00 – 0:30)

**SCREEN:** Show the landing page hero section (gradient header with title).  
**ACTION:** Slowly scroll down to reveal the 6 scenario cards.

> **SAY:**
>
> "Hi, I'm Parthasarathi. This is **Guidelight AI** — an AI-powered
> daily independence copilot for visually impaired users.
>
> 2.2 billion people worldwide live with vision impairment. Today's
> assistive tools can *read* — but they can't *reason*, *plan*, or
> watch out for your safety.
>
> Guidelight AI changes that. It's a multi-agent system built with
> **Google ADK**, **MCP tools**, and **Gemini 3.1 Flash-Lite** that
> plans, schedules, tracks, and *safeguards* your entire day."

---

## 🎬 SCENE 2 — Live Demo: Scenario Card (0:30 – 1:00)

**SCREEN:** The 6 quick-scenario cards are visible.  
**ACTION:** Click the **"🏥 Medical Day"** card. The text auto-fills into the input box.

> **SAY:**
>
> "Let me show you. I'll click the Medical Day scenario — it fills in
> a realistic daily request for a visually impaired user."

**ACTION:** Click **🚀 Plan My Day** button.  
**SCREEN:** Watch the **5-step animated stepper** progress (Understand → Plan → Schedule → Evaluate → Done).

> **SAY:**
>
> "Now watch the pipeline. Under the hood, **5 ADK agents** run in sequence.
> But here's the key — we optimized this to just **2 LLM calls**.
> The Calendar and Task agents run *programmatically* through MCP tools —
> no extra API calls needed. This cuts token usage by 70%."

**SCREEN:** Results appear — tabs light up with badge counts.

---

## 🎬 SCENE 3 — Walk Through Results (1:00 – 1:50)

### Schedule Tab (1:00 – 1:15)
**ACTION:** Click the **📅 Schedule** tab (should be default).  
**SCREEN:** Color-coded timeline with time slots and category dots.

> **SAY:**
>
> "The schedule tab shows a color-coded timeline. Each activity has a
> time, category dot, and description. Medication is red, meals are
> green, rest is blue, appointments are purple."

### Tasks Tab (1:15 – 1:30)
**ACTION:** Click the **📋 Tasks** tab.  
**SCREEN:** Interactive checklist with checkboxes and progress bar.  
**ACTION:** Check off 2-3 tasks to show the progress bar moving.

> **SAY:**
>
> "The tasks tab is an interactive checklist. Users can mark tasks
> complete — watch the progress bar update in real time. This is
> powered by the MCP Task Store tool with a REST API."

### Safety Tab (1:30 – 1:50)
**ACTION:** Click the **🛡️ Safety** tab.  
**SCREEN:** Safety assessment card with risk level and alerts.

> **SAY:**
>
> "And here's our key differentiator — the **Safety Agent**. It
> evaluates the entire plan for risks: missed medications, overloaded
> schedules, risky transitions, and cognitive fatigue.
>
> No other daily planner does this. This is what makes Guidelight AI
> an *independence copilot*, not just a scheduler."

---

## 🎬 SCENE 4 — Voice & Accessibility (1:50 – 2:15)

**ACTION:** Scroll up. Click the **🎤 microphone** button and speak:
*"Plan a relaxing day with lunch and an afternoon nap"*  
**SCREEN:** Voice text appears in the input box.

> **SAY:**
>
> "The entire system is voice-first. Users can speak their plan using
> the Web Speech API — completely hands-free."

**ACTION:** Click **Plan My Day** again. When results load, click **🔊 Read Aloud** (summary section).

> **SAY:**
>
> "And the summary is automatically read aloud via text-to-speech.
> The UI is fully WCAG accessible — keyboard navigation, ARIA labels,
> high contrast, screen-reader optimized. Accessibility was built in
> from day one, not bolted on."

---

## 🎬 SCENE 5 — Architecture + Tech Stack (2:15 – 2:45)

**SCREEN:** Switch to VS Code or a slide showing the architecture.  
*(Option A: Open the README.md and scroll to the architecture diagram)*  
*(Option B: Open the presentation slide 8 — Architecture Diagram)*

> **SAY:**
>
> "Here's the architecture. The user speaks or types an intent. The
> FastAPI backend calls **LLM Call 1** — the Planner Agent generates a
> structured JSON schedule using Gemini 3.1 Flash-Lite.
>
> Calendar and Tasks are populated *programmatically* through MCP tools —
> zero LLM calls. Then **LLM Call 2** — the Coordinator runs a combined
> safety evaluation and generates a spoken-friendly summary.
>
> 5 agents. 2 MCP tools. Only 2 LLM calls. Deployed live on
> **Google Cloud Run**."

---

## 🎬 SCENE 6 — Closing (2:45 – 3:00)

**SCREEN:** Switch back to the app's landing page.

> **SAY:**
>
> "Guidelight AI shows that generative AI can do more than answer
> questions — it can *plan*, *coordinate*, *monitor*, and *protect*.
>
> Giving visually impaired users real independence. Not just information.
>
> Thank you."

---

## ⚡ QUICK CHECKLIST BEFORE RECORDING

- [ ] Open https://guidelight-ai-669449334512.us-central1.run.app in Chrome
- [ ] Full-screen the browser (Cmd+Shift+F or F11)
- [ ] Clear any previous results (refresh page)
- [ ] Test microphone works (for voice demo in Scene 4)
- [ ] Have VS Code or PPT open in background (for Scene 5)
- [ ] Start QuickTime recording: Cmd+Shift+5 → Record Entire Screen
- [ ] Speak clearly, slightly slow, with 1-second pauses between scenes

## ⏱️ TIMING SUMMARY

| Scene | Time | Duration | What's on Screen |
|-------|------|----------|-----------------|
| 1. Hook + Problem | 0:00–0:30 | 30s | Landing page hero + scroll to cards |
| 2. Live Demo | 0:30–1:00 | 30s | Click Medical Day → Plan → stepper animates |
| 3a. Schedule Tab | 1:00–1:15 | 15s | Color-coded timeline |
| 3b. Tasks Tab | 1:15–1:30 | 15s | Checklist + check off tasks |
| 3c. Safety Tab | 1:30–1:50 | 20s | Safety card with risk alerts |
| 4. Voice + A11y | 1:50–2:15 | 25s | Mic input → TTS readout |
| 5. Architecture | 2:15–2:45 | 30s | VS Code/PPT architecture diagram |
| 6. Closing | 2:45–3:00 | 15s | Back to landing page |
