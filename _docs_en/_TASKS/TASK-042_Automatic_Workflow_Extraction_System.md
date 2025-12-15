# Plan: Automatic Workflow Extraction System

## Summary

System for automatic workflow extraction from 3D models for blender-ai-mcp. Analyzes existing 3D models and generates YAML workflow definitions compatible with Router Supervisor.

**Goal**: Import 3D model → Analyze structure → Generate YAML workflow → Register in Router

### User decisions:
- **Scope**: Full implementation (all 6 phases including LLM Vision)
- **Output**: `server/router/application/workflows/custom/`
- **Method**: Hybrid (Rule-based + heuristics + LLM Vision)
- **POC**: 5 models initially for approach validation

---

## 1. Architecture

```
+-----------------------------------------------------------------------------+
|                      WORKFLOW EXTRACTION SYSTEM                             |
+-----------------------------------------------------------------------------+
|                                                                             |
|  +------------+    +------------+    +------------+    +-----------+        |
|  |   Model    |--->|  Topology  |--->|  Structure |--->| Workflow  |        |
|  |  Importer  |    |  Analyzer  |    | Decomposer |    | Generator |        |
|  +------------+    +------------+    +------------+    +-----------+        |
|        |                 |                 |                 |              |
|        v                 v                 v                 v              |
|  +------------+    +------------+    +------------+    +-----------+        |
|  | Format     |    | Proportion |    | Component  |    |   YAML    |        |
|  | Handlers   |    | Calculator |    | Detector   |    |   Writer  |        |
|  |(OBJ,FBX,GLB)    | (existing) |    |            |    |           |        |
|  +------------+    +------------+    +------------+    +-----------+        |
|                                                                             |
|                    +------------------------------+                         |
|                    |  LLM Vision Enhancement      |   (Optional)            |
|                    +------------------------------+                         |
|                                                                             |
|  +-----------------------------------------------------------------------+  |
|  |                     ROUTER INTEGRATION                                |  |
|  |  WorkflowRegistry | IntentClassifier | PatternDetector                |  |
|  +-----------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------+
```

### Directory structure (Clean Architecture)

```
server/router/
├── domain/
│   ├── entities/
│   │   ├── extracted_model.py        # NEW: Model analysis data classes
│   │   ├── model_component.py        # NEW: Component representation
│   │   └── reconstruction_step.py    # NEW: Reconstructed operation steps
│   └── interfaces/
│       ├── i_model_analyzer.py       # NEW: Analysis interface
│       ├── i_structure_decomposer.py # NEW: Decomposition interface
│       └── i_workflow_generator.py   # NEW: Generation interface
│
├── application/
│   ├── extraction/                   # NEW: Main extraction module
│   │   ├── __init__.py
│   │   ├── model_importer.py         # Import 3D models via RPC
│   │   ├── topology_analyzer.py      # Vertex/edge/face analysis
│   │   ├── structure_decomposer.py   # Component detection
│   │   ├── operation_mapper.py       # Map structure to MCP tools
│   │   └── workflow_generator.py     # Generate YAML definitions
│   │
│   └── extraction_vision/            # NEW: Optional LLM enhancement
│       ├── renderer.py               # Multi-angle rendering
│       └── semantic_analyzer.py      # LLM description extraction
│
├── infrastructure/
│   └── extraction_config.py          # NEW: Extraction settings
│
└── adapters/
    └── extraction_cli.py             # NEW: CLI interface

blender_addon/application/handlers/
└── extraction.py                     # NEW: Blender-side analysis
```

---

## 2. Implementation phases

### Phase 1: Model Import and Basic Analysis (POC Foundation) ✅ COMPLETE
**Time**: 2-3 days | **Status**: ✅ Done via TASK-044

**Implementation**: TASK-044 Extraction Analysis Tools

**Files created**:
- `server/domain/tools/extraction.py` - IExtractionTool interface
- `server/application/tool_handlers/extraction_handler.py` - RPC bridge
- `server/adapters/mcp/areas/extraction.py` - MCP tool definitions
- `blender_addon/application/handlers/extraction.py` - bmesh implementation

**MCP Tools available**:
| Tool | Status |
|------|--------|
| `extraction_deep_topology` | ✅ Implemented |
| `extraction_component_separate` | ✅ Implemented |
| `extraction_detect_symmetry` | ✅ Implemented |
| `extraction_edge_loop_analysis` | ✅ Implemented |
| `extraction_face_group_analysis` | ✅ Implemented |
| `extraction_render_angles` | ✅ Implemented |

**Deliverables**:
1. ✅ Import OBJ/FBX/GLB via existing tools
2. ✅ Extract topology (vertex/edge/face counts) - `extraction_deep_topology`
3. ✅ Calculate bounding box and proportions - `extraction_deep_topology`
4. ✅ Detect base primitive (cube, sphere, cylinder) - `extraction_deep_topology`
5. ✅ Component separation - `extraction_component_separate`
6. ✅ Symmetry detection - `extraction_detect_symmetry`
7. ✅ Feature detection (bevels, insets, extrusions) - `extraction_edge_loop_analysis`, `extraction_face_group_analysis`
8. ✅ Multi-angle rendering for LLM Vision - `extraction_render_angles`

**Tests**: 27 unit tests + 22 E2E tests (15 passed, 7 skipped without Blender)

### Phase 2: Structure Decomposition
**Time**: 3-4 days

**Files to create**:
- `server/router/domain/entities/model_component.py`
- `server/router/domain/interfaces/i_structure_decomposer.py`
- `server/router/application/extraction/structure_decomposer.py`

**Deliverables**:
1. Separate model into loose parts (components)
2. Detect symmetry (X/Y/Z mirror planes)
3. Identify parent-child relationships
4. Detect symmetric pairs

### Phase 3: Operation Mapping
**Time**: 3-4 days

**Files to create**:
- `server/router/domain/entities/reconstruction_step.py`
- `server/router/application/extraction/operation_mapper.py`

**Deliverables**:
1. Map component geometry to likely operations:
   - Thin border faces → inset
   - Recessed faces → extrude negative
   - Rounded edges → bevel
   - Regular subdivisions → subdivide/loop cut
2. Calculate operation parameters from geometry
3. Order operations logically

### Phase 4: Workflow Generation
**Time**: 2-3 days

**Files to create**:
- `server/router/domain/interfaces/i_workflow_generator.py`
- `server/router/application/extraction/workflow_generator.py`
- `server/router/infrastructure/extraction_config.py`

**Deliverables**:
1. Generate YAML workflow from reconstruction steps
2. Add `$AUTO_*` parameters for size-independent workflows
3. Generate trigger keywords
4. Validate against WorkflowLoader schema

### Phase 5: Router Integration
**Time**: 2 days

**Files to modify**:
- `server/router/application/workflows/registry.py`
- `server/router/application/analyzers/geometry_pattern_detector.py`

**Files to create**:
- `server/router/adapters/extraction_cli.py`

**Deliverables**:
1. Auto-register generated workflows
2. Update pattern detection if new pattern found
3. CLI interface for batch extraction

### Phase 6: LLM Vision Enhancement (Optional)
**Time**: 2-3 days

**Files to create**:
- `server/router/application/extraction_vision/renderer.py`
- `server/router/application/extraction_vision/semantic_analyzer.py`

**Deliverables**:
1. Render model from 4-6 angles
2. Send to Claude/GPT-4V for description
3. Extract semantic keywords

---

## 3. Key data structures

### ExtractedModel

```python
@dataclass
class ExtractedModel:
    name: str
    source_file: str
    source_format: str  # OBJ, FBX, GLB

    # Geometry
    bounding_box: BoundingBoxInfo
    topology: TopologyStats
    proportions: Dict[str, Any]

    # Structure
    base_primitive: BasePrimitive  # CUBE, CYLINDER, SPHERE, PLANE, CONE, CUSTOM
    primitive_confidence: float
    components: List[ModelComponent]
    symmetry: SymmetryInfo

    # Detected features
    has_beveled_edges: bool
    has_inset_faces: bool
    has_extruded_regions: bool
    has_subdivisions: bool

    # Metadata
    detected_pattern: Optional[str]
    suggested_keywords: List[str]
```

### ReconstructionStep

```python
@dataclass
class ReconstructionStep:
    order: int
    tool_name: str
    params: Dict[str, Any]
    description: str
    confidence: float

    uses_proportions: bool = False
    proportion_expressions: Dict[str, str] = {}  # For $AUTO_* params
    condition: Optional[str] = None
```

---

## 4. Heuristic algorithms

### Base Primitive Detection

| Primitive | Heuristics |
|-----------|------------|
| CUBE | 8 vertices, cubic proportions, 6 faces |
| CYLINDER | Circular cross-section, >12 vertices, uniform Z |
| SPHERE | High vertex count, all vertices equidistant from center |
| PLANE | 4 vertices, 1 face, flat (Z ≈ 0) |

### Feature Detection

| Feature | Indicators |
|---------|------------|
| Beveled edges | Extra edge loops between flat surfaces, chamfered corners |
| Inset faces | Coplanar faces surrounded by thin quad borders |
| Extrusions | Face groups at different Z levels, consistent normals |
| Subdivisions | Regular edge loop spacing, quads split into 4 |

---

## 5. New RPC commands

| Command | Description |
|---------|-------------|
| `extraction.deep_topology` | Extended topology analysis |
| `extraction.component_separate` | Separate by loose parts |
| `extraction.detect_symmetry` | Find symmetry planes |
| `extraction.edge_loop_analysis` | Analyze edge loops for bevel |
| `extraction.face_group_analysis` | Analyze face groups for inset/extrude |
| `extraction.render_angles` | Render from multiple angles (for LLM Vision) |

---

## 6. CLI Interface

```bash
# Extract single model
python -m server.router.adapters.extraction_cli extract phone.obj -o phone_workflow.yaml

# Batch extraction
python -m server.router.adapters.extraction_cli batch ./models/ -o ./workflows/

# Validate workflow
python -m server.router.adapters.extraction_cli validate phone_workflow.yaml
```

---

## 7. Success metrics (POC)

| Metric | Target |
|--------|--------|
| Import Success | 100% |
| Pattern Detection Accuracy | 80%+ |
| Base Primitive Detection | 80%+ |
| Feature Detection Accuracy | 70%+ |
| Valid YAML Generation | 100% |
| Workflow Execution Success | 90%+ |

---

## 8. Files to read before implementation

1. `server/router/application/analyzers/proportion_calculator.py` - pattern of calculation
2. `server/router/infrastructure/workflow_loader.py` - YAML workflow format
3. `server/router/application/workflows/base.py` - BaseWorkflow class
4. `blender_addon/application/handlers/scene.py` - existing scene operations
5. `server/router/application/analyzers/geometry_pattern_detector.py` - pattern detection

---

## 9. Risks and mitigations

| Risk | Mitigation |
|------|------------|
| Complex models produce incorrect operations | Start from simple primitives, iterate heuristics |
| Low confidence in operation mapping | Enable confidence scores, allow manual review |
| Generated workflows do not work | Validate via WorkflowLoader, test execution |
| Slow processing of large models | Timeout, chunk processing |

---

## 10. Available tools (TASK-043 Complete)

### Scene Utility Tools (ready to use)
Tools from TASK-043 are available and can assist workflow extraction:

| Tool | Use in Extraction |
|-----------|--------------------------|
| `scene_isolate_object` | Isolation of components for analysis (Phase 2) |
| `scene_camera_focus` | Focus on component for LLM Vision (Phase 6) |
| `scene_camera_orbit` | Rendering from various angles (Phase 6) |
| `scene_rename_object` | Naming detected components |
| `scene_hide_object` | Hiding parts during analysis |

---

## 11. Router status (verification)

### ✅ Properly connected:
- 10-step pipeline works
- 129 uses of `route_tool_call()` in MCP tools
- Workflow Python and YAML work
- Pattern detection works
- Intent classifier works
- Error firewall works

### ⚠️ To be completed:
- Extension of the workflow library (goal of this project)
- Tests for WorkflowTriggerer
