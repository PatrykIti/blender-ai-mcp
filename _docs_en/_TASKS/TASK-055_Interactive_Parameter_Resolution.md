# TASK-055: Interactive Parameter Resolution via LLM Feedback

## Status: ✅ Done (with FIX-2 applied)
## Priority: 🔴 High
## Created: 2025-12-08
## Updated: 2025-12-09 (FIX-2: Semantic Matching Improvements)

---

## Recent Fixes

### FIX-2: Semantic Matching Improvements (2025-12-09) ✅

**Problem**: "table with legs X" incorrectly matched "straight legs" YAML modifier because n-gram matching only required 1 word to match.

**Solution**:
1. **Multi-word matching**: Require min(N, 2) words to match for N-word modifiers
2. **Negative signals**: YAML-defined contradictory terms that reject matches
3. **Per-word threshold**: 0.65 (allows multilingual fuzzy matching)

**Impact**:
- ✅ "table with legs X" now correctly returns `needs_input`
- ✅ "simple table with straight legs" still matches "straight legs"

See: **TASK-055-FIX-2_Semantic_Matching_Improvements.md**

### FIX-1: Defaults Removal (2025-12-09) ✅

**Problem**: ModifierExtractor included workflow defaults in modifiers dict, causing ParameterResolver TIER 1 to always win.

**Solution**: Removed defaults from ModifierExtractor - now handled only in ParameterResolver TIER 3.

See: **TASK-055-FIX_Unified_Parameter_Resolution.md**

---

## Overview

Enable MCP server to **ask the connected LLM** for parameter values when it doesn't know them, instead of requiring all parameter mappings in YAML workflow files. The system learns from LLM responses and stores mappings for future use.

**Key Design Principle:** This is an **extension** of the existing modifier system, not a replacement. Both systems coexist - workflows can define explicit modifiers in YAML, AND the interactive system can learn new ones dynamically.

## Problem Statement

Currently, workflow YAML files require explicit modifier mappings:

```yaml
modifiers:
  "straight legs":
    leg_angle_left: 0
    leg_angle_right: 0
  "proste nogi":      # Polish variant needed
    leg_angle_left: 0
  "prostymi nogami":  # Another Polish variant needed
    leg_angle_left: 0
```

This is not scalable - every language variant must be manually defined.

## Solution

**Three-tier parameter resolution (in order):**

1. **Tier 1: YAML Modifiers (existing)** - `ModifierExtractor` checks if explicit modifier matches prompt → **USE IT, SKIP REST**
2. **Tier 2: Learned Mappings (LanceDB)** - Check if we've learned similar prompt before via LaBSE
3. **Tier 3: LLM Interactive (new)** - If neither matches, ask LLM for parameter values

**Key rule:** If YAML modifier exists for the semantic, use it directly - no LLM interaction needed. Interactive resolution is only for cases where no YAML mapping exists.

Router asks LLM for unknown parameter values and stores the answers in a **semantic knowledge store** (LanceDB with LaBSE embeddings). Over time, the system learns and reduces LLM queries.

```
Resolution Priority:
┌─────────────────────────────────────────────────────────────────────────┐
│  1. ModifierExtractor.extract()    ← Explicit YAML                    │
│     ↓ FOUND → USE IT (done!)                                              │
│     ↓ NOT FOUND                                                           │
│  2. ParameterStore.find_mapping()  ← Learned from LLM                   │
│     ↓ FOUND → USE IT (done!)                                              │
│     ↓ NOT FOUND                                                           │
│  3. Ask LLM via "needs_parameter_input" response                         │
│     ↓ LLM responds                                                        │
│  4. Store in ParameterStore for future                                    │
└─────────────────────────────────────────────────────────────────────────┘
```

**Example scenarios:**

| Prompt | YAML has modifier? | Learned? | Action |
|--------|-------------------|----------|--------|
| "straight legs" | ✅ Yes | - | Use YAML modifier |
| "proste nogi" | ❌ No | ❌ No | Ask LLM, store answer |
| "pionowe nogi" | ❌ No | ✅ Yes (similar to "proste nogi") | Use learned mapping |
| "nachylone nogi" | ❌ No | ❌ No | Ask LLM, store answer |

### Flow

```
1. User: "prosty stół z prostymi nogami"

2. Router:
   → Matches workflow: picnic_table
   → Sees parameter: leg_angle (default: 0.32)
   → LaBSE detects "prostymi nogami" relates to leg_angle
   → Checks ParameterStore → NOT FOUND

3. Router returns to LLM:
   {
     "status": "needs_parameter_input",
     "questions": [{
       "parameter": "leg_angle_left",
       "context": "prostymi nogami",
       "description": "rotation angle for table legs",
       "range": [-1.57, 1.57],
       "default": 0.32
     }]
   }

4. LLM (Claude Code/Cline/etc.) responds:
   router_resolve_parameter(
     parameter_name="leg_angle_left",
     value=0,
     context="prostymi nogami"
   )

5. Router:
   → Uses leg_angle=0
   → SAVES mapping: "prostymi nogami" → leg_angle=0

6. Next time "proste nogi" or "straight legs":
   → LaBSE finds similar stored mapping → leg_angle=0
   → No need to ask LLM!
```

---

## Sub-tasks

### TASK-055-0: Domain Interfaces (Clean Architecture)
**Status:** ✅ Done

Create abstract interfaces following Clean Architecture pattern:

**File:** `server/router/domain/interfaces/i_parameter_resolver.py`

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class IParameterStore(ABC):
    """Abstract interface for parameter mapping storage."""

    @abstractmethod
    def find_mapping(
        self,
        prompt: str,
        parameter_name: str,
        workflow_name: str,
        similarity_threshold: float = 0.85
    ) -> Optional["StoredMapping"]:
        """Find semantically similar stored mapping."""
        pass

    @abstractmethod
    def store_mapping(
        self,
        context: str,
        parameter_name: str,
        value: Any,
        workflow_name: str
    ) -> None:
        """Store LLM-provided value with embedding."""
        pass


class IParameterResolver(ABC):
    """Abstract interface for parameter resolution."""

    @abstractmethod
    def resolve(
        self,
        prompt: str,
        workflow_name: str,
        parameters: Dict[str, "ParameterSchema"],
        existing_modifiers: Dict[str, Any]
    ) -> "ParameterResolutionResult":
        """Resolve parameters using learned mappings + modifiers."""
        pass
```

**Tests:** `tests/unit/router/domain/interfaces/test_i_parameter_resolver.py`

---

### TASK-055-1: Domain Entities
**Status:** ✅ Done

Create domain entities for parameter resolution:

**File:** `server/router/domain/entities/parameter.py`

```python
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Tuple, Union

@dataclass
class ParameterSchema:
    """Schema definition for a workflow parameter."""
    name: str
    type: str  # "float", "int", "bool", "string"
    range: Optional[Tuple[float, float]] = None
    default: Any = None
    description: str = ""
    semantic_hints: List[str] = field(default_factory=list)
    group: Optional[str] = None  # For grouped params like "leg_angles"

@dataclass
class StoredMapping:
    """A learned parameter mapping from LLM."""
    context: str          # Original prompt fragment
    value: Any            # Resolved value
    similarity: float     # How well it matched the query
    workflow_name: str
    parameter_name: str
    usage_count: int = 1

@dataclass
class UnresolvedParameter:
    """Parameter that needs LLM input."""
    name: str
    schema: ParameterSchema
    context: str  # Extracted from prompt
    relevance: float  # LaBSE similarity score

@dataclass
class ParameterResolutionResult:
    """Result of parameter resolution attempt."""
    resolved: Dict[str, Any]  # Known values (from store or modifiers)
    unresolved: List[UnresolvedParameter]  # Need LLM input
    resolution_sources: Dict[str, str] = field(default_factory=dict)
    # Maps param_name -> "learned" | "yaml_modifier" | "default"

    @property
    def needs_llm_input(self) -> bool:
        """True if there are unresolved parameters."""
        return len(self.unresolved) > 0

    @property
    def is_complete(self) -> bool:
        """True if all parameters are resolved."""
        return len(self.unresolved) == 0
```

**Tests:** `tests/unit/router/domain/entities/test_parameter.py`

---

### TASK-055-2: Parameter Store (LanceDB Persistence)
**Status:** ✅ Done

Create LanceDB-based store for learned parameter mappings:

**File:** `server/router/application/resolver/parameter_store.py`

```python
class ParameterStore:
    """Stores learned parameter mappings with LaBSE embeddings."""

    def __init__(self, classifier: WorkflowIntentClassifier, db_path: str):
        self._classifier = classifier
        self._db = lancedb.connect(db_path)
        self._table = self._ensure_table()

    def store_mapping(
        self,
        context: str,
        parameter_name: str,
        value: Any,
        workflow_name: str
    ) -> None:
        """Store LLM-provided value with embedding."""
        embedding = self._classifier.get_embedding(context)
        self._table.add([{
            "context": context,
            "embedding": embedding,
            "parameter": parameter_name,
            "value": value,
            "workflow": workflow_name,
            "created_at": datetime.now().isoformat()
        }])

    def find_mapping(
        self,
        prompt: str,
        parameter_name: str,
        similarity_threshold: float = 0.85
    ) -> Optional[StoredMapping]:
        """Find semantically similar stored mapping."""
        embedding = self._classifier.get_embedding(prompt)
        results = self._table.search(embedding)\
            .where(f"parameter = '{parameter_name}'")\
            .limit(1)\
            .to_list()

        if results and results[0]["_distance"] < (1 - similarity_threshold):
            return StoredMapping(
                context=results[0]["context"],
                value=results[0]["value"],
                similarity=1 - results[0]["_distance"]
            )
        return None
```

**Tests:** `tests/unit/router/application/resolver/test_parameter_store.py`
- Test store and retrieve mapping
- Test LaBSE similarity matching (Polish → English)
- Test threshold filtering
- Test multiple parameters for same workflow

---

### TASK-055-3: Parameter Resolver
**Status:** ✅ Done

Create resolver that combines YAML modifiers → learned mappings → LLM fallback:

**File:** `server/router/application/resolver/parameter_resolver.py`

```python
class ParameterResolver(IParameterResolver):
    """Resolves workflow parameters using three-tier system.

    Priority:
    1. YAML modifiers (from ModifierExtractor / EnsembleResult)
    2. Learned mappings (from ParameterStore via LaBSE)
    3. Mark as unresolved (needs LLM input)
    """

    def __init__(
        self,
        classifier: WorkflowIntentClassifier,
        store: ParameterStore,
        relevance_threshold: float = 0.5
    ):
        self._classifier = classifier
        self._store = store
        self._relevance_threshold = relevance_threshold

    def resolve(
        self,
        prompt: str,
        workflow_name: str,
        parameters: Dict[str, ParameterSchema],
        existing_modifiers: Dict[str, Any]  # From ModifierExtractor/EnsembleMatcher
    ) -> ParameterResolutionResult:
        """Resolve parameters using three-tier system.

        Args:
            prompt: User prompt for semantic matching
            workflow_name: Current workflow name
            parameters: Parameter schemas from workflow definition
            existing_modifiers: Already extracted modifiers from YAML
        """
        resolved = {}
        unresolved = []
        sources = {}

        for param_name, schema in parameters.items():
            # TIER 1: Check YAML modifiers first (highest priority)
            if param_name in existing_modifiers:
                resolved[param_name] = existing_modifiers[param_name]
                sources[param_name] = "yaml_modifier"
                continue

            # TIER 2: Check learned mappings (from previous LLM interactions)
            stored = self._store.find_mapping(
                prompt=prompt,
                parameter_name=param_name,
                workflow_name=workflow_name
            )
            if stored:
                resolved[param_name] = stored.value
                sources[param_name] = "learned"
                # Increment usage count for analytics
                self._store.increment_usage(stored)
                continue

            # TIER 3: Check if prompt relates to this parameter
            relevance = self._classifier.similarity(
                prompt,
                schema.description
            )

            if relevance > self._relevance_threshold:
                # Prompt mentions this parameter but we don't know value
                # → Mark for LLM resolution
                unresolved.append(UnresolvedParameter(
                    name=param_name,
                    schema=schema,
                    context=self._extract_context(prompt, schema),
                    relevance=relevance
                ))
            else:
                # Prompt doesn't mention this parameter - use default
                resolved[param_name] = schema.default
                sources[param_name] = "default"

        return ParameterResolutionResult(
            resolved=resolved,
            unresolved=unresolved,
            resolution_sources=sources
        )

    def _extract_context(
        self,
        prompt: str,
        schema: ParameterSchema
    ) -> str:
        """Extract relevant context from prompt for this parameter.

        Uses semantic hints to find the most relevant phrase.
        """
        # Find phrases that match semantic hints
        prompt_lower = prompt.lower()
        for hint in schema.semantic_hints:
            if hint.lower() in prompt_lower:
                # Extract surrounding context (simple approach)
                idx = prompt_lower.find(hint.lower())
                start = max(0, idx - 20)
                end = min(len(prompt), idx + len(hint) + 20)
                return prompt[start:end].strip()

        # Fallback: return full prompt
        return prompt
```

**Tests:** `tests/unit/router/application/resolver/test_parameter_resolver.py`
- Test YAML modifier takes priority over learned
- Test learned mapping used when no YAML modifier
- Test unresolved when neither found but prompt relates to param
- Test default fallback when prompt doesn't relate
- Test context extraction with semantic hints

---

### TASK-055-4: Workflow Schema Enhancement
**Status:** ✅ Done

Add `parameters:` section to workflow YAML schema. **Note:** `modifiers:` section stays as-is for explicit mappings.

**File:** `server/router/application/workflows/custom/picnic_table.yaml`

```yaml
name: picnic_table
description: Creates a picnic table with benches

# EXISTING: Explicit modifiers (highest priority - used when prompt matches)
modifiers:
  "straight legs":
    leg_angle_left: 0
    leg_angle_right: 0
  "angled legs":
    leg_angle_left: 0.32
    leg_angle_right: -0.32

# NEW: Parameter schemas for interactive resolution
# Used when NO modifier matches and prompt relates to parameter
parameters:
  leg_angle_left:
    type: float
    range: [-1.57, 1.57]
    default: 0.32
    description: "rotation angle for left table legs"
    semantic_hints: ["angle", "rotation", "tilt", "lean", "straight", "vertical", "legs", "tilt"]
    group: leg_angles  # Grouped with leg_angle_right

  leg_angle_right:
    type: float
    range: [-1.57, 1.57]
    default: -0.32
    description: "rotation angle for right table legs"
    semantic_hints: ["angle", "rotation", "tilt", "lean"]
    group: leg_angles

steps:
  # ... existing steps ...
```

**Flow with both sections:**
```
Prompt: "table with straight legs"
→ ModifierExtractor finds "straight legs" in modifiers
→ Uses: leg_angle_left=0, leg_angle_right=0
→ Done! (no LLM interaction)

Prompt: "stół z prostymi nogami"
→ ModifierExtractor: no match in modifiers
→ ParameterStore.find_mapping(): no match (first time)
→ LaBSE detects "prostymi nogami" relates to leg_angles (via semantic_hints)
→ Ask LLM: "what value for leg_angle?"
→ LLM responds: 0
→ Store mapping for future
```

**Files to update:**
- `server/router/application/workflows/base.py` - Add `parameters` field to `WorkflowDefinition`
- `server/router/infrastructure/workflow_loader.py` - Parse `parameters:` section
- `server/router/application/workflows/registry.py` - Pass parameters to resolver

**Tests:** `tests/unit/router/application/workflows/test_workflow_parameters.py`
- Test YAML with both modifiers and parameters
- Test YAML with only modifiers (backward compatible)
- Test YAML with only parameters (new style)
- Test parameter schema parsing with all fields

---

### TASK-055-5: MCP Tool for Parameter Resolution
**Status:** ✅ Done

Create tool for LLM to provide parameter values:

**File:** `server/adapters/mcp/tools/router_tools.py`

```python
@mcp.tool()
def router_resolve_parameter(
    parameter_name: str,
    value: float,
    context: str,
    workflow_name: Optional[str] = None
) -> str:
    """
    Provide a parameter value for the current workflow.

    Called by LLM when router asks for parameter input.
    The value is stored for future semantic matching.

    Args:
        parameter_name: Name of the parameter (e.g., "leg_angle_left")
        value: Numeric value to use
        context: Original prompt context (e.g., "prostymi nogami")
        workflow_name: Optional workflow name (uses current if not specified)

    Returns:
        Confirmation message with stored mapping details.
    """
    router = get_router()
    router.store_parameter_mapping(
        context=context,
        parameter_name=parameter_name,
        value=value,
        workflow_name=workflow_name
    )
    return f"Stored: '{context}' → {parameter_name}={value}"
```

**Tests:** `tests/unit/adapters/mcp/tools/test_router_resolve_parameter.py`

---

### TASK-055-6: Router Integration
**Status:** ✅ Done

Integrate ParameterResolver into SupervisorRouter without changing existing return types.

**File:** `server/router/application/router.py`

**Key design:** Add NEW method `set_goal_interactive()` instead of modifying `set_current_goal()`. This preserves backward compatibility.

Changes:
1. Add `ParameterResolver` and `ParameterStore` initialization in `__init__`
2. Add `set_goal_interactive()` method for interactive resolution
3. Integrate with `EnsembleResult.modifiers` from TASK-053
4. Add `store_parameter_mapping()` method
5. Add configuration in `RouterConfig`:
   - `parameter_resolution_timeout: float = 30.0`
   - `parameter_relevance_threshold: float = 0.5`
   - `parameter_memory_threshold: float = 0.85`

```python
class SupervisorRouter:
    def __init__(self, config: RouterConfig, ...):
        # ... existing init ...

        # NEW: Parameter resolution (TASK-055)
        self._parameter_store = ParameterStore(
            classifier=self._intent_classifier,
            db_path=config.parameter_store_path or DEFAULT_PARAM_STORE_PATH
        )
        self._parameter_resolver = ParameterResolver(
            classifier=self._intent_classifier,
            store=self._parameter_store,
            relevance_threshold=config.parameter_relevance_threshold
        )

    def set_goal_interactive(self, goal: str) -> Dict[str, Any]:
        """Set goal with interactive parameter resolution.

        Returns dict with status:
        - {"status": "ready", "workflow": "...", "variables": {...}}
        - {"status": "needs_parameter_input", "workflow": "...", "questions": [...]}
        - {"status": "no_match"}
        """
        # Step 1: Get EnsembleResult (includes modifiers from YAML)
        ensemble_result = self._set_goal_ensemble(goal)

        if not ensemble_result or not ensemble_result.workflow_id:
            return {"status": "no_match"}

        workflow_name = ensemble_result.workflow_id
        definition = self._registry.get_definition(workflow_name)

        if not definition:
            return {"status": "no_match"}

        # Step 2: Get modifiers from EnsembleResult (YAML-based)
        yaml_modifiers = ensemble_result.modifiers or {}

        # Step 3: Resolve parameters (3-tier system)
        resolution = self._parameter_resolver.resolve(
            prompt=goal,
            workflow_name=workflow_name,
            parameters=definition.parameters or {},
            existing_modifiers=yaml_modifiers  # Pass YAML modifiers
        )

        # Step 4: Check if we need LLM input
        if resolution.needs_llm_input:
            # Store pending state for when LLM responds
            self._pending_resolution = {
                "workflow": workflow_name,
                "resolved": resolution.resolved,
                "unresolved": resolution.unresolved
            }
            return {
                "status": "needs_parameter_input",
                "workflow": workflow_name,
                "questions": [
                    {
                        "parameter": p.name,
                        "context": p.context,
                        "description": p.schema.description,
                        "range": list(p.schema.range) if p.schema.range else None,
                        "default": p.schema.default,
                        "type": p.schema.type,
                        "group": p.schema.group
                    }
                    for p in resolution.unresolved
                ]
            }

        # All resolved - continue with workflow
        self._pending_variables = resolution.resolved
        return {
            "status": "ready",
            "workflow": workflow_name,
            "variables": resolution.resolved,
            "sources": resolution.resolution_sources
        }

    def store_parameter_mapping(
        self,
        context: str,
        parameter_name: str,
        value: Any,
        workflow_name: Optional[str] = None
    ) -> str:
        """Store LLM-provided parameter value for future reuse."""
        wf_name = workflow_name or self._current_goal
        if not wf_name:
            return "Error: No active workflow"

        self._parameter_store.store_mapping(
            context=context,
            parameter_name=parameter_name,
            value=value,
            workflow_name=wf_name
        )

        return f"Stored: '{context}' → {parameter_name}={value} (workflow: {wf_name})"
```

**Config additions (`server/router/infrastructure/config.py`):**
```python
@dataclass
class RouterConfig:
    # ... existing fields ...

    # TASK-055: Parameter resolution
    parameter_store_path: Optional[str] = None  # Default: ~/.cache/blender-ai-mcp/params
    parameter_resolution_timeout: float = 30.0
    parameter_relevance_threshold: float = 0.5
    parameter_memory_threshold: float = 0.85
```

**Tests:** `tests/unit/router/application/test_router_parameter_resolution.py`
- Test `set_goal_interactive()` with YAML modifier match (no LLM needed)
- Test `set_goal_interactive()` with learned mapping match
- Test `set_goal_interactive()` returns `needs_parameter_input`
- Test `store_parameter_mapping()` saves to store
- Test integration with EnsembleResult.modifiers

---

### TASK-055-7: E2E Tests
**Status:** ✅ Done

End-to-end tests for the complete flow:

**File:** `tests/e2e/router/test_parameter_resolution_e2e.py`

```python
class TestParameterResolutionE2E:
    """E2E tests for interactive parameter resolution."""

    def test_yaml_modifier_takes_priority(self, router):
        """YAML modifier match should NOT trigger interactive resolution."""
        # "straight legs" is defined in picnic_table.yaml modifiers
        result = router.set_goal_interactive("table with straight legs")

        assert result["status"] == "ready"
        assert result["variables"]["leg_angle_left"] == 0
        assert result["sources"]["leg_angle_left"] == "yaml_modifier"

    def test_first_time_needs_llm_input(self, router):
        """First time with unknown phrase should ask LLM."""
        # "with straight legs" not in YAML modifiers, not learned yet
        result = router.set_goal_interactive("simple table with straight legs")

        assert result["status"] == "needs_parameter_input"
        assert len(result["questions"]) > 0
        assert result["questions"][0]["parameter"] == "leg_angle_left"
        assert result["questions"][0]["range"] == [-1.57, 1.57]

    def test_stored_mapping_reuse(self, router):
        """After LLM provides value, similar prompts auto-resolve."""
        # First: simulate LLM response
        router.store_parameter_mapping(
            context="with straight legs",
            parameter_name="leg_angle_left",
            value=0,
            workflow_name="picnic_table"
        )

        # Second: similar prompt should auto-resolve
        result = router.set_goal_interactive("table with straight legs")

        assert result["status"] == "ready"
        assert result["variables"]["leg_angle_left"] == 0
        assert result["sources"]["leg_angle_left"] == "learned"

    def test_multilingual_semantic_matching(self, router):
        """Polish stored mapping should match English query via LaBSE."""
        # Store Polish phrase
        router.store_parameter_mapping(
            context="proste nogi",
            parameter_name="leg_angle_left",
            value=0
        )

        # Query with different Polish variant - should find via LaBSE
        result = router.set_goal_interactive("stół z pionowymi nogami")

        # LaBSE should find "pionowymi nogami" similar to "proste nogi"
        assert result["status"] == "ready"
        assert result["sources"]["leg_angle_left"] == "learned"

    def test_grouped_parameters(self, router):
        """Plural form should apply to all grouped parameters."""
        # "proste nogi" (plural) should set both leg_angle_left AND leg_angle_right
        router.store_parameter_mapping(
            context="proste nogi",
            parameter_name="leg_angle_left",
            value=0
        )
        router.store_parameter_mapping(
            context="proste nogi",
            parameter_name="leg_angle_right",
            value=0
        )

        result = router.set_goal_interactive("table with straight legs")

        assert result["status"] == "ready"
        assert result["variables"]["leg_angle_left"] == 0
        assert result["variables"]["leg_angle_right"] == 0

    def test_value_out_of_range_rejected(self, router):
        """Value outside schema range should be rejected."""
        # Attempt to store value outside range [-1.57, 1.57]
        result = router.store_parameter_mapping(
            context="test",
            parameter_name="leg_angle_left",
            value=5.0,  # Outside range!
            workflow_name="picnic_table"
        )

        assert "Error" in result or "out of range" in result.lower()

    def test_default_when_not_mentioned(self, router):
        """Parameters not mentioned in prompt should use defaults."""
        # Prompt only mentions table, not legs at all
        result = router.set_goal_interactive("simple table")

        assert result["status"] == "ready"
        # Should use default values from schema
        assert result["variables"]["leg_angle_left"] == 0.32  # default
        assert result["sources"]["leg_angle_left"] == "default"

    def test_yaml_modifier_priority_over_learned(self, router):
        """YAML modifier should take priority over learned mapping."""
        # First: store a learned mapping
        router.store_parameter_mapping(
            context="straight legs",
            parameter_name="leg_angle_left",
            value=0.5  # Different from YAML modifier!
        )

        # Query with exact YAML modifier phrase
        result = router.set_goal_interactive("table with straight legs")

        # Should use YAML value (0), not learned value (0.5)
        assert result["status"] == "ready"
        assert result["variables"]["leg_angle_left"] == 0
        assert result["sources"]["leg_angle_left"] == "yaml_modifier"
```

**Additional test file:** `tests/e2e/router/test_parameter_store_e2e.py`
- Test LanceDB persistence across restarts
- Test concurrent access to parameter store
- Test cleanup of old/unused mappings

---

## Documentation Updates Required

After implementation, update these files:

| File | Updates |
|------|---------|
| `_docs/_ROUTER/README.md` | Add ParameterResolver component |
| `_docs/_ROUTER/ROUTER_ARCHITECTURE.md` | Add parameter resolution flow diagram |
| `_docs/_MCP_SERVER/README.md` | Add `router_resolve_parameter` tool |
| `_docs/AVAILABLE_TOOLS_SUMMARY.md` | Add new tool entry |
| `_docs/_CHANGELOG/XX-2025-12-XX-parameter-resolution.md` | Create changelog |
| `README.md` | Update Router Supervisor section |

---

## Technical Notes

### LanceDB Schema for Parameter Store

```python
PARAMETER_MAPPING_SCHEMA = {
    "context": str,           # Original prompt context
    "embedding": list,        # LaBSE 768-dim vector
    "parameter": str,         # Parameter name
    "value": float,           # Resolved value
    "workflow": str,          # Workflow name
    "created_at": str,        # ISO timestamp
    "usage_count": int,       # How many times used
}
```

### Thresholds

| Threshold | Value | Purpose |
|-----------|-------|---------|
| `relevance_threshold` | 0.50 | Min similarity for "prompt relates to parameter" |
| `memory_match_threshold` | 0.85 | Min similarity to reuse stored mapping (skip LLM) |

### Parameter Resolution Pipeline

```
STEP 0: Workflow Selection (router + EnsembleMatcher)
        → Returns EnsembleResult with workflow_id + modifiers (from YAML)

STEP 1: For each parameter in workflow.parameters:

    TIER 1 - YAML Modifier Check:
        if param_name in EnsembleResult.modifiers:
            → USE value from YAML modifier
            → DONE for this param (skip other tiers)

    TIER 2 - Learned Mapping Check:
        memory_score = cosine(labse(prompt), labse(stored_example))
        if memory_score >= 0.85:
            → USE stored value from ParameterStore
            → DONE for this param

    TIER 3 - LLM Resolution Check:
        relevance = cosine(labse(prompt), labse(parameter.description))
        if relevance >= 0.50:
            → Mark as UNRESOLVED (prompt relates to param, but no value)
        else:
            → USE default from schema (prompt doesn't mention param)

STEP 2: Return Result
    if any UNRESOLVED:
        → Return {"status": "needs_parameter_input", "questions": [...]}
        → Wait for LLM to call router_resolve_parameter()
    else:
        → Return {"status": "ready", "variables": {...}}

STEP 3: Store LLM Response (when router_resolve_parameter() called)
    → Save prompt fragment → parameter value in ParameterStore
    → Future similar prompts will auto-resolve via TIER 2
```

### Grouped Parameters (e.g., leg angles)

```python
# Rule: Plural form + no side indicator = apply to all grouped parameters.
if is_plural(phrase) and not has_side_indicator(phrase):
    # "proste nogi", "straight legs", "nogi bez pochylenia"
    apply_to_all_related_parameters(value)
    # leg_angle_left = 0, leg_angle_right = 0

# Side indicators: "left", "right", "lewa", "prawa", "lewy", "prawy"
if has_side_indicator(phrase, "left"):
    apply_to_parameter("leg_angle_left", value)
```

Store as grouped example:
```
"proste nogi" → {leg_angle_left: 0, leg_angle_right: 0}
```

### Fallback Behavior

If LLM doesn't respond to parameter question:
1. Wait for timeout (configurable, default 30s)
2. Use default value from schema
3. Log warning for debugging

---

## ⚠️ Implementation Notes

### Semantic Hints vs Modifiers Validation

**Important:** When implementing TASK-055-4 (Workflow Schema Enhancement), add validation to ensure `semantic_hints` in parameters don't overlap with existing `modifiers` keywords.

**Problem scenario:**
```yaml
modifiers:
  "straight legs":           # Explicit YAML modifier
    leg_angle_left: 0

parameters:
  leg_angle_left:
    semantic_hints: ["straight", "legs"]  # ⚠️ Overlaps with modifier!
```

**Required validation in `WorkflowLoader`:**
```python
def _validate_no_hint_modifier_overlap(self, definition: WorkflowDefinition) -> None:
    """Ensure semantic_hints don't overlap with modifier keywords."""
    if not definition.modifiers or not definition.parameters:
        return

    modifier_keywords = set()
    for keyword in definition.modifiers.keys():
        # Tokenize modifier keywords
        modifier_keywords.update(keyword.lower().split())

    for param_name, schema in definition.parameters.items():
        for hint in schema.semantic_hints:
            if hint.lower() in modifier_keywords:
                logger.warning(
                    f"Workflow '{definition.name}': semantic_hint '{hint}' "
                    f"overlaps with modifier keyword. YAML modifier will take priority."
                )
```

**Rationale:** This avoids ambiguity about which resolution path (Tier 1 YAML vs Tier 3 LLM) should handle a given phrase. YAML modifiers always win, so overlapping hints would never trigger LLM interaction anyway.

---

## Dependencies

- TASK-053 (Ensemble Matcher) - Completed ✅
  - Provides `EnsembleResult.modifiers` for YAML-based resolution
  - `ModifierExtractor` extracts modifiers from YAML
- LanceDB vector store - Already integrated ✅
  - Reuse existing `LanceVectorStore` infrastructure
- LaBSE model - Already loaded ✅
  - Reuse `WorkflowIntentClassifier` for embeddings
- `WorkflowDefinition` in `base.py` - Needs extension for `parameters` field

## Implementation Order

1. **TASK-055-0** - Domain interfaces (required for Clean Architecture)
2. **TASK-055-1** - Domain entities
3. **TASK-055-2** - ParameterStore (LanceDB)
4. **TASK-055-3** - ParameterResolver
5. **TASK-055-4** - Workflow YAML schema extension
6. **TASK-055-5** - MCP tool
7. **TASK-055-6** - Router integration
8. **TASK-055-7** - E2E tests

## Estimated Effort

- Sub-tasks: 8 (including TASK-055-0)
- Estimated LOC: ~700-900
- Complexity: Medium-High (new interaction pattern with LLM)

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `server/router/domain/interfaces/i_parameter_resolver.py` | CREATE | Abstract interfaces |
| `server/router/domain/entities/parameter.py` | CREATE | Domain entities |
| `server/router/application/resolver/parameter_store.py` | CREATE | LanceDB store |
| `server/router/application/resolver/parameter_resolver.py` | CREATE | 3-tier resolver |
| `server/router/application/workflows/base.py` | MODIFY | Add `parameters` field |
| `server/router/infrastructure/workflow_loader.py` | MODIFY | Parse `parameters:` |
| `server/router/infrastructure/config.py` | MODIFY | Add config fields |
| `server/router/application/router.py` | MODIFY | Add `set_goal_interactive()` |
| `server/adapters/mcp/areas/router.py` | MODIFY | Add `router_resolve_parameter` |
| `tests/unit/router/**` | CREATE | Unit tests |
| `tests/e2e/router/**` | CREATE | E2E tests |

---

## Bug Fixes and Improvements

### TASK-055-FIX-3: Context Truncation Bug Fix (2025-12-09)

**Problem**: ParameterStore truncated prompts to 60-char windows (30 chars before/after hint), losing critical semantic information like "X-shaped".

**Example**:
```python
# BEFORE FIX
prompt = "create a picnic table with X-shaped legs"
stored_context = "ed legs picnic table"  # Lost "X-shaped"!
search_similarity = 0.80 < threshold 0.85 → MISS ❌

# AFTER FIX
prompt = "create a picnic table with X-shaped legs"
stored_context = "create a picnic table with X-shaped legs"  # Full sentence!
search_similarity = 0.92 > threshold 0.85 → HIT ✅
```

**Solution**: Implemented hybrid 3-tier context extraction strategy:
- **TIER 3**: Full prompt for short inputs (≤500 chars) - O(1) complexity
- **TIER 1**: Smart sentence extraction using sentence boundaries - O(n) complexity
- **TIER 2**: Expanded window (100 chars before + hint + 100 chars after) - O(1) fallback

**Results**:
- Context length: 60 chars → 100-400 chars
- Similarity scores: ~0.80 → >0.85
- Search recall: Significant improvement for learned mappings
- All 20 unit tests passing ✅

**Files Modified**:
- `server/router/application/resolver/parameter_resolver.py` - New 3-tier extraction
- `tests/unit/router/application/resolver/test_parameter_resolver_context.py` - 20 unit tests

**Documentation**:
- Implementation: `_docs/_ROUTER/IMPLEMENTATION/35-parameter-resolver.md`
- Changelog: `_docs/_CHANGELOG/100-2025-12-09-parameter-context-extraction.md`

**See**: `TASK-055-FIX-3_ParameterStore_Context_Truncation.md` for detailed implementation plan and rationale.
