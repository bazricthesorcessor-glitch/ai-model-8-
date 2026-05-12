# Query Maker Integration Guide
## Connecting Query Makers to Scout Memory System

**Purpose**: Show how Query Maker 1 (LLM) and Query Maker 2 (Agents) integrate with the new Scout memory system.

---

## Overview

### Query Maker 1 (For LLM - Full Context)
```
User Query
    ↓
Query Maker 1
    ├─ ContextCompiler.compile_scout_context(query)
    │   ├─ Loads ALL 9 sections
    │   ├─ 1M token budget
    │   └─ Complete Scout reasoning context
    ↓
LLM (Claude) with Full Context
    ├─ Makes strategic decisions
    ├─ Reasons about multiple options
    └─ Coordinates with agents
    ↓
Response to User
```

### Query Maker 2 (For Agents - Focused Context)
```
Task for Specific Agent
    ↓
Query Maker 2
    ├─ ContextCompiler.compile_agent_context(agent_name, query, memory_type)
    │   ├─ Loads agent's SPECIFIC memory type only
    │   ├─ Agent-focused context
    │   └─ Minimal, efficient prompt
    ↓
Agent (Executor, etc.) with Focused Context
    ├─ Executes specific task
    └─ Reports results
    ↓
Results logged to agent memory
```

---

## Query Maker 1 Implementation

### Current File Location
`/home/dmannu/ai-model-8/tools/query_maker1.py`

### Required Changes

```python
# OLD (before integration)
def compile_context(query: str) -> str:
    """Compile context for LLM."""
    # ... manual context building ...
    return context

# NEW (after integration)
from memory import ContextCompiler

def compile_context(query: str) -> str:
    """Compile full Scout context for LLM reasoning."""
    context = ContextCompiler.compile_scout_context(
        query=query,
        include_sections=[
            "identity",
            "time_date", 
            "state",
            "agents",
            "important_memory",
            "recent_14_days",
            "relevant_archive",
            "tools",
            "current_query"
        ],
        custom_token_allocation=None  # Use defaults
    )
    return context

def use_context(context: str, query: str) -> str:
    """Send context to LLM and get response."""
    prompt = f"{context}\n\nTask: {query}"
    response = llm.call(prompt, max_tokens=50000)
    return response
```

### Integration Steps
1. Import `ContextCompiler` from memory module
2. Replace manual context compilation with `ContextCompiler.compile_scout_context()`
3. Pass full context to LLM
4. Log LLM decisions back to daily log
5. Update state snapshots based on decisions

---

## Query Maker 2 Implementation

### Current File Location
`/home/dmannu/ai-model-8/tools/query_maker2.py`

### Required Changes

```python
# OLD (before integration)
def compile_agent_context(agent_name: str, query: str) -> str:
    """Compile context for specific agent."""
    # ... manual context building ...
    return context

# NEW (after integration)
from memory import ContextCompiler

def compile_agent_context(agent_name: str, query: str, memory_type: str = "recent") -> str:
    """Compile agent-specific context (agent's memory type only)."""
    context = ContextCompiler.compile_agent_context(
        agent_name=agent_name,
        query=query,
        memory_type=memory_type  # "recent", "archive", "learned", or "context"
    )
    return context

def execute_with_context(agent_name: str, query: str, memory_type: str = "recent") -> dict:
    """Send context to agent and get execution results."""
    context = compile_agent_context(agent_name, query, memory_type)
    
    # Send to agent (via executor, etc.)
    result = agent_executor.execute(
        agent_name=agent_name,
        context=context,
        query=query
    )
    
    # Log execution
    from memory import MemoryWriter
    MemoryWriter.log_execution_history({
        "agent": agent_name,
        "query": query,
        "result": result.get("status"),
        "duration": result.get("duration")
    })
    
    # Update agent's memory with results
    MemoryWriter.save_agent_memory(
        agent_name=agent_name,
        memory_type=memory_type,
        data=result.get("memory_update", {})
    )
    
    return result
```

### Integration Steps
1. Import `ContextCompiler` from memory module
2. Replace manual context compilation with `ContextCompiler.compile_agent_context()`
3. Pass agent-specific context to agent execution
4. Log execution results to execution history
5. Update agent's memory with results
6. Route results back to Scout

---

## Integration with Scout Context Router

### File Location
`/home/dmannu/ai-model-8/scout/scout_context_router.py`

### Purpose
Routes queries to appropriate context compiler based on recipient (LLM vs Agent).

### Implementation

```python
from memory import ContextCompiler
from tools.query_maker1 import compile_context as qm1_compile
from tools.query_maker2 import compile_agent_context as qm2_compile

class ScoutContextRouter:
    """Routes context based on conversation partner."""
    
    @staticmethod
    def route_query(query: str, target: str) -> str:
        """
        Args:
            query: The query/task
            target: "llm" for full context, agent_name for focused context
        
        Returns:
            Compiled context string
        """
        if target == "llm":
            # Full Scout context for LLM reasoning
            return ContextCompiler.compile_scout_context(query)
        else:
            # Agent-specific context (their memory type only)
            return ContextCompiler.compile_agent_context(
                agent_name=target,
                query=query,
                memory_type="recent"
            )
    
    @staticmethod
    def route_and_execute(query: str, target: str) -> dict:
        """
        Route query, execute with appropriate context, and log results.
        
        Args:
            query: The query/task
            target: "llm" or agent_name
        
        Returns:
            Execution result with context and output
        """
        context = ScoutContextRouter.route_query(query, target)
        
        if target == "llm":
            # Execute with LLM
            result = llm.call(context + f"\n\nTask: {query}")
            context_type = "scout_llm"
        else:
            # Execute with agent
            result = execute_agent(target, context, query)
            context_type = f"agent_{target}"
        
        # Log routing decision
        from memory import MemoryWriter
        entry = MemoryWriter.create_daily_log_entry(
            log_type="routing",
            message=f"Routed query to {target}",
            category="system",
            data={"context_type": context_type}
        )
        MemoryWriter.log_to_daily(entry)
        
        return {
            "target": target,
            "result": result,
            "context_type": context_type
        }
```

---

## Memory Logging Integration

### What to Log

Every Scout decision and agent execution should log:

```python
# Scout decision logging
MemoryWriter.log_to_daily({
    "timestamp": datetime.now().isoformat(),
    "type": "scout_decision",
    "message": "Decided to delegate task to executor",
    "category": "coordination",
    "data": {
        "reasoning": "Task requires UI control",
        "agent": "executor",
        "confidence": 0.95
    }
})

# Agent execution logging
MemoryWriter.log_execution_history({
    "timestamp": datetime.now().isoformat(),
    "agent": "executor",
    "action": "clicked_button",
    "target": "submit_button",
    "result": "success",
    "duration_ms": 250
})

# State update logging
MemoryWriter.save_state_snapshot({
    "current_focus": "browser_control",
    "active_workspace": "dev_env",
    "browser_url": "example.com"
})
```

---

## Token Allocation Strategy

### Query Maker 1 (LLM) - 1M Token Budget

Total available: 900,000 tokens

```
Identity:           2%  (18,000)   - Scout's role & preferences
Time/Date:         0.5% (4,500)   - Current temporal context
State:             10%  (90,000)  - System state
Agents:             5%  (45,000)  - Agent capabilities
Important Memory:   8%  (72,000)  - Explicit important items
Recent 14 Days:    20%  (180,000) - History for context
Relevant Archive:  25%  (225,000) - Related past items
Tools:             10%  (90,000)  - Available capabilities
Current Query:     15%  (135,000) - The task itself
Reserved:           5%  (45,000)  - Buffer/adjustments
```

### Query Maker 2 (Agent) - Focused Budget

For agents, use much smaller context (50-100K tokens):

```python
# For agent context, use selective allocation
agent_token_budget = 100_000
custom_allocation = {
    "current_query": 0.5,    # 50K - The immediate task
    "agents": 0.3,            # 30K - Agent's own capabilities
    "tools": 0.2,             # 20K - Available tools
}

context = ContextCompiler.compile_agent_context(
    agent_name="executor",
    query=query,
    memory_type="recent"
)
```

---

## Testing the Integration

### Test 1: Query Maker 1 Context

```python
from memory import ContextCompiler

context = ContextCompiler.compile_scout_context(
    query="What should I work on next?"
)
print(f"Scout context generated: {len(context)} characters")
assert "IDENTITY" in context
assert "CURRENT QUERY" in context
```

### Test 2: Query Maker 2 Context

```python
from memory import ContextCompiler

context = ContextCompiler.compile_agent_context(
    agent_name="executor",
    query="Open Firefox and go to example.com",
    memory_type="recent"
)
print(f"Agent context generated: {len(context)} characters")
assert "AGENT: executor" in context
assert "Tools Available" in context
```

### Test 3: Full Routing

```python
from scout.scout_context_router import ScoutContextRouter

# Route to LLM
llm_result = ScoutContextRouter.route_and_execute(
    query="Plan my day",
    target="llm"
)

# Route to agent
agent_result = ScoutContextRouter.route_and_execute(
    query="Open Firefox",
    target="executor"
)
```

---

## Checklist for Integration

- [ ] Update `tools/query_maker1.py` to use `ContextCompiler`
- [ ] Update `tools/query_maker2.py` to use `ContextCompiler`
- [ ] Update `scout/scout_context_router.py` to use new system
- [ ] Add logging to Scout decision flow
- [ ] Add logging to agent execution flow
- [ ] Test Query Maker 1 context generation
- [ ] Test Query Maker 2 context generation
- [ ] Test routing between LLM and agents
- [ ] Verify memory updates are logged
- [ ] Verify state snapshots are saved
- [ ] Load recent context and verify accuracy
- [ ] Test 14-day memory retrieval
- [ ] Test archive searching

---

## Current Implementation Status

| Component | Status | File |
|-----------|--------|------|
| ContextCompiler | ✅ Complete | `memory/compiler.py` |
| MemoryWriter | ✅ Complete | `memory/writer.py` |
| MemoryReader | ✅ Complete | `memory/reader.py` |
| Paths | ✅ Complete | `memory/paths.py` |
| Query Maker 1 | ⏳ Needs Integration | `tools/query_maker1.py` |
| Query Maker 2 | ⏳ Needs Integration | `tools/query_maker2.py` |
| Scout Router | ⏳ Needs Integration | `scout/scout_context_router.py` |

---

## Next Steps

1. **Immediate** (Can do now):
   - Integrate Query Maker 1 with ContextCompiler
   - Integrate Query Maker 2 with ContextCompiler
   - Update Scout router to use new system
   - Add comprehensive logging

2. **Short-term** (After integration):
   - Create memory schemas for type safety
   - Add advanced search capabilities
   - Build expiry/cleanup system
   - Add memory compression

3. **Long-term** (Optimization):
   - Semantic relationship indexing
   - Intelligent context selection
   - Memory encryption for sensitive data
   - Performance optimization

---

Created: May 12, 2026  
Status: Foundation Ready for Integration  
Next File: `memory/schemas.py` (data models)
