# Router Supervisor Documentation

> Intelligent Router acting as supervisor over LLM tool calls.

---

## Quick Links

| Document | Description |
|----------|-------------|
| [ROUTER_HIGH_LEVEL_OVERVIEW.md](./ROUTER_HIGH_LEVEL_OVERVIEW.md) | Concept and architecture |
| [ROUTER_ARCHITECTURE.md](./ROUTER_ARCHITECTURE.md) | Code templates and structure |
| [IMPLEMENTATION/](./IMPLEMENTATION/) | Step-by-step implementation docs |
| [WORKFLOWS/](./WORKFLOWS/) | Predefined workflow definitions |
| [TOOLS/](./TOOLS/) | **Guide for adding new tools to Router** |

---

## Key Concept

**Router is NOT just an "intent matcher".**

Traditional approach:
```
User → LLM → tool_call → Blender
(LLM decides everything, errors propagate)
```

New architecture:
```
User → LLM → tool_call → ROUTER → corrected_tools → Blender
                            ↑
                  [Scene Context Analyzer]
                  [Geometry Pattern Detector]
                  [Tool Correction Engine]
                  [Workflow Expansion Engine]
                  [Error Firewall]
```

---

## Components

| Component | Purpose | Status |
|-----------|---------|--------|
| **Tool Interceptor** | Capture LLM tool calls | ✅ Done |
| **Scene Context Analyzer** | Read Blender state | ✅ Done |
| **Geometry Pattern Detector** | Detect tower/phone/table patterns | ✅ Done |
| **Tool Correction Engine** | Fix params, mode, selection | ✅ Done |
| **Tool Override Engine** | Replace with better alternatives | ✅ Done |
| **Workflow Expansion Engine** | 1 tool → N tools | ✅ Done |
| **Error Firewall** | Block invalid operations | ✅ Done |
| **Intent Classifier** | Offline intent matching (LaBSE) | ✅ Done |
| **SupervisorRouter** | Main orchestrator | ✅ Done |
| **WorkflowIntentClassifier** | Semantic workflow matching (LaBSE) | ✅ Done |
| **SemanticWorkflowMatcher** | Matching + generalization | ✅ Done |
| **ProportionInheritance** | Cross-workflow rule inheritance | ✅ Done |
| **FeedbackCollector** | Learning from user feedback | ✅ Done |
| **WorkflowAdapter** | Confidence-based workflow adaptation (TASK-051) | ✅ Done |
| **LanceVectorStore** | LanceDB vector database (TASK-047) | ✅ Done |
| **IVectorStore** | Vector store interface (DIP compliance) | ✅ Done |
| **PickleToLanceMigration** | Legacy pickle cache migration | ✅ Done |
| **Shared LaBSE via DI** | Single model instance (~1.8GB RAM) (TASK-048) | ✅ Done |
| **ParameterStore** | Learned parameter mappings via LaBSE (TASK-055) | ✅ Done |
| **ParameterResolver** | Three-tier parameter resolution with hybrid context extraction (TASK-055, TASK-055-FIX-3) | ✅ Done |
| **EnsembleMatcher** | Parallel multi-matcher orchestrator (TASK-053) | ✅ Done |
| **EnsembleAggregator** | Weighted consensus aggregation (TASK-053) | ✅ Done |
| **ModifierExtractor** | LaBSE semantic modifier matching (TASK-053) | ✅ Done |
| **KeywordMatcher** | Trigger keyword matching (TASK-053) | ✅ Done |
| **SemanticMatcher** | LaBSE workflow similarity (TASK-053) | ✅ Done |
| **PatternMatcher** | Geometry pattern detection (TASK-053) | ✅ Done |

---

## Directory Structure

```
server/router/
├── domain/
│   ├── entities/           # Data classes (no dependencies)
│   │   ├── tool_call.py
│   │   ├── scene_context.py
│   │   └── pattern.py
│   └── interfaces/         # Abstract interfaces
│       ├── i_interceptor.py
│       ├── i_analyzer.py
│       └── i_correction_engine.py
│
├── application/
│   ├── interceptor/        # Tool interception
│   │   └── tool_interceptor.py
│   ├── analyzers/          # Scene & pattern analysis
│   │   ├── scene_context_analyzer.py
│   │   ├── geometry_pattern_detector.py
│   │   └── proportion_calculator.py
│   ├── engines/            # Correction, override, expansion
│   │   ├── tool_correction_engine.py
│   │   ├── tool_override_engine.py
│   │   ├── workflow_expansion_engine.py
│   │   └── error_firewall.py
│   ├── classifier/         # Intent classification (LaBSE)
│   │   ├── intent_classifier.py
│   │   └── workflow_intent_classifier.py   # TASK-046
│   ├── matcher/            # Semantic workflow matching (TASK-046)
│   │   └── semantic_workflow_matcher.py
│   ├── inheritance/        # Proportion inheritance (TASK-046)
│   │   └── proportion_inheritance.py
│   ├── learning/           # Feedback learning (TASK-046)
│   │   └── feedback_collector.py
│   ├── evaluator/          # Condition & expression evaluation
│   │   ├── condition_evaluator.py
│   │   ├── expression_evaluator.py
│   │   └── proportion_resolver.py
│   ├── resolver/           # Parameter resolution (TASK-055)
│   │   ├── parameter_store.py
│   │   └── parameter_resolver.py
│   ├── triggerer/          # Workflow triggering
│   │   └── workflow_triggerer.py
│   ├── workflows/          # Predefined workflows
│   │   ├── registry.py
│   │   ├── base.py
│   │   ├── phone_workflow.py
│   │   ├── tower_workflow.py
│   │   ├── screen_cutout_workflow.py
│   │   └── custom/         # Custom YAML workflows
│   └── router.py           # SupervisorRouter
│
├── infrastructure/
│   ├── metadata_loader.py  # Tool metadata loader
│   ├── config.py           # Router configuration
│   ├── logger.py           # Telemetry
│   ├── vector_store/       # LanceDB vector storage (TASK-047)
│   │   ├── __init__.py
│   │   ├── lance_store.py  # LanceVectorStore implementation
│   │   └── migrations.py   # Pickle to Lance migration
│   └── tools_metadata/     # Per-tool JSON metadata (modular)
│       ├── _schema.json    # JSON Schema for validation
│       ├── scene/          # scene_*.json files
│       ├── system/         # system_*.json files
│       ├── modeling/       # modeling_*.json files
│       ├── mesh/           # mesh_*.json files
│       ├── material/       # material_*.json files
│       ├── uv/             # uv_*.json files
│       ├── curve/          # curve_*.json files
│       ├── collection/     # collection_*.json files
│       ├── lattice/        # lattice_*.json files
│       ├── sculpt/         # sculpt_*.json files
│       └── baking/         # baking_*.json files
│
└── adapters/
    └── mcp_integration.py  # Hook into MCP server
```

---

## Implementation Plan

See [TASK-039: Router Supervisor Implementation](../_TASKS/TASK-039_Router_Supervisor_Implementation.md)

### Phases

| Phase | Description | Tasks |
|-------|-------------|-------|
| **Phase 1** | Foundation & Infrastructure | 5 tasks |
| **Phase 2** | Scene Analysis | 4 tasks |
| **Phase 3** | Tool Processing Engines | 6 tasks |
| **Phase 4** | SupervisorRouter Integration | 3 tasks |
| **Phase 5** | Workflows & Patterns | 4 tasks |
| **Phase 6** | Testing & Documentation | 2 tasks |

**Total: 24 tasks**

---

## Detected Patterns

| Pattern | Detection Rule | Workflow |
|---------|---------------|----------|
| `tower_like` | height > width × 3 | Taper, subdivide |
| `phone_like` | flat, rectangular, thin | Screen cutout, bevel |
| `table_like` | flat horizontal surface | Leg extrusion |
| `pillar_like` | tall and cubic | Detail subdivisions |
| `wheel_like` | flat and circular | Spoke pattern |

---

## Example: Router in Action

**Scenario:** LLM sends `mesh_extrude_region` in OBJECT mode, no selection

```python
# LLM sends:
tool_call("mesh_extrude_region", {"move": [0.0, 0.0, 0.5]})

# Router detects:
# - Mode: OBJECT (mesh tool needs EDIT)
# - Selection: None (extrude needs selection)
# - Pattern: phone_like (suggests screen cutout)

# Router outputs:
[
    {"tool": "system_set_mode", "params": {"mode": "EDIT"}},
    {"tool": "mesh_select", "params": {"action": "all"}},
    {"tool": "mesh_inset", "params": {"thickness": 0.03}},
    {"tool": "mesh_extrude_region", "params": {"move": [0.0, 0.0, -0.02]}},
    {"tool": "system_set_mode", "params": {"mode": "OBJECT"}}
]
```

**Note:** `auto_selection` only injects `mesh_select(action="all")` when the **Edit Mode selection is empty**. Existing selections are preserved.

**Result:** Instead of crashing, Router fixes the issues and creates a proper screen cutout!

---

## Configuration

```python
RouterConfig:
    # Correction
    auto_mode_switch: True
    auto_selection: True
    clamp_parameters: True

    # Override
    enable_overrides: True
    enable_workflow_expansion: True

    # Firewall
    block_invalid_operations: True
    auto_fix_mode_violations: True

    # Thresholds
    embedding_threshold: 0.40
    bevel_max_ratio: 0.5
    subdivide_max_cuts: 6
```

---

## Semantic Generalization (TASK-046)

> **Status:** ✅ Done | [Task Details](../_TASKS/TASK-046_Router_Semantic_Generalization.md)

Extends Router with semantic workflow matching using LaBSE embeddings.

### Problem

```python
# Current: keyword matching only
user: "make a chair"
result: None  # No "chair" keyword in any workflow
```

### Solution

```python
# After TASK-046: semantic similarity
user: "make a chair"
result: [
    ("table_workflow", 0.72),   # Chair has legs like table
    ("tower_workflow", 0.45),   # Vertical structure
]
# Router uses table_workflow proportions for legs, etc.
```

### New Components

| Component | Purpose | File |
|-----------|---------|------|
| **WorkflowIntentClassifier** | LaBSE embeddings for workflows | `classifier/workflow_intent_classifier.py` |
| **SemanticWorkflowMatcher** | Match + generalize workflows | `matcher/semantic_workflow_matcher.py` |
| **ProportionInheritance** | Inherit rules from similar workflows | `inheritance/proportion_inheritance.py` |
| **FeedbackCollector** | Learn from user corrections | `learning/feedback_collector.py` |

### Key Features

1. **Semantic Matching** - Find workflows by meaning, not just keywords
2. **Generalization** - Use similar workflow when exact match missing
3. **Proportion Inheritance** - Combine rules from multiple workflows
4. **Multilingual Support** - LaBSE supports 109 languages
5. **Feedback Learning** - Improve matching over time

### Implementation Docs

- [28-workflow-intent-classifier.md](./IMPLEMENTATION/28-workflow-intent-classifier.md)
- [29-semantic-workflow-matcher.md](./IMPLEMENTATION/29-semantic-workflow-matcher.md)
- [30-proportion-inheritance.md](./IMPLEMENTATION/30-proportion-inheritance.md)
- [31-feedback-learning.md](./IMPLEMENTATION/31-feedback-learning.md)

---

## Confidence-Based Workflow Adaptation (TASK-051)

> **Status:** ✅ Done | [Task Details](../_TASKS/TASK-051_Confidence_Based_Workflow_Adaptation.md)

Adapts workflow execution based on semantic match confidence level.

### Problem

```python
# Router has confidence levels but doesn't use them
user: "simple table with 4 legs"
result: picnic_table_workflow (49 steps with benches)  # Too much!
```

### Solution

```python
# Adapt workflow based on confidence
user: "simple table with 4 legs"
confidence: LOW (0.68)
result: picnic_table_workflow → 33 steps (benches skipped)
```

### Adaptation Strategies

| Confidence | Strategy | Behavior |
|------------|----------|----------|
| **HIGH** (≥0.90) | `FULL` | Execute ALL steps |
| **MEDIUM** (≥0.75) | `FILTERED` | Core + tag-matching optional |
| **LOW** (≥0.60) | `CORE_ONLY` | Core steps only |
| **NONE** (<0.60) | `CORE_ONLY` | Core steps only (fallback) |

### New Components

| Component | Purpose | File |
|-----------|---------|------|
| **WorkflowAdapter** | Adapts workflow steps by confidence | `engines/workflow_adapter.py` |
| **WorkflowStep.optional** | Marks step as skippable | `workflows/base.py` |
| **WorkflowStep.tags** | Tags for MEDIUM filtering | `workflows/base.py` |

### Implementation Docs

- [32-workflow-adapter.md](./IMPLEMENTATION/32-workflow-adapter.md)

---

## LanceDB Vector Store (TASK-047)

> **Status:** ✅ Done | [Task Details](../_TASKS/TASK-047_Migration_Router_Semantic_Search_To_LanceDB.md)

Replaces pickle-based embedding cache with LanceDB - an embedded vector database.

### Problem

```python
# Before: O(N) linear search on all embeddings
EmbeddingCache (pickle)     WorkflowEmbeddingCache (pickle)
       ↓                              ↓
IntentClassifier            WorkflowIntentClassifier
       ↓                              ↓
   O(N) linear search on all embeddings
```

### Solution

```python
# After: O(log N) HNSW ANN search + metadata filters
              LanceVectorStore (LanceDB)
                 ├── namespace: "tools"
                 └── namespace: "workflows"
                        ↓
         IVectorStore interface (domain layer)
                        ↓
    IntentClassifier    WorkflowIntentClassifier
           ↓                      ↓
      O(log N) HNSW ANN search + metadata filters
```

### Key Benefits

| Feature | Benefit |
|---------|---------|
| **HNSW Indexing** | O(log N) instead of O(N) linear search |
| **Metadata Filtering** | Filter by category, mode, etc. |
| **Embedded-first** | No external server required (MCP compatible) |
| **Persistence** | Folder-based, survives restarts |
| **Namespace Support** | Unified store for tools and workflows |
| **In-Memory Fallback** | Works when LanceDB unavailable |

### New Components

| Component | Purpose | File |
|-----------|---------|------|
| **IVectorStore** | Domain interface for vector storage | `domain/interfaces/i_vector_store.py` |
| **LanceVectorStore** | LanceDB implementation | `infrastructure/vector_store/lance_store.py` |
| **PickleToLanceMigration** | Migrate legacy pickle caches | `infrastructure/vector_store/migrations.py` |
| **workflow_catalog** | MCP tool for workflow browsing/import (no execution) | `server/adapters/mcp/areas/workflow_catalog.py` |

### Workflow Catalog Usage

```text
# Import a workflow from YAML/JSON
workflow_catalog(action="import", filepath="/path/to/workflow.yaml")

# If a name conflict is detected
workflow_catalog(action="import", filepath="/path/to/workflow.yaml", overwrite=true)
workflow_catalog(action="import", filepath="/path/to/workflow.yaml", overwrite=false)
```

### Implementation Docs

- [32-lance-vector-store.md](./IMPLEMENTATION/32-lance-vector-store.md)

---

---

## Interactive Parameter Resolution (TASK-055)

> **Status:** ✅ Done | [Task Details](../_TASKS/TASK-055_Interactive_Parameter_Resolution.md)

Enables the Router to learn parameter values from LLM interactions and reuse them via semantic similarity.

### Problem

```python
# Before: Every language variant must be manually defined in YAML
modifiers:
  "straight legs":
    leg_angle_left: 0
  "proste nogi":      # Polish variant needed
    leg_angle_left: 0
```

### Solution

```python
# After: LLM provides value once, Router learns it
user: "table with straight legs"  # First time - asks LLM
router: leg_angle_left = ? → LLM responds: 0 → stored in LanceDB

user: "table with vertical legs"  # Second time - auto-resolved
router: leg_angle_left = 0 (learned, similarity: 0.87)
```

### Three-Tier Resolution

| Tier | Source | Priority | Description |
|------|--------|----------|-------------|
| **1** | YAML Modifiers | Highest | Explicit mappings from workflow definition |
| **2** | Learned Mappings | Medium | LaBSE semantic search in LanceDB |
| **3** | LLM Interactive | Fallback | Ask LLM, store response for future |

### New Components

| Component | Purpose | File |
|-----------|---------|------|
| **ParameterStore** | LanceDB storage for learned mappings | `resolver/parameter_store.py` |
| **ParameterResolver** | Three-tier resolution logic | `resolver/parameter_resolver.py` |
| **ParameterSchema** | Schema with semantic hints | `domain/entities/parameter.py` |

### Unified MCP Interface (TASK-055-FIX)

| Tool | Description |
|------|-------------|
| `router_set_goal(goal, resolved_params)` | Unified parameter resolution. Returns status (ready/needs_input/no_match/disabled/error), resolved/unresolved params. Call again with resolved_params to provide answers. Mappings auto-stored. |

### Thresholds

| Threshold | Value | Purpose |
|-----------|-------|---------|
| `relevance_threshold` | 0.50 | "Prompt relates to parameter" |
| `memory_threshold` | 0.85 | "Reuse stored mapping" |

---

## Ensemble Matching System (TASK-053)

> **Status:** ✅ Done | [Implementation Details](./IMPLEMENTATION/34-ensemble-matching-system.md)

Replaces fallback-based matching with parallel ensemble of multiple matchers.

### Architecture

```
User Prompt
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  EnsembleMatcher.match() - WHICH workflow?          │
│  ├─ KeywordMatcher  → workflow (0.40 weight)        │
│  ├─ SemanticMatcher → workflow (0.40 weight)        │
│  └─ PatternMatcher  → workflow (0.15 weight)        │
│                                                     │
│  EnsembleAggregator.aggregate()                     │
│  → Weighted consensus → best_workflow               │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  ModifierExtractor.extract() - WHICH params?        │
│  ├─ Extract n-grams from prompt                     │
│  ├─ LaBSE similarity vs YAML modifier keywords      │
│  └─ Select BEST match (highest similarity)          │
│                                                     │
│  → modifiers = {leg_angle_left: 0, ...}             │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│  execute_pending_workflow()                         │
│  ├─ final_variables = _pending_modifiers            │
│  ├─ WorkflowAdapter filters steps (confidence)      │
│  └─ Blender executes tool calls                     │
└─────────────────────────────────────────────────────┘
```

### Key Features

1. **Parallel Matching** - 3 matchers run independently with weighted scores
2. **LaBSE Modifier Extraction** - Multilingual modifier matching (109 languages)
3. **Best Match Selection** - Only highest similarity modifier applied
4. **Pattern Boost** - 1.3× score multiplier when geometry pattern matches

### Components

| Component | Purpose | File |
|-----------|---------|------|
| **EnsembleMatcher** | Orchestrates parallel matchers | `matcher/ensemble_matcher.py` |
| **EnsembleAggregator** | Weighted consensus + ModifierExtractor | `matcher/ensemble_aggregator.py` |
| **ModifierExtractor** | LaBSE semantic modifier matching | `matcher/modifier_extractor.py` |
| **KeywordMatcher** | Trigger keyword matching | `matcher/keyword_matcher.py` |
| **SemanticMatcher** | LaBSE workflow similarity | `matcher/semantic_matcher.py` |
| **PatternMatcher** | Geometry pattern detection | `matcher/pattern_matcher.py` |

### Multilingual Example

```python
# Polish prompt automatically matches English YAML keyword
prompt = "simple table with 4 straight legs"
result = extractor.extract(prompt, "picnic_table_workflow")
# → "prostymi nogami" ↔ "straight legs" = 0.877 similarity
# → modifiers = {leg_angle_left: 0, leg_angle_right: 0}
```

### Score Normalization (TASK-055-FIX)

**Problem**: When only SemanticMatcher fires (e.g., Polish prompt without English keywords), the maximum possible score is `1.0 × 0.40 = 0.40`, which is exactly at the MEDIUM/LOW boundary.

```
Prompt: "create picnic table" (Polish)

KeywordMatcher:  0.0   (no English keywords matched)
SemanticMatcher: 0.336 (0.84 × 0.40 weight)
PatternMatcher:  0.0   (empty scene)
─────────────────────────
TOTAL:           0.336 → OLD: LOW → CORE_ONLY (25 steps, no benches!)
```

**Solution**: Normalize score relative to contributing matchers' maximum:

```python
# Old: absolute thresholds
if score >= 0.7: return "HIGH"      # 0.336 < 0.7 → NO
elif score >= 0.4: return "MEDIUM"  # 0.336 < 0.4 → NO
else: return "LOW"                  # ← This won!

# New: normalized thresholds
max_possible = 0.40  # Only semantic matcher contributed
normalized = 0.336 / 0.40 = 0.84 (84%)

if normalized >= 0.70: return "HIGH"   # 0.84 >= 0.70 → YES!
elif normalized >= 0.50: return "MEDIUM"
else: return "LOW"
```

**Result**: Polish prompts now get fair confidence levels:

| Prompt | Matchers | Raw | Max | Normalized | Old | New |
|--------|----------|-----|-----|------------|-----|-----|
| "create picnic table" | semantic | 0.336 | 0.40 | 84% | LOW | **HIGH** |
| "create picnic table" | keyword+semantic | 0.74 | 0.80 | 92% | HIGH | **HIGH** |
| "simple table" | semantic | 0.30 | 0.40 | 75% | LOW | **LOW** (forced) |

---

## See Also

- [TOOLS_ARCHITECTURE_DEEP_DIVE.md](../TOOLS_ARCHITECTURE_DEEP_DIVE.md) - Tool design philosophy
- [MESH_TOOLS_ARCHITECTURE.md](../MESH_TOOLS_ARCHITECTURE.md) - Mesh tool reference
- [MEGA_TOOLS_ARCHITECTURE.md](../MEGA_TOOLS_ARCHITECTURE.md) - Mega tool patterns
