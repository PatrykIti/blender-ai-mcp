# TASK-055: Interactive Parameter Resolution via LLM Feedback

## Status: 🚨 To Do
## Priority: 🔴 High
## Created: 2025-12-08

---

## Overview

Enable MCP server to **ask the connected LLM** for parameter values when it doesn't know them, instead of requiring all parameter mappings in YAML workflow files. The system learns from LLM responses and stores mappings for future use.

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

Router asks LLM for unknown parameter values and stores the answers in a **semantic knowledge store** (LanceDB with LaBSE embeddings).

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

### TASK-055-1: Domain Entities
**Status:** ⬜ To Do

Create domain entities for parameter resolution:

**File:** `server/router/domain/entities/parameter.py`

```python
@dataclass
class ParameterSchema:
    name: str
    type: str  # "float", "int", "bool", "string"
    range: Optional[Tuple[float, float]] = None
    default: Any = None
    description: str = ""
    semantic_hints: List[str] = field(default_factory=list)

@dataclass
class UnresolvedParameter:
    name: str
    schema: ParameterSchema
    context: str  # Extracted from prompt
    relevance: float  # LaBSE similarity score

@dataclass
class ParameterResolutionResult:
    resolved: Dict[str, Any]  # Known values
    unresolved: List[UnresolvedParameter]  # Need LLM input
```

**Tests:** `tests/unit/router/domain/entities/test_parameter.py`

---

### TASK-055-2: Parameter Store (LanceDB Persistence)
**Status:** ⬜ To Do

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
**Status:** ⬜ To Do

Create resolver that uses LaBSE to match prompts to parameters:

**File:** `server/router/application/resolver/parameter_resolver.py`

```python
class ParameterResolver:
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
        parameters: Dict[str, ParameterSchema]
    ) -> ParameterResolutionResult:
        """Resolve parameters from prompt using stored mappings and LaBSE."""
        resolved = {}
        unresolved = []

        for param_name, schema in parameters.items():
            # 1. Check stored mappings first
            stored = self._store.find_mapping(prompt, param_name)
            if stored:
                resolved[param_name] = stored.value
                continue

            # 2. Check if prompt relates to this parameter
            relevance = self._classifier.similarity(
                prompt,
                schema.description
            )

            if relevance > self._relevance_threshold:
                # Prompt mentions this parameter but we don't know value
                unresolved.append(UnresolvedParameter(
                    name=param_name,
                    schema=schema,
                    context=self._extract_context(prompt, schema),
                    relevance=relevance
                ))
            else:
                # Prompt doesn't mention this - use default
                resolved[param_name] = schema.default

        return ParameterResolutionResult(resolved, unresolved)
```

**Tests:** `tests/unit/router/application/resolver/test_parameter_resolver.py`
- Test resolution with stored mapping
- Test resolution with unresolved parameters
- Test default fallback
- Test relevance threshold

---

### TASK-055-4: Workflow Schema Enhancement
**Status:** ⬜ To Do

Add `parameters:` section to workflow YAML schema:

**File:** `server/router/application/workflows/custom/picnic_table.yaml`

```yaml
# NEW: Parameter definitions with descriptions for LaBSE matching
parameters:
  leg_angle_left:
    type: float
    range: [-1.57, 1.57]
    default: 0.32
    description: "rotation angle for left table legs"
    semantic_hints: ["angle", "rotation", "tilt", "lean", "straight", "vertical"]

  leg_angle_right:
    type: float
    range: [-1.57, 1.57]
    default: -0.32
    description: "rotation angle for right table legs"
    semantic_hints: ["angle", "rotation", "tilt", "lean"]

# REMOVED: modifiers section (no longer needed!)
# modifiers:
#   "straight legs": ...
```

**Files to update:**
- `server/router/domain/entities/workflow.py` - Add `parameters` field to `WorkflowDefinition`
- `server/router/application/workflows/registry.py` - Parse parameters section

**Tests:** `tests/unit/router/application/workflows/test_workflow_parameters.py`

---

### TASK-055-5: MCP Tool for Parameter Resolution
**Status:** ⬜ To Do

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
**Status:** ⬜ To Do

Integrate ParameterResolver into SupervisorRouter:

**File:** `server/router/application/router.py`

Changes:
1. Add `ParameterResolver` and `ParameterStore` initialization
2. Modify `_build_variables()` to use resolver
3. Return `needs_parameter_input` status when unresolved parameters exist
4. Add `store_parameter_mapping()` method

```python
def set_current_goal(self, goal: str) -> Dict[str, Any]:
    # ... existing workflow matching ...

    # NEW: Resolve parameters
    resolution = self._parameter_resolver.resolve(
        prompt=goal,
        workflow_name=matched_workflow,
        parameters=definition.parameters
    )

    if resolution.unresolved:
        return {
            "status": "needs_parameter_input",
            "workflow": matched_workflow,
            "questions": [
                {
                    "parameter": p.name,
                    "context": p.context,
                    "description": p.schema.description,
                    "range": p.schema.range,
                    "default": p.schema.default
                }
                for p in resolution.unresolved
            ]
        }

    # Continue with resolved values...
    self._pending_variables = resolution.resolved
    return {"status": "ready", "workflow": matched_workflow}
```

**Tests:** `tests/unit/router/application/test_router_parameter_resolution.py`

---

### TASK-055-7: E2E Tests
**Status:** ⬜ To Do

End-to-end tests for the complete flow:

**File:** `tests/e2e/router/test_parameter_resolution_e2e.py`

```python
def test_first_time_parameter_resolution():
    """First time asking about 'prostymi nogami' should return question."""
    router = get_router()
    result = router.set_current_goal("prosty stół z prostymi nogami")

    assert result["status"] == "needs_parameter_input"
    assert result["questions"][0]["parameter"] == "leg_angle_left"

def test_stored_mapping_reuse():
    """After storing, similar prompts should auto-resolve."""
    router = get_router()

    # First: provide value
    router.store_parameter_mapping(
        context="prostymi nogami",
        parameter_name="leg_angle_left",
        value=0
    )

    # Second: similar prompt should auto-resolve
    result = router.set_current_goal("stół z prostymi nogami")
    assert result["status"] == "ready"

def test_multilingual_semantic_matching():
    """Polish stored mapping should match English prompt."""
    router = get_router()

    # Store Polish
    router.store_parameter_mapping(
        context="proste nogi",
        parameter_name="leg_angle_left",
        value=0
    )

    # Query English - should find via LaBSE
    result = router.set_current_goal("table with straight legs")
    assert result["status"] == "ready"
```

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
STEP 0: Workflow Selection (router + matchers)

STEP 1: For each parameter in workflow:
    relevance = cosine(labse(prompt), labse(parameter_semantic_label))
    if relevance < 0.50 → SKIP (not related)

STEP 2: Memory Check
    memory_score = cosine(labse(prompt), labse(stored_example))
    if memory_score >= 0.85 → USE stored value, SKIP LLM

STEP 3: Ask LLM (if relevance >= 0.50 AND memory < 0.85)
    → Return ALL unresolved parameters in SINGLE tool call
    → LLM resolves all at once with full context

STEP 4: Store Example
    → Save prompt → parameter values mapping
    → Future similar prompts will auto-resolve
```

### Grouped Parameters (e.g., leg angles)

```python
# Rule: Plural form + no side indicator = apply to both
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

## Dependencies

- TASK-053 (Ensemble Matcher) - Completed ✅
- LanceDB vector store - Already integrated ✅
- LaBSE model - Already loaded ✅

## Estimated Effort

- Sub-tasks: 7
- Estimated LOC: ~600-800
- Complexity: Medium-High (new interaction pattern with LLM)
