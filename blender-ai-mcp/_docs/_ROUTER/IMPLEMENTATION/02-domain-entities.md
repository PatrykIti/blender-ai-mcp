# 02 - Domain Entities

**Task:** TASK-039-2
**Status:** ✅ Done
**Layer:** Domain

---

## Overview

Domain entities are pure data classes with no external dependencies. They represent the core concepts used throughout the router pipeline.

---

## Entities

### Tool Call Entities (`tool_call.py`)

#### InterceptedToolCall

Represents a tool call intercepted from the LLM.

```python
@dataclass
class InterceptedToolCall:
    tool_name: str                    # Name of the tool
    params: Dict[str, Any]            # Parameters passed
    timestamp: datetime               # When intercepted
    source: str = "llm"               # Origin ("llm" or "router")
    original_prompt: Optional[str]    # User prompt (if available)
    session_id: Optional[str]         # Session identifier
```

#### CorrectedToolCall

Represents a tool call after router corrections.

```python
@dataclass
class CorrectedToolCall:
    tool_name: str                    # Name (may differ from original)
    params: Dict[str, Any]            # Corrected parameters
    corrections_applied: List[str]    # List of corrections made
    original_tool_name: Optional[str] # Original name before override
    original_params: Optional[Dict]   # Original params before correction
    is_injected: bool = False         # True if router added this call
```

#### ToolCallSequence

Represents a sequence of tool calls (when one call expands to many).

```python
@dataclass
class ToolCallSequence:
    calls: List[CorrectedToolCall]           # Calls to execute in order
    original_call: Optional[InterceptedToolCall]
    expansion_reason: Optional[str]
```

---

### Scene Context Entities (`scene_context.py`)

#### ObjectInfo

Information about a single Blender object.

```python
@dataclass
class ObjectInfo:
    name: str
    type: str                         # MESH, CURVE, etc.
    location: List[float]             # [x, y, z]
    dimensions: List[float]           # [x, y, z]
    selected: bool
    active: bool
```

#### TopologyInfo

Mesh topology information.

```python
@dataclass
class TopologyInfo:
    vertices: int
    edges: int
    faces: int
    triangles: int
    selected_verts: int               # In edit mode
    selected_edges: int
    selected_faces: int

    @property
    def has_selection(self) -> bool   # Any geometry selected?
    @property
    def total_selected(self) -> int   # Total selected elements
```

#### ProportionInfo

Calculated proportions of an object.

```python
@dataclass
class ProportionInfo:
    aspect_xy: float                  # Width / Height
    aspect_xz: float                  # Width / Depth
    aspect_yz: float                  # Height / Depth
    is_flat: bool                     # z < min(x, y) * 0.2
    is_tall: bool                     # z > max(x, y) * 2
    is_wide: bool                     # x > max(y, z) * 2
    is_cubic: bool                    # max/min < 1.5
    dominant_axis: str                # "x", "y", or "z"
    volume: float
    surface_area: float
```

#### SceneContext

Complete scene context for router decision making.

```python
@dataclass
class SceneContext:
    mode: str                         # OBJECT, EDIT, SCULPT, etc.
    active_object: Optional[str]
    selected_objects: List[str]
    objects: List[ObjectInfo]
    topology: Optional[TopologyInfo]
    proportions: Optional[ProportionInfo]
    materials: List[str]
    modifiers: List[str]
    timestamp: datetime

    @property
    def has_selection(self) -> bool
    @property
    def is_edit_mode(self) -> bool
    @property
    def is_object_mode(self) -> bool
```

---

### Pattern Entities (`pattern.py`)

#### PatternType (Enum)

Known geometry pattern types.

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

#### DetectedPattern

Represents a detected geometry pattern.

```python
@dataclass
class DetectedPattern:
    pattern_type: PatternType
    confidence: float                 # 0.0 to 1.0
    suggested_workflow: Optional[str]
    metadata: Dict[str, Any]
    detection_rules: List[str]

    @property
    def name(self) -> str             # Pattern name as string
    @property
    def is_confident(self) -> bool    # confidence > 0.7
```

---

### Firewall Entities (`firewall_result.py`)

#### FirewallAction (Enum)

```python
class FirewallAction(Enum):
    ALLOW = "allow"       # Let through unchanged
    BLOCK = "block"       # Block entirely
    MODIFY = "modify"     # Modify parameters
    AUTO_FIX = "auto_fix" # Auto-fix issues
```

#### FirewallResult

Result of firewall validation.

```python
@dataclass
class FirewallResult:
    allowed: bool
    action: FirewallAction
    violations: List[FirewallViolation]
    modified_call: Optional[Dict]
    pre_steps: List[Dict]             # Steps to execute before
    message: str

    @classmethod
    def allow(cls) -> "FirewallResult"
    @classmethod
    def block(cls, message: str) -> "FirewallResult"
    @classmethod
    def auto_fix(cls, message: str, ...) -> "FirewallResult"
```

---

### Override Entities (`override_decision.py`)

#### ReplacementTool

A replacement tool in an override.

```python
@dataclass
class ReplacementTool:
    tool_name: str
    params: Dict[str, Any]
    inherit_params: List[str]         # Params to inherit from original
    description: str

    def resolve_params(self, original_params: Dict) -> Dict
        # Handles $param_name syntax and inherit_params
```

#### OverrideDecision

Decision about whether to override a tool call.

```python
@dataclass
class OverrideDecision:
    should_override: bool
    reasons: List[OverrideReason]
    replacement_tools: List[ReplacementTool]
    is_workflow_expansion: bool
    workflow_name: Optional[str]

    @classmethod
    def no_override(cls) -> "OverrideDecision"
    @classmethod
    def expand_to_workflow(cls, ...) -> "OverrideDecision"
```

---

## Usage Examples

### Creating a Tool Call Sequence

```python
from server.router.domain.entities import (
    InterceptedToolCall,
    CorrectedToolCall,
    ToolCallSequence,
)

# Intercept LLM call
original = InterceptedToolCall(
    tool_name="mesh_extrude_region",
    params={"move": [0.0, 0.0, 1.0]},
    original_prompt="extrude the top face",
)

# Create corrected sequence
sequence = ToolCallSequence(
    calls=[
        CorrectedToolCall(
            tool_name="system_set_mode",
            params={"mode": "EDIT"},
            is_injected=True,
        ),
        CorrectedToolCall(
            tool_name="mesh_select",
            params={"action": "all"},
            is_injected=True,
        ),
        CorrectedToolCall(
            tool_name="mesh_extrude_region",
            params={"move": [0.0, 0.0, 1.0]},
            original_tool_name="mesh_extrude_region",
        ),
    ],
    original_call=original,
    expansion_reason="Added mode switch and selection",
)

# Get execution list
for tool in sequence.to_execution_list():
    execute(tool["tool"], tool["params"])
```

---

## Tests

- `tests/unit/router/domain/test_entities.py` - 32 tests

---

## See Also

- [01-directory-structure.md](./01-directory-structure.md)
- [03-domain-interfaces.md](./03-domain-interfaces.md) (next)
