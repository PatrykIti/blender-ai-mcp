# 15. SupervisorRouter Core

**Task:** TASK-039-16
**Status:** Done
**Layer:** Application

---

## Overview

The SupervisorRouter is the main orchestrator of the Router Supervisor system. It processes LLM tool calls through an 8-step pipeline that intercepts, analyzes, corrects, and validates operations before execution.

---

## Interface

From `server/router/domain/interfaces/` (conceptual):

```python
class ISupervisorRouter(ABC):
    @abstractmethod
    def process_llm_tool_call(
        self,
        tool_name: str,
        params: Dict[str, Any],
        prompt: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Process an LLM tool call through the router pipeline."""
        pass

    @abstractmethod
    def route(self, prompt: str) -> List[str]:
        """Route a natural language prompt to tools (offline)."""
        pass
```

---

## Implementation

**File:** `server/router/application/router.py`

### Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      SupervisorRouter Pipeline                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. INTERCEPT ─────► Capture LLM tool call                          │
│         │            - Record in history                            │
│         │            - Extract prompt context                       │
│         ▼                                                            │
│  2. ANALYZE ───────► Read scene context                             │
│         │            - Query Blender via RPC                        │
│         │            - Cache results                                │
│         ▼                                                            │
│  3. DETECT ────────► Identify geometry patterns                     │
│         │            - tower_like, phone_like, etc.                 │
│         │            - Calculate confidence scores                  │
│         ▼                                                            │
│  4. CORRECT ───────► Fix params/mode/selection                      │
│         │            - Add mode switch if needed                    │
│         │            - Add selection if required                    │
│         │            - Clamp parameters to valid ranges             │
│         ▼                                                            │
│  5. OVERRIDE ──────► Check for better alternatives                  │
│         │            - Pattern-based tool replacement               │
│         │            - Context-aware substitution                   │
│         ▼                                                            │
│  6. EXPAND ────────► Transform to workflow if needed                │
│         │            - Single tool → multi-step workflow            │
│         │            - Parameter inheritance ($param syntax)        │
│         ▼                                                            │
│  7. FIREWALL ──────► Validate each tool                             │
│         │            - Block invalid operations                     │
│         │            - Auto-fix mode violations                     │
│         │            - Clamp parameter values                       │
│         ▼                                                            │
│  8. OUTPUT ────────► Return final tool list                         │
│                      - List of {"tool": ..., "params": ...}         │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Core Implementation

```python
class SupervisorRouter:
    """Main router orchestrator."""

    def __init__(
        self,
        config: Optional[RouterConfig] = None,
        rpc_client: Optional[Any] = None,
    ):
        self.config = config or RouterConfig()
        self._rpc_client = rpc_client

        # Initialize components
        self.interceptor = ToolInterceptor()
        self.analyzer = SceneContextAnalyzer(rpc_client=rpc_client)
        self.detector = GeometryPatternDetector()
        self.correction_engine = ToolCorrectionEngine(config=self.config)
        self.override_engine = ToolOverrideEngine(config=self.config)
        self.expansion_engine = WorkflowExpansionEngine(config=self.config)
        self.firewall = ErrorFirewall(config=self.config)
        self.classifier = IntentClassifier(config=self.config)
        self.logger = RouterLogger()

    def process_llm_tool_call(
        self,
        tool_name: str,
        params: Dict[str, Any],
        prompt: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Process an LLM tool call through the router pipeline."""
        # Step 1: Intercept
        intercepted = self.interceptor.intercept(tool_name, params, prompt)

        # Step 2: Analyze
        context = self._analyze_scene()

        # Step 3: Detect
        pattern = self._detect_pattern(context)

        # Step 4: Correct
        corrected, pre_steps = self._correct_tool_call(tool_name, params, context)

        # Step 5: Override
        override_result = self._check_override(tool_name, params, context, pattern)

        # Step 6: Expand
        expanded = self._expand_workflow(tool_name, params, context, pattern)

        # Step 7: Build sequence
        final_tools = self._build_tool_sequence(
            corrected, pre_steps, override_result, expanded
        )

        # Step 8: Firewall
        validated_tools = self._validate_tools(final_tools, context)

        return self._format_output(validated_tools)
```

### Tool Sequence Priority

```python
def _build_tool_sequence(
    self,
    corrected: CorrectedToolCall,
    pre_steps: List[CorrectedToolCall],
    override_tools: Optional[List[CorrectedToolCall]],
    expanded_tools: Optional[List[CorrectedToolCall]],
) -> List[CorrectedToolCall]:
    """Build final sequence with priority:
    1. Override takes highest priority
    2. Workflow expansion comes next
    3. Default: pre-steps + corrected call
    """
    if override_tools:
        return list(pre_steps) + list(override_tools)

    if expanded_tools:
        return list(pre_steps) + list(expanded_tools)

    return list(pre_steps) + [corrected]
```

### Context Simulation

The router simulates context changes after each tool to validate subsequent operations:

```python
def _simulate_context_change(
    self,
    context: SceneContext,
    tool: CorrectedToolCall,
) -> SceneContext:
    """Simulate context change after tool execution."""
    # Mode switch simulation
    if tool.tool_name == "system_set_mode":
        new_mode = tool.params.get("mode", context.mode)
        return SceneContext(mode=new_mode, ...)

    # Selection simulation
    if tool.tool_name == "mesh_select":
        action = tool.params.get("action")
        if action == "all":
            # Simulate full selection
            return SceneContext(topology=TopologyInfo(selected_verts=vertices, ...))
        elif action == "none":
            # Simulate no selection
            return SceneContext(topology=TopologyInfo(selected_verts=0, ...))

    return context
```

---

## Configuration

All configuration options are controlled via `RouterConfig`:

```python
RouterConfig:
    # Correction settings
    auto_mode_switch: bool = True        # Auto-switch Blender mode
    auto_selection: bool = True          # Auto-select geometry
    clamp_parameters: bool = True        # Clamp params to valid ranges

    # Override settings
    enable_overrides: bool = True        # Enable tool replacement
    enable_workflow_expansion: bool = True  # Enable workflow expansion

    # Firewall settings
    block_invalid_operations: bool = True   # Block invalid ops
    auto_fix_mode_violations: bool = True   # Auto-fix mode issues

    # Cache settings
    cache_scene_context: bool = True     # Cache scene analysis
    cache_ttl_seconds: float = 1.0       # Cache TTL
```

---

## Usage

### Basic Usage

```python
from server.router import SupervisorRouter, RouterConfig

# Create router
config = RouterConfig()
router = SupervisorRouter(config=config, rpc_client=rpc_client)

# Process tool call
result = router.process_llm_tool_call(
    tool_name="mesh_extrude_region",
    params={"depth": 0.5},
    prompt="extrude the top face",
)

# Result is list of corrected/expanded tools
for tool in result:
    execute_tool(tool["tool"], tool["params"])
```

### Batch Processing

```python
# Process multiple calls
result = router.process_batch([
    {"tool": "mesh_extrude_region", "params": {"depth": 0.5}},
    {"tool": "mesh_bevel", "params": {"width": 0.1}},
])
```

### Intent Routing

```python
# Load tool metadata for classification
metadata = metadata_loader.load_all()
router.load_tool_metadata(metadata)

# Route natural language prompt
tools = router.route("extrude the top face")
# Returns: ["mesh_extrude_region", "mesh_inset", ...]
```

### State Management

```python
# Get last analyzed context
context = router.get_last_context()

# Get last detected pattern
pattern = router.get_last_pattern()

# Invalidate cache
router.invalidate_cache()

# Get processing stats
stats = router.get_stats()
# {"total_calls": 10, "corrections_applied": 5, ...}

# Reset stats
router.reset_stats()
```

---

## Example Scenarios

### Scenario 1: Mesh Tool in Object Mode

**Input:**
```python
router.process_llm_tool_call("mesh_extrude_region", {"depth": 0.5})
```

**Context:** OBJECT mode, no selection

**Output:**
```python
[
    {"tool": "system_set_mode", "params": {"mode": "EDIT"}},
    {"tool": "mesh_select", "params": {"action": "all"}},
    {"tool": "mesh_extrude_region", "params": {"depth": 0.5}},
]
```

### Scenario 2: Phone Pattern Override

**Input:**
```python
router.process_llm_tool_call("mesh_extrude_region", {"depth": -0.02})
```

**Context:** EDIT mode, phone_like pattern detected

**Output:**
```python
[
    {"tool": "mesh_inset", "params": {"thickness": 0.03}},
    {"tool": "mesh_extrude_region", "params": {"depth": -0.02}},
]
```

### Scenario 3: Workflow Expansion

**Input:**
```python
router.process_llm_tool_call("some_tool", {})
```

**Context:** phone_like pattern with suggested workflow

**Output:**
```python
[
    {"tool": "modeling_create_primitive", "params": {"type": "CUBE"}},
    {"tool": "modeling_transform_object", "params": {"scale": [0.4, 0.8, 0.05]}},
    {"tool": "system_set_mode", "params": {"mode": "EDIT"}},
    # ... 7 more steps
]
```

---

## Tests

**File:** `tests/unit/router/application/test_supervisor_router.py`

### Test Categories

1. **Initialization Tests** - Component setup, config
2. **Basic Pipeline Tests** - Passthrough, corrections
3. **Override Tests** - Pattern-based replacement
4. **Workflow Expansion Tests** - Multi-step expansion
5. **Firewall Tests** - Validation, blocking
6. **Batch Processing Tests** - Multiple calls
7. **Route Method Tests** - Intent classification
8. **Context Simulation Tests** - State tracking
9. **State Management Tests** - Cache, stats
10. **Configuration Tests** - Config updates
11. **Integration Tests** - Full pipeline

### Running Tests

```bash
PYTHONPATH=. poetry run pytest tests/unit/router/application/test_supervisor_router.py -v
```

---

## See Also

- [06-tool-interceptor.md](./06-tool-interceptor.md) - Tool interception
- [07-scene-context-analyzer.md](./07-scene-context-analyzer.md) - Scene analysis
- [08-geometry-pattern-detector.md](./08-geometry-pattern-detector.md) - Pattern detection
- [10-tool-correction-engine.md](./10-tool-correction-engine.md) - Tool correction
- [11-tool-override-engine.md](./11-tool-override-engine.md) - Tool override
- [12-workflow-expansion-engine.md](./12-workflow-expansion-engine.md) - Workflow expansion
- [13-error-firewall.md](./13-error-firewall.md) - Error firewall
- [14-intent-classifier.md](./14-intent-classifier.md) - Intent classification
