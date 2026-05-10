"""
Knowledge Tier Router - Intelligently routes queries to appropriate knowledge sources.

Implements hybrid classification:
1. Fast pattern-based detection (keywords, syntax)
2. LLM fallback if confidence < 0.7

Four knowledge tiers:
- Tier 1: Internal LLM (conversational, reasoning, general knowledge)
- Tier 2: Wikipedia + structured sources (factual, definitions, background)
- Tier 3: API/Backend search (structured fast data: prices, weather, results)
- Tier 4: Browser automation + ScrapeGraphAI (interactive, JavaScript-heavy sites)
"""

from typing import Dict, Any, Tuple, Optional
import re


# ============================================================================
# PATTERN-BASED CLASSIFICATION (Fast, O(1))
# ============================================================================

class QueryClassifier:
    """Pattern-based query classification."""

    # Keywords that indicate API search is best
    API_SEARCH_KEYWORDS = [
        "price", "cost", "weather", "stock", "exchange rate", "current",
        "today", "tomorrow", "forecast", "latest", "news", "update",
        "score", "standings", "results", "match", "game",
    ]

    # Keywords that indicate Wikipedia/factual tier
    WIKIPEDIA_KEYWORDS = [
        "what is", "who is", "who was", "explain", "define", "definition",
        "history of", "about", "background", "information",
        "biography", "wikipedia", "facts", "statistics",
    ]

    # Keywords that indicate browser automation is needed
    BROWSER_KEYWORDS = [
        "click", "navigate", "scroll", "login", "fill out", "submit",
        "interact", "browse", "find on page", "button", "link",
        "javascript", "dynamic", "single page",
    ]

    # Keywords that indicate internal reasoning
    REASONING_KEYWORDS = [
        "explain", "why", "how does", "reason", "think", "opinion",
        "help", "suggest", "recommend", "advice", "problem",
    ]

    @staticmethod
    def classify(query: str) -> Tuple[str, float]:
        """
        Classify query using pattern matching.

        Args:
            query: User query string

        Returns:
            (tier_name, confidence: 0.0-1.0)
        """
        query_lower = query.lower().strip()

        # Check for browser automation (highest priority - unambiguous)
        if any(kw in query_lower for kw in QueryClassifier.BROWSER_KEYWORDS):
            return "browser", 0.95

        # Check for API/search queries (very high confidence)
        if any(kw in query_lower for kw in QueryClassifier.API_SEARCH_KEYWORDS):
            return "api_search", 0.95

        # Check for Wikipedia/factual queries
        if any(kw in query_lower for kw in QueryClassifier.WIKIPEDIA_KEYWORDS):
            return "wikipedia", 0.90

        # Check for reasoning/conversational (requires deeper understanding)
        if any(kw in query_lower for kw in QueryClassifier.REASONING_KEYWORDS):
            return "internal_llm", 0.75

        # Query ends with question mark - likely conversational
        if query_lower.endswith("?"):
            return "internal_llm", 0.70

        # Default: uncertain, needs LLM decision
        return "internal_llm", 0.50


# ============================================================================
# FALLBACK CHAIN MANAGEMENT
# ============================================================================

FALLBACK_CHAINS = {
    "internal_llm": ["wikipedia", "api_search", "browser"],
    "wikipedia": ["api_search", "browser"],
    "api_search": ["browser"],
    "browser": [],  # Last resort, no fallback
}


def get_fallback_chain(tier: str) -> list:
    """Get fallback chain for a knowledge tier."""
    return FALLBACK_CHAINS.get(tier, [])


# ============================================================================
# LLM-BASED TIER DECISION (Fallback when confidence is low)
# ============================================================================

def get_llm_tier_decision(query: str, context: Optional[Dict[str, Any]] = None) -> str:
    """
    Ask LLM which tier is best for this query.

    Args:
        query: User query
        context: Optional execution context

    Returns:
        Tier name ("internal_llm", "wikipedia", "api_search", "browser")
    """
    try:
        from brain.llm import get_llm_response
    except ImportError:
        # Fallback if LLM not available
        return "internal_llm"

    prompt = f"""
Which knowledge source is best for this query?

Query: {query}

Choose ONE:
- internal_llm: For conversational, reasoning, explanation questions
- wikipedia: For factual, definitions, background information
- api_search: For structured fast data (prices, weather, current info)
- browser: For interactive tasks (clicking, navigating, form filling)

Respond with ONLY the tier name (no explanation).
"""

    try:
        response = get_llm_response(prompt, model="qwen2.5-coder")
        # Parse response - just take first valid option
        response_lower = response.lower().strip()

        for tier in ["internal_llm", "wikipedia", "api_search", "browser"]:
            if tier in response_lower:
                return tier

        # Default fallback
        return "internal_llm"
    except Exception:
        return "internal_llm"


# ============================================================================
# MAIN ROUTING FUNCTION
# ============================================================================

def route_query(query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Route a query to the appropriate knowledge tier.

    Hybrid approach:
    1. Use fast pattern-based classification
    2. If confidence < 0.7, ask LLM for decision
    3. Return tier + fallback chain

    Args:
        query: User query
        context: Optional execution context

    Returns:
        Dict with keys:
            - tier: Selected tier name
            - confidence: Confidence score (0.0-1.0)
            - fallback_chain: List of fallback tiers
            - reasoning: Why this tier was chosen
    """
    context = context or {}

    # Step 1: Pattern-based classification (fast)
    tier, confidence = QueryClassifier.classify(query)

    # Step 2: LLM decision if confidence is low
    if confidence < 0.7:
        llm_tier = get_llm_tier_decision(query, context)
        return {
            "tier": llm_tier,
            "confidence": 0.95,  # Trust LLM decision
            "fallback_chain": get_fallback_chain(llm_tier),
            "reasoning": f"Low confidence pattern match ({confidence:.2f}); LLM decided: {llm_tier}",
        }

    # Step 3: Pattern-matched result is confident enough
    return {
        "tier": tier,
        "confidence": confidence,
        "fallback_chain": get_fallback_chain(tier),
        "reasoning": f"Pattern match: {tier} (confidence: {confidence:.2f})",
    }


# ============================================================================
# UTILITY: Explain routing decision
# ============================================================================

def explain_routing(query: str) -> str:
    """
    Get a human-readable explanation of routing decision.

    Args:
        query: User query

    Returns:
        Explanation string
    """
    decision = route_query(query)

    msg = f"Query: {query}\n"
    msg += f"Selected tier: {decision['tier']}\n"
    msg += f"Confidence: {decision['confidence']:.1%}\n"
    msg += f"Reasoning: {decision['reasoning']}\n"

    if decision['fallback_chain']:
        msg += f"Fallback chain: {' → '.join(decision['fallback_chain'])}"
    else:
        msg += f"Fallback chain: (none - {decision['tier']} is final resort)"

    return msg
