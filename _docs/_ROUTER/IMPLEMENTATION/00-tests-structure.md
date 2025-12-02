# Router Tests Structure

Documentation of test structure for Router Supervisor.

**Total tests:** 635
- Unit tests: 561
- E2E tests: 74

---

## Directory Structure

```
tests/
├── unit/router/                    # Unit tests (no Blender required)
│   ├── domain/                     # Entities and interfaces
│   │   ├── test_entities.py        # 32 tests
│   │   └── test_interfaces.py      # 24 tests
│   ├── application/                # Business logic
│   │   ├── test_tool_interceptor.py           # 25 tests
│   │   ├── test_scene_context_analyzer.py     # 20 tests
│   │   ├── test_geometry_pattern_detector.py  # 23 tests
│   │   ├── test_proportion_calculator.py      # 31 tests
│   │   ├── test_tool_correction_engine.py     # 43 tests
│   │   ├── test_tool_override_engine.py       # 27 tests
│   │   ├── test_workflow_expansion_engine.py  # 38 tests
│   │   ├── test_error_firewall.py             # 41 tests
│   │   ├── test_intent_classifier.py          # 36 tests
│   │   ├── test_supervisor_router.py          # 37 tests
│   │   └── workflows/
│   │       ├── test_workflows.py              # 33 tests
│   │       └── test_registry.py               # 22 tests
│   ├── infrastructure/             # Configuration, loader, logger
│   │   ├── test_config.py          # 16 tests
│   │   ├── test_metadata_loader.py # 20 tests
│   │   ├── test_workflow_loader.py # 31 tests
│   │   └── test_logger.py          # 30 tests
│   └── adapters/                   # MCP integration
│       └── test_mcp_integration.py # 32 tests
│
└── e2e/router/                     # E2E tests (requires Blender)
    ├── conftest.py                 # Fixtures (session-scoped)
    ├── test_router_scenarios.py    # 7 tests
    ├── test_pattern_detection.py   # 12 tests
    ├── test_workflow_execution.py  # 9 tests
    ├── test_full_pipeline.py       # 10 tests
    ├── test_error_firewall.py      # 7 tests
    ├── test_tool_override.py       # 6 tests
    ├── test_intent_classifier.py   # 8 tests
    └── test_edge_cases.py          # 15 tests
```

---

## Unit Tests (561 tests)

### Domain Layer (56 tests)

| File | Tests | Coverage |
|------|-------|----------|
| `test_entities.py` | 32 | All entities: `InterceptedToolCall`, `CorrectedToolCall`, `SceneContext`, `ObjectInfo`, `TopologyInfo`, `Pattern`, `FirewallResult`, `TelemetryEntry` |
| `test_interfaces.py` | 24 | All ABC interfaces: `IToolInterceptor`, `ISceneContextAnalyzer`, `IPatternDetector`, `ICorrectionEngine`, `IOverrideEngine`, `IExpansionEngine`, `IErrorFirewall` |

### Application Layer (396 tests)

| File | Tests | Coverage |
|------|-------|----------|
| `test_tool_interceptor.py` | 25 | Tool call interception, parameter extraction, name normalization |
| `test_scene_context_analyzer.py` | 20 | Mode analysis, active object, selection, dimensions |
| `test_geometry_pattern_detector.py` | 23 | Pattern detection: phone, tower, box, plate, sphere |
| `test_proportion_calculator.py` | 31 | Proportion calculation, aspect ratio, shape classification |
| `test_tool_correction_engine.py` | 43 | Mode correction (OBJECT↔EDIT↔SCULPT), auto-selection, parameter clamping |
| `test_tool_override_engine.py` | 27 | Override rules: `extrude_for_screen`, `subdivide_tower`, pattern conditions |
| `test_workflow_expansion_engine.py` | 38 | Workflow expansion: phone, tower, screen_cutout, parameterization |
| `test_error_firewall.py` | 41 | Firewall rules: blocking, auto-fix, validation, all action types |
| `test_intent_classifier.py` | 36 | Intent classification, multilingual (PL/EN/DE), fallback, TF-IDF |
| `test_supervisor_router.py` | 37 | Full pipeline, component orchestration, cache, telemetry |
| `test_workflows.py` | 33 | Workflow definitions: PhoneWorkflow, TowerWorkflow, ScreenCutoutWorkflow |
| `test_registry.py` | 22 | WorkflowRegistry: registration, lookup, pattern matching |

### Infrastructure Layer (97 tests)

| File | Tests | Coverage |
|------|-------|----------|
| `test_config.py` | 16 | RouterConfig: default values, validation, feature flags |
| `test_metadata_loader.py` | 20 | Loading tool metadata from JSON, schema validation |
| `test_workflow_loader.py` | 31 | Loading workflows from YAML/JSON, validation, custom workflows |
| `test_logger.py` | 30 | TelemetryLogger: event registration, formats, rotation |

### Adapters Layer (32 tests)

| File | Tests | Coverage |
|------|-------|----------|
| `test_mcp_integration.py` | 32 | MCPRouterIntegration, RouterMiddleware, FastMCP hook |

---

## E2E Tests (74 tests)

E2E tests require a running Blender instance with active RPC server.

### Fixtures (conftest.py)

```python
# Session-scoped - shared between all tests
@pytest.fixture(scope="session")
def router_config()        # Router configuration
def shared_classifier()    # IntentClassifier with LaBSE (~1.8GB RAM)
def router()               # SupervisorRouter with real RPC

# Function-scoped - runs for each test
@pytest.fixture
def clean_scene()          # Cleans scene + purge_orphans
```

**Important:** Classifier is session-scoped to avoid loading the LaBSE model (~1.8GB) multiple times. Without this, 74 tests × 1.8GB = ~133GB RAM.

### Test Files

| File | Tests | Coverage |
|------|-------|----------|
| `test_router_scenarios.py` | 7 | Basic scenarios: mode correction, parameter clamping, selection |
| `test_pattern_detection.py` | 12 | Pattern detection on real geometry, SceneContext analysis |
| `test_workflow_execution.py` | 9 | Workflow execution: phone, tower, screen_cutout, custom |
| `test_full_pipeline.py` | 10 | Full modeling sessions, error recovery, configuration |
| `test_error_firewall.py` | 7 | Operation blocking, mode/selection auto-fix, clamping |
| `test_tool_override.py` | 6 | Pattern-based override, configuration, execution |
| `test_intent_classifier.py` | 8 | Multilingual classification (EN/PL/DE), fallback, prompt influence |
| `test_edge_cases.py` | 15 | Edge cases: no object, multiple selected, mode transitions, invalid params |

---

## Detailed Component Coverage

### Error Firewall

| Rule | Unit Test | E2E Test |
|------|-----------|----------|
| `mesh_in_object_mode` | ✅ | ✅ |
| `sculpt_in_wrong_mode` | ✅ | ✅ |
| `extrude_no_selection` | ✅ | ✅ |
| `bevel_no_selection` | ✅ | ✅ |
| `inset_no_selection` | ✅ | ✅ |
| `delete_no_object` | ✅ | ✅ |
| `parameter_clamping` | ✅ | ✅ |
| `block_invalid` | ✅ | ✅ |

### Tool Override Engine

| Rule | Unit Test | E2E Test |
|------|-----------|----------|
| `extrude_for_screen` (phone) | ✅ | ✅ |
| `subdivide_tower` (tower) | ✅ | ✅ |
| `disabled_override` | ✅ | ✅ |

### Intent Classifier

| Feature | Unit Test | E2E Test |
|---------|-----------|----------|
| English prompts | ✅ | ✅ |
| Polish prompts | ✅ | ✅ |
| German prompts | ✅ | ✅ |
| Unknown/gibberish | ✅ | ✅ |
| Empty/None prompt | ✅ | ✅ |
| LaBSE embeddings | ✅ | ✅ |

### Workflow Expansion

| Workflow | Unit Test | E2E Test |
|----------|-----------|----------|
| PhoneWorkflow | ✅ | ✅ |
| TowerWorkflow | ✅ | ✅ |
| ScreenCutoutWorkflow | ✅ | ✅ |
| Custom YAML/JSON | ✅ | ✅ |

---

## Running Tests

### Unit tests (no Blender)
```bash
# All router unit tests
PYTHONPATH=. poetry run pytest tests/unit/router/ -v

# Specific component
PYTHONPATH=. poetry run pytest tests/unit/router/application/test_error_firewall.py -v
```

### E2E tests (requires Blender)
```bash
# Start Blender with addon (separate terminal)
# Addon must have active RPC server on localhost:9876

# All router E2E tests
PYTHONPATH=. poetry run pytest tests/e2e/router/ -v

# Specific file
PYTHONPATH=. poetry run pytest tests/e2e/router/test_edge_cases.py -v
```

### Quick coverage check
```bash
# Test count
PYTHONPATH=. poetry run pytest tests/unit/router/ --collect-only -q | tail -1
PYTHONPATH=. poetry run pytest tests/e2e/router/ --collect-only -q | tail -1
```

---

## Adding New Tests

### Unit test pattern
```python
"""
Unit tests for [Component Name].

Tests [brief description].
"""

import pytest
from unittest.mock import MagicMock

from server.router.application.engines.my_engine import MyEngine


class TestMyEngine:
    @pytest.fixture
    def engine(self):
        return MyEngine()

    def test_basic_functionality(self, engine):
        """Test: [what it tests]."""
        result = engine.do_something()
        assert result.is_valid
```

### E2E test pattern
```python
"""
E2E tests for [Feature].

Tests [brief description].
Requires running Blender instance.
"""

import pytest


class TestMyFeature:
    def test_feature_works(self, router, rpc_client, clean_scene):
        """Test: [what it tests]."""
        # Setup
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})

        # Action
        tools = router.process_llm_tool_call("mesh_bevel", {"width": 0.1})

        # Assert
        assert len(tools) > 0
```

---

## Changelog

| Date | Change | Tests |
|------|--------|-------|
| 2024-12 | TASK-039: Router implementation | 561 unit + 38 E2E |
| 2024-12 | TASK-040: Coverage extension | +36 E2E (74 total) |
