"""MCP-compliant persistent task store tool stub.

In production this would be backed by Firestore or Cloud SQL via MCP.
For the hackathon demo it uses an in-memory dict that demonstrates the
MCP tool contract.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

# In-memory task store (plan_id → list of tasks)
_task_store: dict[str, list[dict[str, Any]]] = {}


def create_task(
    plan_id: str,
    title: str,
    scheduled_time: str,
    category: str = "general",
    priority: str = "normal",
) -> dict[str, Any]:
    """Create a new task in the MCP task store.

    Args:
        plan_id: Owning plan.
        title: Task description.
        scheduled_time: ISO-8601 time string.
        category: One of general / medication / meal / rest / appointment / exercise.
        priority: One of low / normal / high / critical.

    Returns:
        The created task dict.
    """
    task = {
        "task_id": str(uuid.uuid4())[:8],
        "plan_id": plan_id,
        "title": title,
        "scheduled_time": scheduled_time,
        "category": category,
        "priority": priority,
        "status": "pending",
        "created_at": datetime.utcnow().isoformat(),
        "completed_at": None,
    }
    _task_store.setdefault(plan_id, []).append(task)
    return task


def list_tasks(plan_id: str) -> list[dict[str, Any]]:
    """List all tasks for a plan."""
    return _task_store.get(plan_id, [])


def complete_task(plan_id: str, task_id: str) -> dict[str, Any] | None:
    """Mark a task as completed."""
    for task in _task_store.get(plan_id, []):
        if task["task_id"] == task_id:
            task["status"] = "completed"
            task["completed_at"] = datetime.utcnow().isoformat()
            return task
    return None


def get_pending_tasks(plan_id: str) -> list[dict[str, Any]]:
    """Return only pending tasks."""
    return [t for t in _task_store.get(plan_id, []) if t["status"] == "pending"]


def get_overdue_tasks(plan_id: str, current_time: str | None = None) -> list[dict[str, Any]]:
    """Return tasks whose scheduled_time has passed but are still pending."""
    now = current_time or datetime.utcnow().isoformat()
    return [
        t
        for t in _task_store.get(plan_id, [])
        if t["status"] == "pending" and t["scheduled_time"] < now
    ]


def get_plan_progress(plan_id: str) -> dict[str, Any]:
    """Summary stats for a plan's tasks."""
    tasks = _task_store.get(plan_id, [])
    total = len(tasks)
    completed = sum(1 for t in tasks if t["status"] == "completed")
    return {
        "plan_id": plan_id,
        "total_tasks": total,
        "completed": completed,
        "pending": total - completed,
        "completion_pct": round(completed / total * 100, 1) if total else 0.0,
    }
