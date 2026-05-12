"""
TODO system - task tracking and execution plan management.
Track tasks like Claude Code and manage multi-step execution plans.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, asdict, field
from enum import Enum
import json
import os
from datetime import datetime

# Import new schema classes
from .schemas import ExecutionPlan, ExecutionStep, StepObservation, StepStatus, PlanStatus


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

    # ========================================================================
    # NEW: ExecutionPlan methods (for multi-step task execution)
    # ========================================================================

    def start_plan(self, plan: ExecutionPlan) -> ExecutionPlan:
        """
        Start an execution plan.

        Args:
            plan: ExecutionPlan to start

        Returns:
            Updated plan with status changed to IN_PROGRESS
        """
        plan.status = PlanStatus.IN_PROGRESS
        plan.started_at = datetime.now().isoformat()

        # Mark first step as in progress if not already
        if plan.current_step_id and not plan.get_current_step():
            plan.current_step_id = None

        # Set current step to first pending step
        if not plan.current_step_id and plan.steps:
            plan.current_step_id = plan.steps[0].id
            plan.steps[0].status = StepStatus.IN_PROGRESS
            plan.steps[0].started_at = datetime.now().isoformat()

        return plan

    def get_current_step(self, plan: ExecutionPlan) -> Optional[ExecutionStep]:
        """Get the currently executing step."""
        if not plan.current_step_id:
            return None
        for step in plan.steps:
            if step.id == plan.current_step_id:
                return step
        return None

    def mark_step_started(self, plan: ExecutionPlan, step_id: str) -> bool:
        """
        Mark a step as in progress.

        Args:
            plan: ExecutionPlan
            step_id: ID of step to start

        Returns:
            True if step was marked started
        """
        for step in plan.steps:
            if step.id == step_id:
                if step.status == StepStatus.PENDING:
                    step.status = StepStatus.IN_PROGRESS
                    step.started_at = datetime.now().isoformat()
                    plan.current_step_id = step_id
                    plan.status = PlanStatus.IN_PROGRESS
                    return True
        return False

    def record_observation(
        self,
        plan: ExecutionPlan,
        step_id: str,
        observation: StepObservation,
    ) -> bool:
        """
        Record observation/feedback from step execution.

        Args:
            plan: ExecutionPlan
            step_id: ID of step that was observed
            observation: StepObservation with feedback

        Returns:
            True if observation was recorded
        """
        for step in plan.steps:
            if step.id == step_id:
                step.last_observation = observation.to_dict()
                # Optionally record to history
                plan.history.append({
                    "timestamp": datetime.now().isoformat(),
                    "step_id": step_id,
                    "event": "observation",
                    "observation": observation.to_dict(),
                })
                return True
        return False

    def mark_step_completed(
        self,
        plan: ExecutionPlan,
        step_id: str,
        actual_result: str = "",
    ) -> bool:
        """
        Mark a step as completed.

        Args:
            plan: ExecutionPlan
            step_id: ID of step
            actual_result: What actually happened

        Returns:
            True if step was marked completed
        """
        for step in plan.steps:
            if step.id == step_id:
                step.status = StepStatus.COMPLETED
                step.actual_result = actual_result
                step.completed_at = datetime.now().isoformat()
                plan.history.append({
                    "timestamp": datetime.now().isoformat(),
                    "step_id": step_id,
                    "event": "completed",
                    "actual_result": actual_result,
                })
                return True
        return False

    def mark_step_failed(
        self,
        plan: ExecutionPlan,
        step_id: str,
        reason: str = "",
    ) -> bool:
        """
        Mark a step as failed.

        Args:
            plan: ExecutionPlan
            step_id: ID of step
            reason: Why it failed

        Returns:
            True if step was marked failed
        """
        for step in plan.steps:
            if step.id == step_id:
                step.status = StepStatus.FAILED
                step.error = reason
                plan.history.append({
                    "timestamp": datetime.now().isoformat(),
                    "step_id": step_id,
                    "event": "failed",
                    "reason": reason,
                })
                return True
        return False

    def get_next_step(self, plan: ExecutionPlan) -> Optional[ExecutionStep]:
        """
        Get the next step that should be executed.

        Respects dependencies: only returns steps whose dependencies are completed.

        Returns:
            Next ExecutionStep or None if no more steps
        """
        for step in plan.steps:
            if step.status == StepStatus.PENDING:
                # Check dependencies
                if self._dependencies_met(plan, step):
                    return step
        return None

    def _dependencies_met(self, plan: ExecutionPlan, step: ExecutionStep) -> bool:
        """Check if all dependencies of a step are completed."""
        for dep_id in step.depends_on:
            dep_step = None
            for s in plan.steps:
                if s.id == dep_id:
                    dep_step = s
                    break
            if not dep_step or dep_step.status != StepStatus.COMPLETED:
                return False
        return True

    def can_continue(self, plan: ExecutionPlan) -> bool:
        """
        Check if plan can continue (not blocked/failed).

        Returns:
            True if plan is in progress or has next steps available
        """
        # Check if plan is complete
        if plan.is_complete():
            return False

        # Check for blocked steps
        for step in plan.steps:
            if step.status == StepStatus.BLOCKED:
                # Plan is blocked if a step is blocked and not yet resolved
                return False

        # Can continue if there's a next step or current step is in progress
        return plan.get_next_incomplete_step() is not None or plan.get_current_step() is not None

    def get_remaining_steps(self, plan: ExecutionPlan) -> List[ExecutionStep]:
        """Get all remaining (not completed/skipped) steps."""
        return plan.get_remaining_steps()

    def save_plan(self, plan: ExecutionPlan, filename: str = None) -> bool:
        """
        Save execution plan to file.

        Args:
            plan: ExecutionPlan to save
            filename: Optional filename (defaults to plan_id)

        Returns:
            True if saved successfully
        """
        try:
            if not filename:
                filename = plan.plan_id
            filepath = os.path.join(self.todo_dir, f"{filename}.json")
            with open(filepath, "w") as f:
                json.dump(plan.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving plan: {e}")
            return False

    def load_plan(self, filename: str) -> Optional[ExecutionPlan]:
        """
        Load execution plan from file.

        Args:
            filename: Filename to load

        Returns:
            ExecutionPlan or None if not found
        """
        try:
            filepath = os.path.join(self.todo_dir, f"{filename}.json")
            with open(filepath, "r") as f:
                data = json.load(f)

            # Reconstruct ExecutionPlan from dict
            # This is a simplified version; proper deserialization might be more complex
            plan = ExecutionPlan(
                plan_id=data["plan_id"],
                objective=data["objective"],
                created_by=data["created_by"],
                status=data.get("status", "created"),
                created_at=data.get("created_at"),
                started_at=data.get("started_at"),
                completed_at=data.get("completed_at"),
                history=data.get("history", []),
                context=data.get("context", {}),
            )

            # Reconstruct steps (simplified)
            for step_data in data.get("steps", []):
                step = ExecutionStep(
                    id=step_data["id"],
                    description=step_data["description"],
                    target=step_data["target"],
                    action=step_data["action"],
                    expected_result=step_data["expected_result"],
                    status=StepStatus(step_data.get("status", "pending")),
                    payload=step_data.get("payload", {}),
                    success_criteria=step_data.get("success_criteria", []),
                    query_maker=step_data.get("query_maker"),
                    retry_count=step_data.get("retry_count", 0),
                    max_retries=step_data.get("max_retries", 3),
                    actual_result=step_data.get("actual_result"),
                    error=step_data.get("error"),
                    depends_on=step_data.get("depends_on", []),
                    last_observation=step_data.get("last_observation"),
                    started_at=step_data.get("started_at"),
                    completed_at=step_data.get("completed_at"),
                )
                plan.steps.append(step)

            plan.current_step_id = data.get("current_step_id")
            return plan
        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"Error loading plan: {e}")
            return None


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
