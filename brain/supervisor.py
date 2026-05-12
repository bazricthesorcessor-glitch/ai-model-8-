"""
Supervisor - controls the multi-step execution loop.

Coordinates:
1. Get current step
2. Prepare message for router/executor/coder
3. Handle response from service
4. Observe/verify results
5. Update todo with state
6. Decide: continue/retry/replan/stop

This is the real "brain" of long-task execution.
"""

from typing import Dict, Any, Optional, Tuple
from todo.schemas import ExecutionPlan, ExecutionStep, StepObservation, StepStatus
from todo import TodoManager
from brain.observer import observe_step_result
from router import Message


class Supervisor:
    """
    Execution supervisor - controls step-by-step task execution.

    Handles the loop:
    - Current step
    - Query maker selection
    - Service dispatch
    - Result observation
    - State update
    - Decision: continue/retry/replan/stop
    """

    def __init__(self):
        """Initialize supervisor."""
        self.todo_manager = TodoManager()

    def prepare_step_message(
        self,
        plan: ExecutionPlan,
        step: ExecutionStep,
    ) -> Optional[Message]:
        """
        Prepare a router Message for step execution.

        Includes query maker context if needed.

        Args:
            plan: Current execution plan
            step: Step to execute

        Returns:
            Message ready for router, or None if can't prepare
        """
        # Decide if we need query maker context
        query_maker_name = step.query_maker or self._select_default_query_maker(step.target)

        # Build payload with context
        payload = {
            **step.payload,
            "plan_id": plan.plan_id,
            "step_id": step.id,
            "expected_result": step.expected_result,
        }

        # Build message
        message = Message(
            source="supervisor",
            target=step.target,
            action=step.action,
            payload=payload,
            context={
                "plan_id": plan.plan_id,
                "step_id": step.id,
                "query_maker": query_maker_name,
                "plan_objective": plan.objective,
            },
        )

        return message

    def _select_default_query_maker(self, target: str) -> str:
        """
        Select default query maker based on target service.

        Rules:
        - executor/fast → query_maker1
        - coder/thinker → query_maker2
        - default → query_maker1
        """
        if target in ["executor", "fast_executor"]:
            return "query_maker1"
        if target in ["coder", "thinker"]:
            return "query_maker2"
        return "query_maker1"

    def handle_service_response(
        self,
        plan: ExecutionPlan,
        step: ExecutionStep,
        service_response: Dict[str, Any],
    ) -> StepObservation:
        """
        Handle response from a service (executor, coder, etc).

        Extract feedback and create observation.

        Args:
            plan: Execution plan
            step: Step that was executed
            service_response: Response dict from service

        Returns:
            StepObservation with result assessment
        """
        # Extract feedback from response
        success = service_response.get("success", False)
        result = service_response.get("result", {})
        error = service_response.get("error")

        # Build feedback string
        if success:
            feedback = f"Success. Result: {result}"
        else:
            feedback = f"Failed. Error: {error}"

        # Create observation
        observation = observe_step_result(
            step_id=step.id,
            step_description=step.description,
            expected_result=step.expected_result,
            success_criteria=step.success_criteria,
            actual_feedback=feedback,
        )

        return observation

    def decide_next_action(
        self,
        plan: ExecutionPlan,
        observation: StepObservation,
    ) -> str:
        """
        Decide what to do next based on observation.

        Returns:
            "continue" | "retry" | "replan" | "stop"
        """
        # If observer recommends something, use it
        if observation.recommended_next in ["continue", "retry", "replan", "stop"]:
            return observation.recommended_next

        # Fallback decision logic
        if observation.matched_expectation:
            return "continue"

        # Check retry count
        current_step = None
        for step in plan.steps:
            if step.id == observation.step_id:
                current_step = step
                break

        if current_step and current_step.retry_count < current_step.max_retries:
            return "retry"

        # Uncertain/low confidence
        if observation.confidence < 0.5:
            return "replan"

        # Default to stop on failure
        return "stop"

    def execute_plan_step(
        self,
        plan: ExecutionPlan,
        step: Optional[ExecutionStep] = None,
    ) -> Tuple[ExecutionPlan, str, Optional[Message]]:
        """
        Prepare a single step of the plan for execution.

        Does pre-dispatch bookkeeping:
        1. Mark step started
        2. Prepare router Message

        The caller will dispatch the Message and then call finalize_step() with the response.

        Args:
            plan: Execution plan
            step: Optional step (defaults to current/next step)

        Returns:
            Tuple of (updated_plan, next_action, message_to_dispatch)
            - next_action: "dispatch" if message is ready, "stop" if blocked
            - message: Router Message ready to dispatch, or None if blocked
        """
        # Get step if not provided
        if not step:
            step = self.todo_manager.get_current_step(plan)
            if not step:
                # Try to get next incomplete step
                step = self.todo_manager.get_next_step(plan)
            if not step:
                return plan, "stop", None

        # Mark step started
        self.todo_manager.mark_step_started(plan, step.id)

        # Prepare message (caller will dispatch this)
        message = self.prepare_step_message(plan, step)
        if not message:
            return plan, "stop", None

        return plan, "dispatch", message

    def finalize_step(
        self,
        plan: ExecutionPlan,
        step: ExecutionStep,
        service_response: Dict[str, Any],
    ) -> Tuple[ExecutionPlan, str]:
        """
        Finalize step after service response.

        Does:
        1. Handle response
        2. Observe results
        3. Record observation
        4. Mark step completed/failed
        5. Update todo
        6. Decide next action

        Args:
            plan: Execution plan
            step: Step that was executed
            service_response: Response from service

        Returns:
            Tuple of (updated_plan, next_action)
        """
        # Handle response and observe
        observation = self.handle_service_response(plan, step, service_response)

        # Record observation in plan
        self.todo_manager.record_observation(plan, step.id, observation)

        # Update step based on observation
        if observation.matched_expectation:
            actual_result = service_response.get("result", {}).get("output", "")
            self.todo_manager.mark_step_completed(plan, step.id, str(actual_result))
        else:
            if step.retry_count < step.max_retries:
                # Will retry
                step.retry_count += 1
            else:
                # Mark failed
                error = service_response.get("error", "Unknown error")
                self.todo_manager.mark_step_failed(plan, step.id, error)

        # Decide next action
        next_action = self.decide_next_action(plan, observation)

        return plan, next_action

    def get_plan_status(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """
        Get current status of plan.

        Returns:
            Dict with plan status, current step, progress, etc
        """
        remaining = self.todo_manager.get_remaining_steps(plan)
        current = self.todo_manager.get_current_step(plan)

        return {
            "plan_id": plan.plan_id,
            "objective": plan.objective,
            "status": plan.status.value if hasattr(plan.status, "value") else str(plan.status),
            "current_step": current.description if current else None,
            "progress": f"{len(plan.steps) - len(remaining)}/{len(plan.steps)}",
            "remaining": len(remaining),
            "can_continue": self.todo_manager.can_continue(plan),
        }
