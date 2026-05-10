"""
TODO system - task tracking and progress management.
Track tasks, steps, and progress similar to Claude Code.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, asdict, field
from enum import Enum
import json
import os
from datetime import datetime


class TaskStatus(Enum):
    """Task status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"


@dataclass
class Task:
    """Individual task/step."""
    content: str                # What needs to be done (imperative)
    active_form: str           # Present continuous form ("Doing X")
    status: str = "pending"    # pending, in_progress, completed
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class TodoList:
    """Collection of tasks."""
    title: str
    tasks: List[Task] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


class TodoManager:
    """Manage tasks and progress."""

    def __init__(self, todo_dir: str = "/home/dmannu/ai model 8/todo"):
        """Initialize TODO manager."""
        self.todo_dir = todo_dir
        os.makedirs(todo_dir, exist_ok=True)

    def create_todo_list(self, title: str) -> TodoList:
        """Create new TODO list."""
        return TodoList(title=title, tasks=[])

    def add_task(
        self,
        todo_list: TodoList,
        content: str,
        active_form: str,
    ) -> Task:
        """Add task to list."""
        task = Task(content=content, active_form=active_form)
        todo_list.tasks.append(task)
        return task

    def mark_in_progress(
        self,
        todo_list: TodoList,
        task_index: int,
    ) -> bool:
        """Mark task as in_progress."""
        if 0 <= task_index < len(todo_list.tasks):
            task = todo_list.tasks[task_index]
            if task.status == "pending":
                task.status = "in_progress"
                todo_list.updated_at = datetime.now().isoformat()
                return True
        return False

    def mark_completed(
        self,
        todo_list: TodoList,
        task_index: int,
    ) -> bool:
        """Mark task as completed."""
        if 0 <= task_index < len(todo_list.tasks):
            task = todo_list.tasks[task_index]
            if task.status in ["pending", "in_progress"]:
                task.status = "completed"
                task.completed_at = datetime.now().isoformat()
                todo_list.updated_at = datetime.now().isoformat()
                return True
        return False

    def mark_blocked(
        self,
        todo_list: TodoList,
        task_index: int,
        reason: str = "",
    ) -> bool:
        """Mark task as blocked."""
        if 0 <= task_index < len(todo_list.tasks):
            task = todo_list.tasks[task_index]
            task.status = "blocked"
            task.notes = reason
            todo_list.updated_at = datetime.now().isoformat()
            return True
        return False

    def save_todo_list(self, todo_list: TodoList, filename: str) -> bool:
        """Save TODO list to file."""
        try:
            filepath = os.path.join(self.todo_dir, f"{filename}.json")
            data = {
                "title": todo_list.title,
                "created_at": todo_list.created_at,
                "updated_at": todo_list.updated_at,
                "tasks": [asdict(t) for t in todo_list.tasks],
            }
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving: {e}")
            return False

    def load_todo_list(self, filename: str) -> Optional[TodoList]:
        """Load TODO list from file."""
        try:
            filepath = os.path.join(self.todo_dir, f"{filename}.json")
            with open(filepath, "r") as f:
                data = json.load(f)

            tasks = [Task(**t) for t in data.get("tasks", [])]
            todo_list = TodoList(
                title=data["title"],
                tasks=tasks,
                created_at=data["created_at"],
                updated_at=data["updated_at"],
            )
            return todo_list
        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"Error loading: {e}")
            return None

    def get_status(self, todo_list: TodoList) -> Dict:
        """Get TODO list status."""
        total = len(todo_list.tasks)
        completed = sum(1 for t in todo_list.tasks if t.status == "completed")
        in_progress = sum(1 for t in todo_list.tasks if t.status == "in_progress")
        pending = sum(1 for t in todo_list.tasks if t.status == "pending")
        blocked = sum(1 for t in todo_list.tasks if t.status == "blocked")

        return {
            "title": todo_list.title,
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "pending": pending,
            "blocked": blocked,
            "percentage": (completed / total * 100) if total > 0 else 0,
        }

    def print_todo_list(self, todo_list: TodoList) -> None:
        """Print TODO list in readable format."""
        status = self.get_status(todo_list)

        print(f"\n{'=' * 70}")
        print(f"TODO: {status['title']}")
        print(f"{'=' * 70}")
        print(f"Status: {status['completed']}/{status['total']} completed ({status['percentage']:.0f}%)")
        print(f"In Progress: {status['in_progress']} | Pending: {status['pending']} | Blocked: {status['blocked']}\n")

        for i, task in enumerate(todo_list.tasks, 1):
            status_icon = {
                "pending": "⏳",
                "in_progress": "🔄",
                "completed": "✅",
                "blocked": "⛔",
            }.get(task.status, "❓")

            print(f"{i}. {status_icon} {task.content}")
            if task.status == "in_progress":
                print(f"   → {task.active_form}")
            if task.status == "blocked" and task.notes:
                print(f"   🛑 {task.notes}")


# ============================================================================
# Convenience Functions
# ============================================================================

def create_task_list(title: str) -> TodoList:
    """Create new task list."""
    return TodoList(title=title, tasks=[])


def add_task(
    todo_list: TodoList,
    content: str,
    active_form: str,
) -> Task:
    """Add task to list."""
    return TodoManager().add_task(todo_list, content, active_form)


def mark_task_done(todo_list: TodoList, task_index: int) -> bool:
    """Mark task as completed."""
    return TodoManager().mark_completed(todo_list, task_index)


def print_tasks(todo_list: TodoList) -> None:
    """Print tasks."""
    TodoManager().print_todo_list(todo_list)
