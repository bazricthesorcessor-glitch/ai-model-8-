"""
Todo execution schemas - structured task and plan representations.
Defines step, plan, and status tracking for long-running agent tasks.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class StepStatus(str, Enum):
    """Status of a single execution step."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


class PlanStatus(str, Enum):
    """Status of entire execution plan."""
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    ABANDONED = "abandoned"


@dataclass
class ExecutionStep:
    """Single step in an execution plan."""

    id: str
    description: str

    # What to do
    target: str  # executor, coder, thinker, query_maker1, etc
    action: str  # dispatch_tool, dispatch_model, run_query_maker, etc

    # What we expect
    expected_result: str  # Human description of success

    # Optional/defaults
    payload: Dict[str, Any] = field(default_factory=dict)
    success_criteria: List[str] = field(default_factory=list)
    query_maker: Optional[str] = None  # query_maker1 or query_maker2

    # Execution tracking
    status: StepStatus = StepStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3

    # Results
    actual_result: Optional[str] = None
    last_observation: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    # Dependencies
    depends_on: List[str] = field(default_factory=list)

    # Timing
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict."""
        return {
            "id": self.id,
            "description": self.description,
            "target": self.target,
            "action": self.action,
            "payload": self.payload,
            "expected_result": self.expected_result,
            "success_criteria": self.success_criteria,
            "query_maker": self.query_maker,
            "status": self.status.value,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "actual_result": self.actual_result,
            "last_observation": self.last_observation,
            "error": self.error,
            "depends_on": self.depends_on,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }


@dataclass
class ExecutionPlan:
    """Complete execution plan for a task."""

    plan_id: str
    objective: str
    created_by: str  # "scout", "brain", etc

    # Steps
    steps: List[ExecutionStep] = field(default_factory=list)
    current_step_id: Optional[str] = None

    # Status
    status: PlanStatus = PlanStatus.CREATED

    # Tracking
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    # History
    history: List[Dict[str, Any]] = field(default_factory=list)

    # Context
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict."""
        return {
            "plan_id": self.plan_id,
            "objective": self.objective,
            "created_by": self.created_by,
            "steps": [step.to_dict() for step in self.steps],
            "current_step_id": self.current_step_id,
            "status": self.status.value,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "history": self.history,
            "context": self.context,
        }

    def get_current_step(self) -> Optional[ExecutionStep]:
        """Get the current step."""
        if not self.current_step_id:
            return None
        for step in self.steps:
            if step.id == self.current_step_id:
                return step
        return None

    def get_next_incomplete_step(self) -> Optional[ExecutionStep]:
        """Get the next incomplete step (not done, not skipped)."""
        for step in self.steps:
            if step.status in [StepStatus.PENDING, StepStatus.FAILED]:
                # Check dependencies
                if not self._dependencies_met(step):
                    return None  # Can't run yet
                return step
        return None

    def _dependencies_met(self, step: ExecutionStep) -> bool:
        """Check if all dependencies of a step are completed."""
        for dep_id in step.depends_on:
            for step_candidate in self.steps:
                if step_candidate.id == dep_id:
                    if step_candidate.status != StepStatus.COMPLETED:
                        return False
        return True

    def get_remaining_steps(self) -> List[ExecutionStep]:
        """Get all remaining (not completed/skipped) steps."""
        return [
            step for step in self.steps
            if step.status not in [StepStatus.COMPLETED, StepStatus.SKIPPED]
        ]

    def is_complete(self) -> bool:
        """Check if plan is complete (all steps done or skipped)."""
        return all(
            step.status in [StepStatus.COMPLETED, StepStatus.SKIPPED]
            for step in self.steps
        )


@dataclass
class StepObservation:
    """Observation/feedback from step execution."""

    step_id: str
    matched_expectation: bool
    confidence: float  # 0.0 to 1.0
    status: str  # "success", "failed", "uncertain", "blocked"
    reason: str
    recommended_next: str  # "continue", "retry", "replan", "stop"

    feedback: Optional[str] = None
    actual_output: Optional[Dict[str, Any]] = None

    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict."""
        return {
            "step_id": self.step_id,
            "matched_expectation": self.matched_expectation,
            "confidence": self.confidence,
            "status": self.status,
            "reason": self.reason,
            "recommended_next": self.recommended_next,
            "feedback": self.feedback,
            "actual_output": self.actual_output,
            "timestamp": self.timestamp,
        }
