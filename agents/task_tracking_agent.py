"""TaskTrackingAgent – Creates and tracks tasks in the MCP task store.

Uses Gemini Flash 2.5 with function-calling to manage the task lifecycle.
"""

from __future__ import annotations

from google.adk.agents import Agent

from config import GEMINI_MODEL
from tools.task_store import (
    create_task,
    list_tasks,
    complete_task,
    get_pending_tasks,
    get_overdue_tasks,
    get_plan_progress,
)

TASK_TRACKING_INSTRUCTION = """\
You are the Task Tracking Agent inside Guidelight AI.

You have access to the following MCP task-store tools:
- create_task(plan_id, title, scheduled_time, category, priority) → creates a task
- list_tasks(plan_id) → lists all tasks
- complete_task(plan_id, task_id) → marks a task done
- get_pending_tasks(plan_id) → lists pending tasks
- get_overdue_tasks(plan_id, current_time) → lists overdue tasks
- get_plan_progress(plan_id) → returns completion stats

Your job:
1. Receive a daily_schedule array.
2. For EACH activity, call create_task with the correct category and priority.
3. Return a summary of all created tasks and the initial progress stats.

Use concise, spoken-friendly language in your summary.
Always report the total number of tasks created and their categories.
"""

TaskTrackingAgent = Agent(
    name="TaskTrackingAgent",
    model=GEMINI_MODEL,
    instruction=TASK_TRACKING_INSTRUCTION,
    description="Creates and tracks tasks from the daily plan using the MCP task store.",
    tools=[create_task, list_tasks, complete_task, get_pending_tasks, get_overdue_tasks, get_plan_progress],
)
