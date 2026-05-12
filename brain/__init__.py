"""
Brain module - decision making and intent detection.
Reads from config, calls LLM, returns structured actions.
Does NOT call executor, tools, or state directly - uses router only.
"""

from .brain import analyze_intent, generate_action_legacy, check_safety, is_conversational
from .planner import create_plan, create_simple_plan, classify_task_size
from .observer import observe_step_result, simple_observe

__all__ = [
    # Core analysis
    "analyze_intent",
    "check_safety",
    "is_conversational",
    # Legacy support
    "generate_action_legacy",
    # New architecture
    "create_plan",
    "create_simple_plan",
    "classify_task_size",
    "observe_step_result",
    "simple_observe",
]
