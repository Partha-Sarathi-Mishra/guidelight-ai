# Guidelight AI – Demo Narration Script

**Duration:** ~3 minutes

---

## OPENING (30 seconds)

> "Imagine you're visually impaired and need to plan your entire day —
> a medical appointment, medication reminders, meals, and rest.
> Today's assistive tools can *read* information, but they can't *reason*
> across your whole day, coordinate tools, or watch out for your safety.
>
> That's why we built **Guidelight AI** — an AI Daily Independence Copilot
> powered by **Gemini Flash 2.5** and **Google's Agent Development Kit**."

---

## DEMO INPUT (15 seconds)

> "Let's try it. I'll type what a real user might say:
>
> *'Help me plan my day. I have a medical appointment, need reminders
> to take my medication, want time to prepare meals, and need breaks
> between activities.'*
>
> Now I'll press **Plan My Day**."

---

## AGENT EXECUTION (60 seconds)

> "Watch the **Agent Execution Log** on the right. Five agents work in
> sequence — and you can see each one in real-time:
>
> 1. **Independence Coordinator** interprets my intent and starts the
>    pipeline.
>
> 2. **Daily Planning Agent** (powered by Gemini Flash 2.5) converts my
>    vague request into a structured schedule — with meals, rest breaks,
>    and time buffers already included.
>
> 3. **Calendar & Reminder Agent** takes the plan and schedules every
>    event on the calendar through an MCP-connected Google Calendar
>    interface. It also checks for conflicts.
>
> 4. **Task Tracking Agent** stores each activity as a trackable task
>    in a persistent MCP task store — so progress can be monitored
>    throughout the day.
>
> 5. **Safety & Risk Agent** — our key differentiator — evaluates the
>    entire plan. It checks for overloaded schedules, missed medication,
>    missing meals, risky transitions, and cognitive overload."

---

## FINAL SUMMARY (30 seconds)

> "At the bottom, you can see the **Final Summary** — a calm, clear,
> spoken-friendly plan ready to be read aloud by a screen reader.
>
> Notice: simple sentences, times spoken as words, supportive tone.
> This isn't just a schedule — it's an *independence plan*."

---

## ACCESSIBILITY HIGHLIGHT (20 seconds)

> "The entire UI uses semantic HTML, high-contrast colors, large fonts,
> and full keyboard navigation. Every interactive element has proper
> ARIA labels. No frameworks — just clean, accessible HTML.
>
> This was designed for visually impaired users from the first line of
> code."

---

## ARCHITECTURE (15 seconds)

> "Under the hood: five ADK-defined agents, all running Gemini Flash 2.5
> on Vertex AI. MCP tool integrations for Calendar and Task Store.
> FastAPI backend. Deployed on Cloud Run.
>
> The entire system is stateless, fast, and ready for production."

---

## CLOSING (15 seconds)

> "Guidelight AI shows that generative AI can do more than answer questions.
> It can *plan*, *coordinate*, *monitor*, and *protect* — giving visually
> impaired users real independence, not just information.
>
> Thank you."

---

## BACKUP DEMO INPUTS

If time permits, show one additional input:

- `"I just got back from the hospital. I need to rest, take my evening medication, and eat dinner. I also want to call my daughter tonight."`
- `"Schedule my morning: wake up, yoga, breakfast, take blood pressure medication, then work from home until lunch."`
