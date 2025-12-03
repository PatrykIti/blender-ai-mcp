# Plan: Automatic Workflow Extraction System

## Podsumowanie

System automatycznej ekstrakcji workflow z modeli 3D dla blender-ai-mcp. Analizuje istniejące modele 3D i generuje definicje workflow YAML kompatybilne z Router Supervisor.

**Cel**: Import 3D model → Analiza struktury → Generowanie YAML workflow → Rejestracja w Router

### Decyzje użytkownika:
- **Scope**: Pełna implementacja (wszystkie 6 faz włącznie z LLM Vision)
- **Output**: `server/router/application/workflows/custom/`
- **Metoda**: Hybrid (Rule-based + heurystyki + LLM Vision)
- **POC**: 5 modeli na początek do walidacji podejścia

---

## 1. Architektura

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

### Struktura katalogów (Clean Architecture)

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

## 2. Fazy implementacji

### Phase 1: Model Import and Basic Analysis (POC Foundation)
**Czas**: 2-3 dni

**Pliki do utworzenia**:
- `server/router/domain/entities/extracted_model.py`
- `server/router/domain/interfaces/i_model_analyzer.py`
- `server/router/application/extraction/model_importer.py`
- `server/router/application/extraction/topology_analyzer.py`
- `blender_addon/application/handlers/extraction.py`

**Deliverables**:
1. Import OBJ/FBX/GLB via existing tools
2. Extract topology (vertex/edge/face counts)
3. Calculate bounding box and proportions
4. Detect base primitive (cube, sphere, cylinder)
5. Integrate with existing pattern detection

### Phase 2: Structure Decomposition
**Czas**: 3-4 dni

**Pliki do utworzenia**:
- `server/router/domain/entities/model_component.py`
- `server/router/domain/interfaces/i_structure_decomposer.py`
- `server/router/application/extraction/structure_decomposer.py`

**Deliverables**:
1. Separate model into loose parts (components)
2. Detect symmetry (X/Y/Z mirror planes)
3. Identify parent-child relationships
4. Detect symmetric pairs

### Phase 3: Operation Mapping
**Czas**: 3-4 dni

**Pliki do utworzenia**:
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
**Czas**: 2-3 dni

**Pliki do utworzenia**:
- `server/router/domain/interfaces/i_workflow_generator.py`
- `server/router/application/extraction/workflow_generator.py`
- `server/router/infrastructure/extraction_config.py`

**Deliverables**:
1. Generate YAML workflow from reconstruction steps
2. Add `$AUTO_*` parameters for size-independent workflows
3. Generate trigger keywords
4. Validate against WorkflowLoader schema

### Phase 5: Router Integration
**Czas**: 2 dni

**Pliki do modyfikacji**:
- `server/router/application/workflows/registry.py`
- `server/router/application/analyzers/geometry_pattern_detector.py`

**Pliki do utworzenia**:
- `server/router/adapters/extraction_cli.py`

**Deliverables**:
1. Auto-register generated workflows
2. Update pattern detection if new pattern found
3. CLI interface for batch extraction

### Phase 6: LLM Vision Enhancement (Optional)
**Czas**: 2-3 dni

**Pliki do utworzenia**:
- `server/router/application/extraction_vision/renderer.py`
- `server/router/application/extraction_vision/semantic_analyzer.py`

**Deliverables**:
1. Render model from 4-6 angles
2. Send to Claude/GPT-4V for description
3. Extract semantic keywords

---

## 3. Kluczowe struktury danych

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

## 4. Algorytmy heurystyczne

### Base Primitive Detection

| Primitive | Heurystyki |
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

## 5. Nowe komendy RPC

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

## 7. Metryki sukcesu (POC)

| Metric | Target |
|--------|--------|
| Import Success | 100% |
| Pattern Detection Accuracy | 80%+ |
| Base Primitive Detection | 80%+ |
| Feature Detection Accuracy | 70%+ |
| Valid YAML Generation | 100% |
| Workflow Execution Success | 90%+ |

---

## 8. Pliki do przeczytania przed implementacją

1. `server/router/application/analyzers/proportion_calculator.py` - wzorzec kalkulacji
2. `server/router/infrastructure/workflow_loader.py` - format YAML workflow
3. `server/router/application/workflows/base.py` - BaseWorkflow class
4. `blender_addon/application/handlers/scene.py` - istniejące operacje na scenie
5. `server/router/application/analyzers/geometry_pattern_detector.py` - detekcja wzorców

---

## 9. Ryzyka i mitigacje

| Risk | Mitigation |
|------|------------|
| Kompleksowe modele dają błędne operacje | Start od prostych prymitywów, iteruj heurystyki |
| Niskie confidence w mapowaniu operacji | Włącz confidence scores, pozwól na manual review |
| Wygenerowane workflow nie działają | Waliduj przez WorkflowLoader, testuj wykonanie |
| Wolne przetwarzanie dużych modeli | Timeout, chunk processing |

---

## 10. Status Router (weryfikacja)

### ✅ Poprawnie połączone:
- Pipeline 10-kroków działa
- 129 użyć `route_tool_call()` w narzędziach MCP
- Workflow Python i YAML działają
- Pattern detection działa
- Intent classifier działa
- Error firewall działa

### ⚠️ Do uzupełnienia:
- Rozszerzenie biblioteki workflow (cel tego projektu)
- Testy WorkflowTriggerer
