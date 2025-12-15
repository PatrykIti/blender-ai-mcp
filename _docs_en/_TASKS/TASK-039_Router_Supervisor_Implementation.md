# TASK-039: Router Supervisor Implementation

**Status:** ✅ Done
**Priority:** 🔴 High
**Category:** Core Infrastructure
**Estimated Sub-Tasks:** 24

---

## Overview

Implement the Router Supervisor layer - an intelligent system that intercepts, corrects, expands, and overrides LLM tool calls before execution. This transforms the MCP from a simple tool executor into a smart assistant that can fix LLM mistakes and optimize workflows.

**Key Principle:** Router is NOT just an "intent matcher" - it's an intelligent supervisor over LLM tool calls.

---

## Architecture Reference

See detailed specifications:
- `_docs/_ROUTER/ROUTER_HIGH_LEVEL_OVERVIEW.md`
- `_docs/_ROUTER/ROUTER_ARCHITECTURE.md`

---

## Phase Overview

| Phase | Description | Tasks | Priority |
|-------|-------------|-------|----------|
| **Phase 1** | Foundation & Infrastructure | 5 | 🔴 High |
| **Phase 2** | Scene Analysis | 4 | 🔴 High |
| **Phase 3** | Tool Processing Engines | 6 | 🔴 High |
| **Phase 4** | SupervisorRouter Integration | 3 | 🔴 High |
| **Phase 5** | Workflows & Patterns | 4 | 🟡 Medium |
| **Phase 6** | Testing & Documentation | 2 | 🟡 Medium |

**Total: 24 tasks**

---

## Phase 1: Foundation & Infrastructure

### TASK-039-1: Router Directory Structure

**Priority:** 🔴 High
**Layer:** Infrastructure

Create the router package structure following Clean Architecture.

**Deliverables:**
```
server/router/
├── __init__.py
├── domain/
│   ├── __init__.py
│   ├── entities/
│   │   ├── __init__.py
│   │   ├── tool_call.py           # InterceptedToolCall, CorrectedToolCall
│   │   ├── scene_context.py       # SceneContext dataclass
│   │   └── pattern.py             # DetectedPattern dataclass
│   └── interfaces/
│       ├── __init__.py
│       ├── i_interceptor.py
│       ├── i_analyzer.py
│       ├── i_correction_engine.py
│       ├── i_override_engine.py
│       └── i_firewall.py
├── application/
│   ├── __init__.py
│   ├── interceptor/
│   ├── analyzers/
│   ├── engines/
│   ├── classifier/
│   ├── workflows/
│   └── router.py                  # SupervisorRouter
├── infrastructure/
│   ├── __init__.py
│   ├── metadata_loader.py
│   ├── config.py
│   ├── logger.py
│   └── tools_metadata/            # Per-tool JSON metadata
│       ├── _schema.json           # JSON Schema for validation
│       ├── scene/
│       ├── system/
│       ├── modeling/
│       ├── mesh/
│       ├── material/
│       ├── uv/
│       ├── curve/
│       ├── collection/
│       ├── lattice/
│       ├── sculpt/
│       └── baking/
└── adapters/
    ├── __init__.py
    └── mcp_integration.py         # Hook into MCP server
```

**Documentation:**
- Update `_docs/_ROUTER/README.md` - add directory structure
- Create `_docs/_ROUTER/IMPLEMENTATION/` directory

**Changelog:** `55-YYYY-MM-DD-router-directory-structure.md`

---

### TASK-039-2: Domain Entities

**Priority:** 🔴 High
**Layer:** Domain

Create core domain entities (no external dependencies).

**Files:**
- `server/router/domain/entities/tool_call.py`
- `server/router/domain/entities/scene_context.py`
- `server/router/domain/entities/pattern.py`
- `server/router/domain/entities/firewall_result.py`
- `server/router/domain/entities/override_decision.py`

**Code:**
```python
# tool_call.py
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from datetime import datetime

@dataclass
class InterceptedToolCall:
    source: str  # "llm" or "router"
    tool_name: str
    params: Dict[str, Any]
    timestamp: datetime
    original_prompt: Optional[str] = None

@dataclass
class CorrectedToolCall:
    tool_name: str
    params: Dict[str, Any]
    corrections_applied: List[str]
    original_params: Dict[str, Any]
```

**Tests:**
- `tests/unit/router/domain/test_entities.py`

**Documentation:**
- `_docs/_ROUTER/IMPLEMENTATION/01-domain-entities.md`

**Changelog:** `56-YYYY-MM-DD-router-domain-entities.md`

---

### TASK-039-3: Domain Interfaces

**Priority:** 🔴 High
**Layer:** Domain

Define abstract interfaces for all router components.

**Files:**
- `server/router/domain/interfaces/i_interceptor.py`
- `server/router/domain/interfaces/i_scene_analyzer.py`
- `server/router/domain/interfaces/i_pattern_detector.py`
- `server/router/domain/interfaces/i_correction_engine.py`
- `server/router/domain/interfaces/i_override_engine.py`
- `server/router/domain/interfaces/i_expansion_engine.py`
- `server/router/domain/interfaces/i_firewall.py`

**Code Example:**
```python
# i_correction_engine.py
from abc import ABC, abstractmethod
from typing import List, Tuple
from ..entities.tool_call import CorrectedToolCall

class ICorrectionEngine(ABC):
    @abstractmethod
    def correct(self, tool_name: str, params: dict, mode: str) -> Tuple[List[CorrectedToolCall], List[str]]:
        """Correct tool call, returns (corrected_calls, pre_steps)."""
        pass
```

**Tests:**
- Interface contracts verification in unit tests

**Documentation:**
- `_docs/_ROUTER/IMPLEMENTATION/02-domain-interfaces.md`

**Changelog:** `57-YYYY-MM-DD-router-domain-interfaces.md`

---

### TASK-039-4: Metadata Loader

**Priority:** 🔴 High
**Layer:** Infrastructure

Create tool metadata loading system with modular per-tool JSON files.

**Files:**
- `server/router/infrastructure/metadata_loader.py`

**Directory Structure:**
```
server/router/infrastructure/tools_metadata/
├── _schema.json                    # JSON Schema for validation
├── scene/
│   ├── scene_list_objects.json
│   ├── scene_delete_object.json
│   ├── scene_context.json
│   └── ...
├── system/
│   ├── system_set_mode.json
│   ├── system_import_obj.json
│   ├── system_export_obj.json
│   └── ...
├── modeling/
│   ├── modeling_create_primitive.json
│   ├── modeling_add_modifier.json
│   └── ...
├── mesh/
│   ├── mesh_extrude.json
│   ├── mesh_bevel.json
│   ├── mesh_select.json
│   └── ...
├── material/
│   ├── material_create.json
│   ├── material_assign.json
│   └── ...
├── uv/
│   ├── uv_unwrap.json
│   ├── uv_project.json
│   └── ...
├── curve/
│   └── ...
├── collection/
│   └── ...
├── lattice/
│   └── ...
├── sculpt/
│   └── ...
└── baking/
    └── ...
```

**Single Tool Metadata Format:**
```json
{
  "tool_name": "mesh_extrude",
  "category": "mesh",
  "mode_required": "EDIT",
  "selection_required": true,
  "keywords": ["extrude", "pull", "extend", "push"],
  "sample_prompts": [
    "extrude the selected faces",
    "pull out the top face",
    "extend the geometry upward"
  ],
  "parameters": {
    "value": {"type": "float", "default": 0.0, "range": [-100.0, 100.0]},
    "direction": {"type": "enum", "options": ["NORMAL", "X", "Y", "Z"]}
  },
  "related_tools": ["mesh_inset", "mesh_bevel"],
  "patterns": ["phone_like:screen_cutout", "tower_like:height_extension"]
}
```

**Features:**
- Load tool definitions from per-tool JSON files
- Auto-discover files by walking `tools_metadata/` directory
- Parse keywords, categories, sample_prompts, parameters
- Validate against `_schema.json`
- Cache loaded metadata in memory
- Hot-reload support (detect file changes)

**MetadataLoader API:**
```python
class MetadataLoader:
    def load_all(self) -> Dict[str, ToolMetadata]
    def load_by_area(self, area: str) -> Dict[str, ToolMetadata]
    def get_tool(self, tool_name: str) -> Optional[ToolMetadata]
    def reload(self) -> None
    def validate_all(self) -> List[ValidationError]
```

**Tests:**
- `tests/unit/router/infrastructure/test_metadata_loader.py`

**Documentation:**
- `_docs/_ROUTER/IMPLEMENTATION/03-metadata-loader.md`

**Changelog:** `58-YYYY-MM-DD-router-metadata-loader.md`

---

### TASK-039-5: Router Configuration

**Priority:** 🔴 High
**Layer:** Infrastructure

Create configuration system for router behavior.

**Files:**
- `server/router/infrastructure/config.py`

**Configuration Options:**
```python
@dataclass
class RouterConfig:
    # Correction settings
    auto_mode_switch: bool = True
    auto_selection: bool = True
    clamp_parameters: bool = True

    # Override settings
    enable_overrides: bool = True
    enable_workflow_expansion: bool = True

    # Firewall settings
    block_invalid_operations: bool = True
    auto_fix_mode_violations: bool = True

    # Thresholds
    embedding_threshold: float = 0.40
    bevel_max_ratio: float = 0.5
    subdivide_max_cuts: int = 6
```

**Tests:**
- `tests/unit/router/infrastructure/test_config.py`

**Documentation:**
- `_docs/_ROUTER/IMPLEMENTATION/04-configuration.md`

**Changelog:** `59-YYYY-MM-DD-router-configuration.md`

---

## Phase 2: Scene Analysis

### TASK-039-6: Tool Interceptor

**Priority:** 🔴 High
**Layer:** Application

Implement LLM tool call interception.

**Files:**
- `server/router/application/interceptor/tool_interceptor.py`

**Features:**
- Capture all incoming tool calls
- Log with timestamp and context
- Maintain call history (last N calls)
- Extract original prompt if available

**Interface Implementation:**
```python
class ToolInterceptor(IInterceptor):
    def intercept(self, tool_name: str, params: Dict, prompt: str = None) -> InterceptedToolCall
    def get_history(self, limit: int = 10) -> List[InterceptedToolCall]
```

**Tests:**
- `tests/unit/router/application/test_tool_interceptor.py`

**Documentation:**
- `_docs/_ROUTER/IMPLEMENTATION/05-tool-interceptor.md`

**Changelog:** `60-YYYY-MM-DD-router-tool-interceptor.md`

---

### TASK-039-7: Scene Context Analyzer

**Priority:** 🔴 High
**Layer:** Application

Implement Blender scene state analysis.

**Files:**
- `server/router/application/analyzers/scene_context_analyzer.py`

**Features:**
- Query scene via RPC
- Extract: objects, dimensions, topology, mode, selection
- Calculate proportions (aspect ratios, is_flat, is_tall)
- Cache recent analysis (avoid repeated RPC calls)

**Data Collected:**
```python
SceneContext:
    active_object: str
    selected_objects: List[str]
    mode: str
    dimensions: Dict[str, float]
    proportions: Dict[str, Any]
    topology: Dict[str, int]
    materials: List[str]
```

**Tests:**
- `tests/unit/router/application/test_scene_context_analyzer.py`
- `tests/e2e/router/test_scene_analysis.py`

**Documentation:**
- `_docs/_ROUTER/IMPLEMENTATION/06-scene-context-analyzer.md`

**Changelog:** `61-YYYY-MM-DD-router-scene-context-analyzer.md`

---

### TASK-039-8: Geometry Pattern Detector

**Priority:** 🔴 High
**Layer:** Application

Implement geometry pattern recognition.

**Files:**
- `server/router/application/analyzers/geometry_pattern_detector.py`

**Patterns to Detect:**
| Pattern | Detection Rule |
|---------|---------------|
| `tower_like` | height > width * 3 |
| `phone_like` | is_flat AND 0.4 < aspect_xy < 0.7 AND z < 0.15 |
| `table_like` | is_flat AND NOT is_tall |
| `pillar_like` | is_tall AND is_cubic |
| `wheel_like` | is_flat AND aspect_xy ≈ 1.0 |
| `screen_area` | has inset face on top |

**Returns:**
```python
DetectedPattern:
    name: str
    confidence: float
    suggested_workflow: Optional[str]
    metadata: Dict[str, Any]
```

**Tests:**
- `tests/unit/router/application/test_geometry_pattern_detector.py`

**Documentation:**
- `_docs/_ROUTER/IMPLEMENTATION/07-geometry-pattern-detector.md`

**Changelog:** `62-YYYY-MM-DD-router-geometry-pattern-detector.md`

---

### TASK-039-9: Proportion Calculator

**Priority:** 🟡 Medium
**Layer:** Application (utility)

Implement detailed proportion analysis.

**Files:**
- `server/router/application/analyzers/proportion_calculator.py`

**Calculations:**
```python
def calculate_proportions(dimensions: Dict[str, float]) -> Dict[str, Any]:
    return {
        "aspect_xy": x / y,
        "aspect_xz": x / z,
        "aspect_yz": y / z,
        "is_flat": z < min(x, y) * 0.2,
        "is_tall": z > max(x, y) * 2,
        "is_wide": x > max(y, z) * 2,
        "is_cubic": max_dim / min_dim < 1.5,
        "dominant_axis": "x" | "y" | "z",
        "volume": x * y * z,
        "surface_area": 2 * (x*y + y*z + x*z)
    }
```

**Tests:**
- `tests/unit/router/application/test_proportion_calculator.py`

**Documentation:**
- `_docs/_ROUTER/IMPLEMENTATION/08-proportion-calculator.md`

**Changelog:** `63-YYYY-MM-DD-router-proportion-calculator.md`

---

## Phase 3: Tool Processing Engines

### TASK-039-10: Tool Correction Engine - Core

**Priority:** 🔴 High
**Layer:** Application

Implement parameter and mode correction.

**Files:**
- `server/router/application/engines/tool_correction_engine.py`

**Correction Types:**
1. **Parameter Clamping** - clamp values to valid ranges
2. **Mode Switching** - add mode switch if needed
3. **Selection Handling** - add selection if missing

**Parameter Limits:**
```python
PARAM_LIMITS = {
    "bevel_width": (0.001, 10.0),
    "bevel_segments": (1, 10),
    "extrude_depth": (-100.0, 100.0),
    "inset_thickness": (0.001, 10.0),
    "subdivide_cuts": (1, 6),
    "decimate_ratio": (0.01, 1.0),
}
```

**Mode Requirements:**
```python
MODE_REQUIREMENTS = {
    "mesh_": "EDIT",
    "modeling_": "OBJECT",
    "sculpt_": "SCULPT",
}
```

**Tests:**
- `tests/unit/router/application/test_tool_correction_engine.py`

**Documentation:**
- `_docs/_ROUTER/IMPLEMENTATION/09-tool-correction-engine.md`

**Changelog:** `64-YYYY-MM-DD-router-tool-correction-engine.md`

---

### TASK-039-11: Tool Correction Engine - Selection

**Priority:** 🔴 High
**Layer:** Application

Extend correction engine with selection auto-fix.

**Features:**
- Detect tools that require selection
- Auto-add `mesh_select(action="all")` if no selection
- Handle face/edge/vertex mode selection

**Selection-Required Tools:**
```python
SELECTION_TOOLS = [
    "mesh_extrude", "mesh_bevel", "mesh_inset",
    "mesh_delete", "mesh_duplicate", "mesh_transform",
    "mesh_dissolve", "mesh_bridge", "mesh_fill"
]
```

**Tests:**
- Extend `tests/unit/router/application/test_tool_correction_engine.py`

**Changelog:** `65-YYYY-MM-DD-router-correction-selection.md`

---

### TASK-039-12: Tool Override Engine

**Priority:** 🔴 High
**Layer:** Application

Implement tool replacement logic.

**Files:**
- `server/router/application/engines/tool_override_engine.py`

**Override Rules:**
```python
OVERRIDE_RULES = {
    "extrude_for_screen": {
        "trigger": tool == "mesh_extrude" AND pattern == "phone_like",
        "replacement": [inset, extrude_negative]
    },
    "subdivide_tower": {
        "trigger": tool == "mesh_subdivide" AND pattern == "tower_like",
        "replacement": [subdivide, select_top_loop, scale_down]
    }
}
```

**Returns:**
```python
OverrideDecision:
    should_override: bool
    reason: str
    replacement_tools: List[Dict]
```

**Tests:**
- `tests/unit/router/application/test_tool_override_engine.py`

**Documentation:**
- `_docs/_ROUTER/IMPLEMENTATION/10-tool-override-engine.md`

**Changelog:** `66-YYYY-MM-DD-router-tool-override-engine.md`

---

### TASK-039-13: Workflow Expansion Engine

**Priority:** 🔴 High
**Layer:** Application

Implement single-tool to workflow expansion.

**Files:**
- `server/router/application/engines/workflow_expansion_engine.py`

**Predefined Workflows:**
```python
WORKFLOWS = {
    "phone_workflow": [...],      # 10 steps
    "tower_workflow": [...],      # 7 steps
    "screen_cutout_workflow": [...],  # 4 steps
    "bevel_all_edges_workflow": [...] # 4 steps
}
```

**Expansion Rules:**
```python
EXPANSION_RULES = {
    "mesh_extrude": {
        "condition": no_selection,
        "expansion": [select_all_faces, extrude]
    }
}
```

**Parameter Inheritance:**
- Use `$param_name` syntax to inherit from original call
- `{"depth": "$depth"}` → takes depth from original params

**Tests:**
- `tests/unit/router/application/test_workflow_expansion_engine.py`

**Documentation:**
- `_docs/_ROUTER/IMPLEMENTATION/11-workflow-expansion-engine.md`

**Changelog:** `67-YYYY-MM-DD-router-workflow-expansion-engine.md`

---

### TASK-039-14: Error Firewall

**Priority:** 🔴 High
**Layer:** Application

Implement operation validation and blocking.

**Files:**
- `server/router/application/engines/error_firewall.py`

**Firewall Rules:**
| Rule | Condition | Action |
|------|-----------|--------|
| `mesh_in_object_mode` | mesh_* AND mode=OBJECT | auto_fix (switch to EDIT) |
| `object_in_edit_mode` | modeling_* AND mode=EDIT | auto_fix (switch to OBJECT) |
| `extrude_no_selection` | mesh_extrude AND selection=0 | auto_fix (select all) |
| `bevel_too_large` | bevel_width > min_dim * 0.5 | modify (clamp) |
| `delete_no_object` | scene_delete AND objects=0 | block |

**Returns:**
```python
FirewallResult:
    allowed: bool
    action: str  # "allow", "block", "modify", "auto_fix"
    message: str
    modified_call: Optional[Dict]
```

**Tests:**
- `tests/unit/router/application/test_error_firewall.py`

**Documentation:**
- `_docs/_ROUTER/IMPLEMENTATION/12-error-firewall.md`

**Changelog:** `68-YYYY-MM-DD-router-error-firewall.md`

---

### TASK-039-15: Intent Classifier (Sentence-Transformers)

**Priority:** 🟡 Medium
**Layer:** Application

Implement offline intent classification using semantic embeddings.

**Files:**
- `server/router/application/classifier/intent_classifier.py`
- `server/router/application/classifier/embedding_cache.py`

**Approach: LaBSE Embeddings (Offline, ~1.8GB RAM)**

Uses `sentence-transformers` with LaBSE model for multilingual semantic similarity.
No external API calls - everything runs locally.

**Features:**
- LaBSE embeddings for semantic understanding
- Cosine similarity matching against tool embeddings
- Pre-compute and cache tool embeddings on startup
- Fallback to TF-IDF if embeddings unavailable
- Support for multilingual prompts (LaBSE is 109 languages)

**Dependencies:**
- sentence-transformers (add to pyproject.toml)
- torch (CPU-only, auto-installed with sentence-transformers)

**Usage:**
```python
classifier = IntentClassifier()
classifier.load_tool_embeddings(metadata)  # Pre-compute on startup

# Fast inference (~10ms)
tool, confidence = classifier.predict("extrude the top face")
# → ("mesh_extrude", 0.87)

# Multilingual support
tool, confidence = classifier.predict("wyciągnij górną ścianę")
# → ("mesh_extrude", 0.82)
```

**Model Details:**
```python
# LaBSE - Language-agnostic BERT Sentence Embedding
MODEL_NAME = "sentence-transformers/LaBSE"
EMBEDDING_DIM = 768
RAM_USAGE = "~1.8GB"
INFERENCE_TIME = "~10ms per query"
```

**Embedding Cache:**
```python
class EmbeddingCache:
    def __init__(self, cache_dir: Path):
        self.cache_file = cache_dir / "tool_embeddings.pkl"

    def save(self, embeddings: Dict[str, np.ndarray]) -> None
    def load(self) -> Optional[Dict[str, np.ndarray]]
    def is_valid(self, metadata_hash: str) -> bool
```

**Tests:**
- `tests/unit/router/application/test_intent_classifier.py`

**Documentation:**
- `_docs/_ROUTER/IMPLEMENTATION/13-intent-classifier.md`

**Changelog:** `69-YYYY-MM-DD-router-intent-classifier.md`

---

## Phase 4: SupervisorRouter Integration

### TASK-039-16: SupervisorRouter Core

**Priority:** 🔴 High
**Layer:** Application

Implement main router orchestrator.

**Files:**
- `server/router/application/router.py`

**Pipeline:**
```
1. Intercept → capture LLM tool call
2. Analyze → read scene context
3. Detect → identify geometry patterns
4. Correct → fix params/mode/selection
5. Override → check for better alternatives
6. Expand → transform to workflow if needed
7. Firewall → validate each tool
8. Execute → return final tool list
```

**Methods:**
```python
class SupervisorRouter:
    def process_llm_tool_call(self, tool_name, params, prompt) -> List[Dict]
    def route(self, prompt: str) -> List[str]  # offline routing
```

**Tests:**
- `tests/unit/router/application/test_supervisor_router.py`
- `tests/e2e/router/test_supervisor_router_integration.py`

**Documentation:**
- `_docs/_ROUTER/IMPLEMENTATION/14-supervisor-router.md`

**Changelog:** `70-YYYY-MM-DD-router-supervisor-router.md`

---

### TASK-039-17: MCP Integration Adapter

**Priority:** 🔴 High
**Layer:** Adapters

Hook router into MCP server tool execution.

**Files:**
- `server/router/adapters/mcp_integration.py`
- Update `server/adapters/mcp/server.py`

**Integration Points:**
1. Intercept all tool calls before execution
2. Run through SupervisorRouter pipeline
3. Execute corrected/expanded tools
4. Return results

**Implementation:**
```python
# In MCP server, wrap tool execution
async def execute_tool(tool_name: str, params: dict):
    # Route through supervisor
    corrected_tools = router.process_llm_tool_call(tool_name, params)

    # Execute each tool in sequence
    results = []
    for tool in corrected_tools:
        result = await original_execute(tool["tool"], tool["params"])
        results.append(result)

    return combine_results(results)
```

**Tests:**
- `tests/e2e/router/test_mcp_integration.py`

**Documentation:**
- `_docs/_ROUTER/IMPLEMENTATION/15-mcp-integration.md`

**Changelog:** `71-YYYY-MM-DD-router-mcp-integration.md`

---

### TASK-039-18: Router Logging & Telemetry

**Priority:** 🟡 Medium
**Layer:** Infrastructure

Implement logging for router decisions.

**Files:**
- `server/router/infrastructure/logger.py`

**Log Events:**
- Tool intercepted (original call)
- Scene context analyzed
- Pattern detected
- Correction applied
- Override triggered
- Workflow expanded
- Firewall decision
- Final execution

**Log Format:**
```json
{
    "timestamp": "...",
    "event": "correction_applied",
    "original_tool": "mesh_extrude",
    "corrections": ["mode_switch:OBJECT->EDIT", "auto_select_all"],
    "final_tools": [...]
}
```

**Tests:**
- `tests/unit/router/infrastructure/test_logger.py`

**Documentation:**
- `_docs/_ROUTER/IMPLEMENTATION/16-logging-telemetry.md`

**Changelog:** `72-YYYY-MM-DD-router-logging.md`

---

## Phase 5: Workflows & Patterns

### TASK-039-19: Phone Workflow

**Priority:** 🟡 Medium
**Layer:** Application (workflows)

Implement complete phone/tablet modeling workflow.

**Files:**
- `server/router/application/workflows/phone_workflow.py`

**Workflow Steps:**
1. Create cube primitive
2. Scale to phone proportions (0.4 × 0.8 × 0.05)
3. Enter Edit mode
4. Select all edges
5. Bevel edges (width=0.02, segments=3)
6. Deselect all
7. Select top face
8. Inset face (thickness=0.03)
9. Extrude inward (depth=-0.02)
10. Exit to Object mode
11. Create dark material
12. Assign material

**Trigger:**
- Pattern: `phone_like`
- Intent: "create phone", "make smartphone", "create tablet"

**Tests:**
- `tests/e2e/router/workflows/test_phone_workflow.py`

**Documentation:**
- `_docs/_ROUTER/WORKFLOWS/phone-workflow.md`

**Changelog:** `73-YYYY-MM-DD-router-phone-workflow.md`

---

### TASK-039-20: Tower Workflow

**Priority:** 🟡 Medium
**Layer:** Application (workflows)

Implement tower/pillar modeling workflow.

**Files:**
- `server/router/application/workflows/tower_workflow.py`

**Workflow Steps:**
1. Create cube primitive
2. Scale to tower proportions (0.3 × 0.3 × 2.0)
3. Enter Edit mode
4. Subdivide (cuts=3)
5. Select top edge loop
6. Scale down (0.7 × 0.7 × 1.0) - taper effect
7. Exit to Object mode

**Trigger:**
- Pattern: `tower_like`
- Intent: "create tower", "make pillar", "build column"

**Tests:**
- `tests/e2e/router/workflows/test_tower_workflow.py`

**Documentation:**
- `_docs/_ROUTER/WORKFLOWS/tower-workflow.md`

**Changelog:** `74-YYYY-MM-DD-router-tower-workflow.md`

---

### TASK-039-21: Screen Cutout Workflow

**Priority:** 🟡 Medium
**Layer:** Application (workflows)

Implement screen/display cutout sub-workflow.

**Files:**
- `server/router/application/workflows/screen_cutout_workflow.py`

**Workflow Steps:**
1. Select top face (by location)
2. Inset face (thickness=0.05)
3. Extrude inward (depth=-0.02)
4. Bevel edges (width=0.005, segments=2)

**Trigger:**
- Pattern: `phone_like` + tool `mesh_extrude`
- Used as sub-workflow in phone workflow

**Tests:**
- `tests/e2e/router/workflows/test_screen_cutout_workflow.py`

**Documentation:**
- `_docs/_ROUTER/WORKFLOWS/screen-cutout-workflow.md`

**Changelog:** `75-YYYY-MM-DD-router-screen-cutout-workflow.md`

---

### TASK-039-22: Custom Workflow Definition System

**Priority:** 🟢 Low
**Layer:** Infrastructure

Allow users to define custom workflows via YAML/JSON.

**Files:**
- `server/router/infrastructure/workflow_loader.py`
- `server/router/workflows/custom/` directory

**Format:**
```yaml
# workflows/custom/my_workflow.yaml
name: "furniture_table"
trigger:
  pattern: "table_like"
  keywords: ["table", "desk", "surface"]
steps:
  - tool: "modeling_create_primitive"
    params: {type: "CUBE"}
  - tool: "modeling_transform"
    params: {scale: [1.2, 0.8, 0.05]}
  # ...
```

**Tests:**
- `tests/unit/router/infrastructure/test_workflow_loader.py`

**Documentation:**
- `_docs/_ROUTER/WORKFLOWS/custom-workflows.md`

**Changelog:** `76-YYYY-MM-DD-router-custom-workflows.md`

---

## Phase 6: Testing & Documentation

### TASK-039-23: Router E2E Test Suite

**Priority:** 🟡 Medium
**Layer:** Testing

Create comprehensive E2E tests for router.

**Files:**
- `tests/e2e/router/test_full_pipeline.py`
- `tests/e2e/router/test_pattern_detection.py`
- `tests/e2e/router/test_correction_scenarios.py`
- `tests/e2e/router/test_override_scenarios.py`
- `tests/e2e/router/test_workflow_execution.py`

**Test Scenarios:**
1. LLM sends mesh tool in OBJECT mode → auto-switch
2. LLM sends extrude without selection → auto-select
3. Phone pattern detected → workflow expansion
4. Invalid bevel width → clamped
5. Complete phone workflow execution

**Documentation:**
- `_docs/_ROUTER/TESTING.md`

**Changelog:** `77-YYYY-MM-DD-router-e2e-tests.md`

---

### TASK-039-24: Router Documentation Complete

**Priority:** 🟡 Medium
**Layer:** Documentation

Finalize all router documentation.

**Files to Create/Update:**
- `_docs/_ROUTER/README.md` - Main index
- `_docs/_ROUTER/QUICK_START.md` - Getting started
- `_docs/_ROUTER/CONFIGURATION.md` - All config options
- `_docs/_ROUTER/PATTERNS.md` - Pattern reference
- `_docs/_ROUTER/WORKFLOWS/README.md` - Workflow index
- `_docs/_ROUTER/API.md` - API reference
- `_docs/_ROUTER/TROUBLESHOOTING.md` - Common issues

**README.md Updates:**
- Update roadmap section
- Add router description
- Update feature list

**Changelog:** `78-YYYY-MM-DD-router-documentation-complete.md`

---

## Dependencies

### Python Packages (add to pyproject.toml)
```toml
[project]
dependencies = [
    # ... existing ...
    "sentence-transformers>=2.0.0,<4.0.0",  # LaBSE embeddings (~1.8GB RAM)
]

[dependency-groups]
dev = [
    # ... existing ...
]
```

**Note:** `sentence-transformers` automatically installs `torch` (CPU version) and `numpy`.
Model downloads on first use (~500MB for LaBSE).

### Optional (for faster similarity search with 1000+ tools)
```toml
# Optional: for FAISS-based similarity search
# "faiss-cpu>=1.7.0,<2.0.0",
```

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Unit test coverage | > 90% |
| E2E test scenarios | > 20 |
| Mode correction success | 100% |
| Pattern detection accuracy | > 85% |
| Workflow execution success | > 95% |

---

## Timeline Recommendation

| Phase | Estimated Effort |
|-------|-----------------|
| Phase 1 | 2-3 days |
| Phase 2 | 2-3 days |
| Phase 3 | 4-5 days |
| Phase 4 | 2-3 days |
| Phase 5 | 2-3 days |
| Phase 6 | 1-2 days |
| **Total** | **~15 days** |

---

## Related Tasks

- TASK-028: E2E Testing Infrastructure (✅ Done)
- TASK-038: Organic Modeling Tools (✅ Done)

---

## Notes

1. **Incremental Delivery** - Each phase delivers working functionality
2. **Backward Compatible** - Router is optional, MCP works without it
3. **Performance** - Scene analysis should be cached
4. **Extensibility** - Easy to add new patterns and workflows
