"""
TODO system - task tracking and execution plan management.
Track tasks like Claude Code and manage multi-step execution plans.
"""

# Legacy interface (Claude-Code style checklist)
from .todo import (
    Task,
    TodoList,
    TaskStatus,
    TodoManager,
    create_task_list,
    add_task,
    mark_task_done,
    print_tasks,
)

# New architecture (execution plans and steps)
from .schemas import (
    ExecutionPlan,
    ExecutionStep,
    StepObservation,
    StepStatus,
    PlanStatus,
)

__all__ = [
    # Legacy
    "Task",
    "TodoList",
    "TaskStatus",
    "TodoManager",
    "create_task_list",
    "add_task",
    "mark_task_done",
    "print_tasks",
    # New architecture
    "ExecutionPlan",
    "ExecutionStep",
    "StepObservation",
    "StepStatus",
    "PlanStatus",
]
