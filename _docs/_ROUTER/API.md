# Router API Reference

Complete API reference for Router Supervisor components.

---

## SupervisorRouter

Main orchestrator that processes LLM tool calls through the router pipeline.

### Import

```python
from server.router.application.router import SupervisorRouter
from server.router.infrastructure.config import RouterConfig
```

### Constructor

```python
SupervisorRouter(
    config: Optional[RouterConfig] = None,
    rpc_client: Optional[Any] = None,
    classifier: Optional[IntentClassifier] = None,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `config` | `RouterConfig` | `RouterConfig()` | Router configuration |
| `rpc_client` | `Any` | `None` | RPC client for Blender communication |
| `classifier` | `IntentClassifier` | `None` | Shared classifier instance (for sharing LaBSE model) |

### Methods

#### process_llm_tool_call

Main entry point for processing tool calls from the LLM.

```python
def process_llm_tool_call(
    self,
    tool_name: str,
    params: Dict[str, Any],
    prompt: Optional[str] = None,
) -> List[Dict[str, Any]]
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `tool_name` | `str` | Name of the tool called by LLM |
| `params` | `Dict[str, Any]` | Parameters passed to the tool |
| `prompt` | `str` | Original user prompt (optional) |

**Returns:** List of corrected/expanded tool calls with `tool` and `params` keys.

**Example:**
```python
router = SupervisorRouter(config=config, rpc_client=rpc_client)

tools = router.process_llm_tool_call(
    tool_name="mesh_extrude_region",
    params={"depth": 0.5},
    prompt="extrude the top face"
)

# Returns:
# [
#     {"tool": "system_set_mode", "params": {"mode": "EDIT"}},
#     {"tool": "mesh_select", "params": {"action": "all"}},
#     {"tool": "mesh_extrude_region", "params": {"depth": 0.5}}
# ]
```

---

#### route

Route a natural language prompt to tools (offline intent classification).

```python
def route(self, prompt: str) -> List[str]
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `prompt` | `str` | Natural language prompt |

**Returns:** List of tool names that match the intent.

**Example:**
```python
tools = router.route("bevel the edges")
# Returns: ["mesh_bevel", "mesh_edge_bevel", ...]
```

---

#### process_batch

Process multiple tool calls at once.

```python
def process_batch(
    self,
    tool_calls: List[Dict[str, Any]],
    prompt: Optional[str] = None,
) -> List[Dict[str, Any]]
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `tool_calls` | `List[Dict]` | List of tool calls with `tool` and `params` |
| `prompt` | `str` | Original user prompt (optional) |

**Returns:** List of corrected/expanded tool calls.

---

#### set_rpc_client

Set the RPC client after initialization.

```python
def set_rpc_client(self, rpc_client: Any) -> None
```

---

#### invalidate_cache

Invalidate scene context cache.

```python
def invalidate_cache(self) -> None
```

---

#### get_stats

Get processing statistics.

```python
def get_stats(self) -> Dict[str, Any]
```

**Returns:**
```python
{
    "total_calls": 100,
    "corrections_applied": 45,
    "overrides_triggered": 12,
    "workflows_expanded": 8,
    "blocked_calls": 3,
}
```

---

#### reset_stats

Reset processing statistics.

```python
def reset_stats(self) -> None
```

---

#### get_last_context

Get last analyzed scene context.

```python
def get_last_context(self) -> Optional[SceneContext]
```

---

#### get_last_pattern

Get last detected geometry pattern.

```python
def get_last_pattern(self) -> Optional[DetectedPattern]
```

---

#### load_tool_metadata

Load tool metadata for intent classification.

```python
def load_tool_metadata(self, metadata: Dict[str, Any]) -> None
```

---

#### is_ready

Check if router is ready for processing.

```python
def is_ready(self) -> bool
```

**Returns:** `True` if RPC client is set.

---

#### get_component_status

Get status of all components.

```python
def get_component_status(self) -> Dict[str, bool]
```

**Returns:**
```python
{
    "interceptor": True,
    "analyzer": True,      # True if RPC client set
    "detector": True,
    "correction_engine": True,
    "override_engine": True,
    "expansion_engine": True,
    "firewall": True,
    "classifier": True,    # True if embeddings loaded
}
```

---

#### get_config / update_config

Get or update configuration.

```python
def get_config(self) -> RouterConfig
def update_config(self, **kwargs: Any) -> None
```

---

## IntentClassifier

Classifies user prompts to tool names using LaBSE embeddings.

### Import

```python
from server.router.application.classifier.intent_classifier import IntentClassifier
```

### Constructor

```python
IntentClassifier(
    config: Optional[RouterConfig] = None,
    cache_dir: Optional[Path] = None,
    model_name: str = "sentence-transformers/LaBSE",
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `config` | `RouterConfig` | `RouterConfig()` | Router configuration |
| `cache_dir` | `Path` | `None` | Directory for embedding cache |
| `model_name` | `str` | `"sentence-transformers/LaBSE"` | Model name |

### Methods

#### predict

Predict the best matching tool for a prompt.

```python
def predict(self, prompt: str) -> Tuple[str, float]
```

**Returns:** Tuple of `(tool_name, confidence_score)`.

**Example:**
```python
classifier = IntentClassifier()
classifier.load_tool_embeddings(metadata)

tool, confidence = classifier.predict("bevel the edges")
# Returns: ("mesh_bevel", 0.85)
```

---

#### predict_top_k

Predict top K matching tools.

```python
def predict_top_k(self, prompt: str, k: int = 5) -> List[Tuple[str, float]]
```

**Returns:** List of `(tool_name, confidence_score)` tuples.

**Example:**
```python
results = classifier.predict_top_k("bevel the edges", k=3)
# Returns: [("mesh_bevel", 0.85), ("mesh_chamfer", 0.72), ("mesh_smooth", 0.45)]
```

---

#### load_tool_embeddings

Load and cache tool embeddings from metadata.

```python
def load_tool_embeddings(self, metadata: Dict[str, Any]) -> None
```

**Example:**
```python
metadata = {
    "mesh_bevel": {
        "keywords": ["bevel", "round", "chamfer"],
        "sample_prompts": ["bevel the edges", "round the corners"],
    },
    # ...
}
classifier.load_tool_embeddings(metadata)
```

---

#### is_loaded

Check if embeddings are loaded.

```python
def is_loaded(self) -> bool
```

---

#### get_embedding

Get embedding for a text.

```python
def get_embedding(self, text: str) -> Optional[np.ndarray]
```

---

#### similarity

Calculate similarity between two texts.

```python
def similarity(self, text1: str, text2: str) -> float
```

**Returns:** Similarity score (0.0 to 1.0).

---

#### get_model_info

Get information about the loaded model.

```python
def get_model_info(self) -> Dict[str, Any]
```

**Returns:**
```python
{
    "model_name": "sentence-transformers/LaBSE",
    "embeddings_available": True,
    "model_loaded": True,
    "num_tools": 45,
    "is_loaded": True,
    "using_fallback": False,
    "cache_size_bytes": 1024000,
}
```

---

#### clear_cache

Clear the embedding cache.

```python
def clear_cache(self) -> bool
```

---

## SceneContextAnalyzer

Analyzes Blender scene state for router decision making.

### Import

```python
from server.router.application.analyzers.scene_context_analyzer import SceneContextAnalyzer
```

### Constructor

```python
SceneContextAnalyzer(
    rpc_client: Optional[Any] = None,
    cache_ttl: float = 1.0,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `rpc_client` | `Any` | `None` | RPC client for Blender |
| `cache_ttl` | `float` | `1.0` | Cache time-to-live (seconds) |

### Methods

#### analyze

Analyze current scene context.

```python
def analyze(self, object_name: Optional[str] = None) -> SceneContext
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `object_name` | `str` | Specific object to focus on (uses active if None) |

**Returns:** `SceneContext` with current scene state.

---

#### get_cached

Get cached scene context if still valid.

```python
def get_cached(self) -> Optional[SceneContext]
```

---

#### invalidate_cache

Invalidate the scene context cache.

```python
def invalidate_cache(self) -> None
```

---

#### get_mode

Get current Blender mode.

```python
def get_mode(self) -> str
```

**Returns:** Mode string (`"OBJECT"`, `"EDIT"`, `"SCULPT"`, etc.).

---

#### has_selection

Check if anything is selected.

```python
def has_selection(self) -> bool
```

---

#### analyze_from_data

Build SceneContext from provided data (for testing).

```python
def analyze_from_data(self, data: Dict[str, Any]) -> SceneContext
```

---

## GeometryPatternDetector

Detects geometry patterns in objects.

### Import

```python
from server.router.application.analyzers.geometry_pattern_detector import GeometryPatternDetector
```

### Constructor

```python
GeometryPatternDetector(default_threshold: float = 0.5)
```

### Methods

#### detect

Detect all patterns in the given scene context.

```python
def detect(self, context: SceneContext) -> PatternMatchResult
```

**Returns:** `PatternMatchResult` with all detected patterns.

---

#### detect_pattern

Check for a specific pattern type.

```python
def detect_pattern(
    self,
    context: SceneContext,
    pattern_type: PatternType,
) -> DetectedPattern
```

---

#### get_best_match

Get the best matching pattern above threshold.

```python
def get_best_match(
    self,
    context: SceneContext,
    threshold: float = 0.5,
) -> Optional[DetectedPattern]
```

---

#### get_supported_patterns

Get list of patterns this detector can identify.

```python
def get_supported_patterns(self) -> List[PatternType]
```

**Returns:** List of supported `PatternType` values.

---

## ErrorFirewall

Validates tool calls and blocks/modifies invalid operations.

### Import

```python
from server.router.application.engines.error_firewall import ErrorFirewall
```

### Methods

#### validate

Validate a tool call against firewall rules.

```python
def validate(
    self,
    tool_call: CorrectedToolCall,
    context: SceneContext,
) -> FirewallResult
```

**Returns:** `FirewallResult` with action (ALLOW, BLOCK, AUTO_FIX, MODIFY).

---

#### register_rule

Register a new firewall rule.

```python
def register_rule(
    self,
    rule_name: str,
    tool_pattern: str,
    condition: str,
    action: str,
    fix_description: str = "",
) -> None
```

---

## Data Classes

### SceneContext

```python
@dataclass
class SceneContext:
    mode: str                              # Current mode (OBJECT, EDIT, etc.)
    active_object: Optional[str]           # Active object name
    selected_objects: List[str]            # Selected object names
    objects: List[ObjectInfo]              # All objects info
    topology: Optional[TopologyInfo]       # Mesh topology (Edit mode)
    proportions: Optional[ProportionInfo]  # Object proportions
    materials: List[str]                   # Material names
    modifiers: List[str]                   # Modifier names
    timestamp: datetime                    # Analysis timestamp

    @property
    def has_selection(self) -> bool: ...
    @property
    def is_edit_mode(self) -> bool: ...
    @property
    def is_object_mode(self) -> bool: ...
    @classmethod
    def empty(cls) -> "SceneContext": ...
```

---

### DetectedPattern

```python
@dataclass
class DetectedPattern:
    pattern_type: PatternType              # Pattern type enum
    confidence: float                      # Confidence (0.0 - 1.0)
    suggested_workflow: Optional[str]      # Suggested workflow name
    metadata: Dict[str, Any]               # Pattern-specific data
    detection_rules: List[str]             # Rules that triggered

    @property
    def name(self) -> str: ...
    @property
    def is_confident(self) -> bool: ...    # confidence > 0.7
```

---

### CorrectedToolCall

```python
@dataclass
class CorrectedToolCall:
    tool_name: str                         # Tool name
    params: Dict[str, Any]                 # Parameters
    corrections_applied: List[str]         # Applied corrections
    original_tool_name: Optional[str]      # Original tool (if modified)
    original_params: Optional[Dict]        # Original params (if modified)
    is_injected: bool                      # True if auto-added by router
```

---

### FirewallResult

```python
@dataclass
class FirewallResult:
    action: FirewallAction                 # ALLOW, BLOCK, AUTO_FIX, MODIFY
    message: str                           # Description
    modified_call: Optional[Dict]          # Modified tool call
    pre_steps: List[Dict]                  # Pre-execution steps
    violations: List[str]                  # Violation messages
```

---

## Enums

### PatternType

```python
class PatternType(Enum):
    TOWER_LIKE = "tower_like"
    PHONE_LIKE = "phone_like"
    TABLE_LIKE = "table_like"
    PILLAR_LIKE = "pillar_like"
    WHEEL_LIKE = "wheel_like"
    SCREEN_AREA = "screen_area"
    BOX_LIKE = "box_like"
    SPHERE_LIKE = "sphere_like"
    CYLINDER_LIKE = "cylinder_like"
    UNKNOWN = "unknown"
```

### FirewallAction

```python
class FirewallAction(Enum):
    ALLOW = "allow"
    BLOCK = "block"
    AUTO_FIX = "auto_fix"
    MODIFY = "modify"
    WARN = "warn"
```

---

## See Also

- [QUICK_START.md](./QUICK_START.md) - Getting started
- [CONFIGURATION.md](./CONFIGURATION.md) - Configuration options
- [PATTERNS.md](./PATTERNS.md) - Pattern detection reference
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Common issues
