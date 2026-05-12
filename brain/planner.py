"""
Planner - generates structured execution plans for large tasks.
Asks GPT-OSS: "Generate steps, expected results, risks, and fallback conditions."
"""

from typing import Dict, Any, List
from todo.schemas import ExecutionPlan, ExecutionStep, StepStatus
from brain.llm import get_llm_response
import json


def create_plan(objective: str, context: Dict[str, Any] = None) -> ExecutionPlan:
    """
    Create an execution plan for an objective.

    For large tasks, asks LLM to generate structured steps with:
    - Description
    - Expected results
    - Success criteria
    - Target service (executor, coder, thinker)
    - Query maker (query_maker1 or query_maker2)
    - Dependencies

    Args:
        objective: What needs to be done
        context: Optional context about the task

    Returns:
        ExecutionPlan with structured steps
    """

    prompt = f"""You are a task planner. Create a detailed execution plan.

OBJECTIVE:
{objective}

CONTEXT:
{json.dumps(context or {{}}, indent=2)}

Create a step-by-step plan with:
1. Clear steps (not vague)
2. Expected results for each step
3. Success criteria (what proves it worked)
4. Target service (executor/coder/thinker/query_maker1/query_maker2)
5. Dependencies between steps (if any)

Rules:
- executor: runs shell commands, tools, system operations
- coder: generates/writes/modifies code
- thinker: analyzes, reasons, makes decisions
- query_maker1: gets context for fast operations
- query_maker2: gets context for complex reasoning

For each step, respond with:
{{
    "id": "step_1",
    "description": "What to do",
    "expected_result": "What success looks like",
    "success_criteria": ["criterion1", "criterion2"],
    "target": "executor|coder|thinker",
    "query_maker": "query_maker1" or "query_maker2",
    "depends_on": ["step_0"] or []
}}

Respond with JSON array of steps:
[
    {{ "id": "step_1", ... }},
    {{ "id": "step_2", ... }},
    ...
]
"""

    try:
        response_text = get_llm_response(prompt, role="deep_thinking_model")

        # Parse JSON response
        steps_data = json.loads(response_text)

        # Build ExecutionPlan
        plan = ExecutionPlan(
            plan_id=f"plan_{objective[:20].lower().replace(' ', '_')}",
            objective=objective,
            created_by="brain",
            context=context or {},
        )

        # Convert step data to ExecutionStep objects
        for step_data in steps_data:
            step = ExecutionStep(
                id=step_data.get("id", f"step_{len(plan.steps)}"),
                description=step_data.get("description", ""),
                expected_result=step_data.get("expected_result", ""),
                success_criteria=step_data.get("success_criteria", []),
                target=step_data.get("target", "executor"),
                query_maker=step_data.get("query_maker"),
                depends_on=step_data.get("depends_on", []),
                action="dispatch_tool",  # Default, can be overridden
                payload={},  # Will be filled during execution
            )
            plan.steps.append(step)

        # Set first step as current
        if plan.steps:
            plan.current_step_id = plan.steps[0].id

        return plan

    except Exception as e:
        # Fallback: create simple single-step plan
        print(f"⚠ Planner error: {str(e)}, creating fallback plan")
        plan = ExecutionPlan(
            plan_id="plan_fallback",
            objective=objective,
            created_by="brain",
            context={"error": str(e)},
        )

        # Single fallback step
        step = ExecutionStep(
            id="step_1",
            description=f"Execute: {objective}",
            expected_result="Task completed",
            success_criteria=["Completed"],
            target="executor",
            action="dispatch_tool",
            payload={"task": objective},
        )
        plan.steps.append(step)
        plan.current_step_id = "step_1"

        return plan


def create_simple_plan(objective: str) -> ExecutionPlan:
    """
    Create a simple single-step plan without LLM.
    Used for quick/obvious tasks.
    """
    plan = ExecutionPlan(
        plan_id=f"simple_{objective[:15].lower().replace(' ', '_')}",
        objective=objective,
        created_by="brain",
    )

    step = ExecutionStep(
        id="step_1",
        description=f"Execute: {objective}",
        expected_result="Task completed successfully",
        success_criteria=["Completed", "No errors"],
        target="executor",
        action="dispatch_tool",
        payload={"task": objective},
    )
    plan.steps.append(step)
    plan.current_step_id = "step_1"

    return plan


def classify_task_size(objective: str) -> str:
    """
    Classify task as small or large to decide if we need planning.

    Small: Can be done in 1-2 steps
    Large: Needs multi-step plan

    Args:
        objective: What needs to be done

    Returns:
        "small" or "large"
    """
    objective_lower = objective.lower()

    # Heuristics for large tasks
    large_indicators = [
        "implement", "build", "design", "architect", "refactor",
        "plan", "analyze", "investigate", "debug", "troubleshoot",
        "optimize", "improve", "migrate", "restructure",
    ]

    for indicator in large_indicators:
        if indicator in objective_lower:
            return "large"

    # Quick tasks are small
    if any(word in objective_lower for word in ["run", "execute", "click", "type", "read"]):
        return "small"

    # Default to small
    return "small"
