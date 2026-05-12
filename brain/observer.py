"""
Observer - verifies step execution against expected results.
Answers: What happened? Was it expected? Should we continue?
"""

from typing import Dict, Any, Optional
from todo.schemas import StepObservation
from brain.llm import get_llm_response
from brain.json_utils import extract_json_object


def observe_step_result(
    step_id: str,
    step_description: str,
    expected_result: str,
    success_criteria: list,
    actual_feedback: str,
) -> StepObservation:
    """
    Observe and interpret step execution result.

    Uses LLM to compare expected vs actual and determine next action.

    Args:
        step_id: ID of the step being observed
        step_description: What the step was supposed to do
        expected_result: What success looks like
        success_criteria: List of criteria that indicate success
        actual_feedback: What actually happened

    Returns:
        StepObservation with confidence, status, and recommendation
    """

    prompt = f"""You are an execution observer. Verify if a step succeeded.

STEP: {step_description}

EXPECTED RESULT:
{expected_result}

SUCCESS CRITERIA:
{chr(10).join(f"- {crit}" for crit in success_criteria)}

ACTUAL FEEDBACK:
{actual_feedback}

Analyze:
1. Did the step succeed? (Yes/No/Uncertain)
2. Confidence level (0.0 to 1.0)
3. Reason for your assessment
4. What should happen next? (continue/retry/replan/stop)

Respond in JSON:
{{
    "succeeded": true/false,
    "confidence": 0.85,
    "reason": "Explanation here",
    "next_action": "continue"
}}
"""

    try:
        response_text = get_llm_response(prompt, role="deep_thinking_model")

        # Parse JSON response robustly
        response_json = extract_json_object(response_text)
        if response_json is None:
            print("⚠ Observer failed to extract JSON, returning uncertain")
            return StepObservation(
                step_id=step_id,
                matched_expectation=False,
                confidence=0.0,
                status="uncertain",
                reason="Observer could not parse response",
                recommended_next="stop",
                feedback=actual_feedback,
            )

        succeeded = response_json.get("succeeded", False)
        confidence = float(response_json.get("confidence", 0.5))
        reason = response_json.get("reason", "Unknown")
        next_action = response_json.get("next_action", "stop")

        # Determine status
        if succeeded:
            status = "success"
        elif confidence < 0.3:
            status = "uncertain"
        else:
            status = "failed"

        # Map next_action to our enums
        recommended = next_action.lower()
        if recommended not in ["continue", "retry", "replan", "stop"]:
            recommended = "stop"

        return StepObservation(
            step_id=step_id,
            matched_expectation=succeeded,
            confidence=confidence,
            status=status,
            reason=reason,
            recommended_next=recommended,
            feedback=actual_feedback,
        )

    except Exception as e:
        # Fallback to conservative assessment
        print(f"⚠ Observer error: {str(e)}")
        return StepObservation(
            step_id=step_id,
            matched_expectation=False,
            confidence=0.0,
            status="uncertain",
            reason=f"Observer error: {str(e)}",
            recommended_next="stop",
            feedback=actual_feedback,
        )


def simple_observe(
    expected: str,
    actual: str,
    success_indicators: Optional[list] = None
) -> bool:
    """
    Simple observation: does actual contain expected patterns?
    Use for quick checks without LLM.

    Args:
        expected: Expected output substring/pattern
        actual: Actual output
        success_indicators: List of patterns, any matching = success

    Returns:
        True if expected found or success_indicator matched
    """
    actual_lower = actual.lower()
    expected_lower = expected.lower()

    # Check if expected appears in actual
    if expected_lower in actual_lower:
        return True

    # Check success indicators
    if success_indicators:
        for indicator in success_indicators:
            if indicator.lower() in actual_lower:
                return True

    return False
