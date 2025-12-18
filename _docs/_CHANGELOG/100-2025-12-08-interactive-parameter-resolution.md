# 100 - Interactive Parameter Resolution (TASK-055)

**Date:** 2025-12-08

## Summary

Implemented three-tier interactive parameter resolution system that enables the Router to learn parameter values from LLM interactions and reuse them via semantic similarity matching (LaBSE).

## Problem Solved

Previously, workflow YAML files required explicit modifier mappings for every language variant:

```yaml
modifiers:
  "straight legs":
    leg_angle_left: 0
  "proste nogi":      # Polish variant needed
    leg_angle_left: 0
  "prostymi nogami":  # Another Polish variant needed
    leg_angle_left: 0
```

This was not scalable - every language variant had to be manually defined.

## Solution

Three-tier parameter resolution (in order):

1. **Tier 1: YAML Modifiers** - Explicit mappings from workflow definition
2. **Tier 2: Learned Mappings** - Stored values from previous LLM interactions (via LaBSE semantic similarity)
3. **Tier 3: LLM Interactive** - Mark as unresolved for LLM to provide value, then store for future reuse

## Changes

### New Files Created

| File | Description |
|------|-------------|
| `server/router/domain/entities/parameter.py` | Domain entities: ParameterSchema, StoredMapping, UnresolvedParameter, ParameterResolutionResult |
| `server/router/domain/interfaces/i_parameter_resolver.py` | Abstract interfaces: IParameterStore, IParameterResolver |
| `server/router/application/resolver/__init__.py` | Resolver module initialization |
| `server/router/application/resolver/parameter_store.py` | LanceDB-based store for learned parameter mappings |
| `server/router/application/resolver/parameter_resolver.py` | Three-tier parameter resolver implementation |
| `tests/unit/router/domain/entities/test_parameter.py` | Unit tests for domain entities |
| `tests/unit/router/application/resolver/test_parameter_store.py` | Unit tests for ParameterStore |
| `tests/unit/router/application/resolver/test_parameter_resolver.py` | Unit tests for ParameterResolver |
| `tests/e2e/router/test_parameter_resolution.py` | E2E tests for complete flow |

### Files Modified

| File | Changes |
|------|---------|
| `server/router/domain/interfaces/i_vector_store.py` | Added `VectorNamespace.PARAMETERS` for parameter storage |
| `server/adapters/mcp/areas/router.py` | Added new MCP tools: `router_store_parameter`, `router_list_parameters`, `router_delete_parameter`, `router_set_goal_interactive` |
| `server/router/application/router_tool_handler.py` | Added handler methods for parameter tools |
| `server/infrastructure/di.py` | Added DI configuration for ParameterStore and ParameterResolver |

### New MCP Tools

| Tool | Description |
|------|-------------|
| `router_store_parameter` | Store LLM-resolved parameter value for future semantic reuse |
| `router_list_parameters` | List stored parameter mappings (optionally filtered by workflow) |
| `router_delete_parameter` | Delete a stored parameter mapping |
| `router_set_goal_interactive` | Set goal with interactive parameter resolution (shows resolved/unresolved params) |

## Technical Details

### ParameterSchema

Defines workflow parameter with semantic hints:

```python
@dataclass
class ParameterSchema:
    name: str
    type: str  # "float", "int", "bool", "string"
    range: Optional[Tuple[float, float]] = None
    default: Any = None
    description: str = ""
    semantic_hints: List[str] = field(default_factory=list)
    group: Optional[str] = None
```

### Thresholds

| Threshold | Value | Purpose |
|-----------|-------|---------|
| `relevance_threshold` | 0.50 | Min similarity for "prompt relates to parameter" |
| `memory_threshold` | 0.85 | Min similarity to reuse stored mapping |

### LanceDB Integration

Parameter mappings are stored in LanceDB with `VectorNamespace.PARAMETERS`:
- Context string (e.g., "straight legs")
- LaBSE embedding (768 dimensions)
- Parameter name
- Value
- Workflow name
- Usage count and timestamps

## Testing

| Test Type | Count | File |
|-----------|-------|------|
| Unit Tests | 18 | `tests/unit/router/` |
| E2E Tests | 11 | `tests/e2e/router/test_parameter_resolution.py` |

All 29 tests pass.

## Example Usage

```python
# First time - unknown phrase triggers LLM interaction
result = router.set_goal_interactive("stół z prostymi nogami")
# Returns: needs_parameter_input with questions

# LLM provides value
router.store_parameter_mapping(
    context="prostymi nogami",
    parameter_name="leg_angle_left",
    value=0.0,
    workflow_name="picnic_table"
)

# Next time - semantic match auto-resolves
result = router.set_goal_interactive("stół z pionowymi nogami")
# Returns: ready (learned mapping found via LaBSE similarity)
```

## Related Tasks

- TASK-053: Ensemble Matcher System (provides modifiers from YAML)
- TASK-047: LanceDB Vector Store (persistence layer)
- TASK-046: Router Semantic Generalization (LaBSE embeddings)
