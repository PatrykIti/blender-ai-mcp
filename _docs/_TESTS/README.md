# Tests Documentation

## Quick Start

### Unit Tests (No Blender Required)

```bash
# Run all unit tests
PYTHONPATH=. poetry run pytest tests/unit/ -v

# Run specific area
PYTHONPATH=. poetry run pytest tests/unit/tools/mesh/ -v
```

### E2E Tests (Requires Blender)

**Automated (Recommended):**
```bash
# Full automated flow: build → install addon → start Blender → run tests → cleanup
python3 scripts/run_e2e_tests.py

# Options:
python3 scripts/run_e2e_tests.py --skip-build      # Use existing addon ZIP
python3 scripts/run_e2e_tests.py --keep-blender    # Don't kill Blender after tests
python3 scripts/run_e2e_tests.py --quiet           # Don't stream output to console
```

**Manual:**
```bash
# 1. Start Blender with addon enabled
# 2. Run E2E tests
PYTHONPATH=. poetry run pytest tests/e2e/ -v
```

---

## Test Statistics

| Type | Count | Execution Time |
|------|-------|----------------|
| Unit Tests | 905+ | ~5-6 seconds |
| E2E Tests | 142 | ~12 seconds |

## Test Coverage by Area

| Area | Unit Tests | E2E Tests |
|------|------------|-----------|
| Scene | ✅ | ✅ |
| Modeling | ✅ | 🔄 |
| Mesh | ✅ | ✅ |
| Collection | ✅ | ✅ |
| Material | ✅ | ✅ |
| UV | ✅ | ✅ |
| Sculpt | ✅ | ✅ |
| Export | ✅ | ✅ |
| Import | ✅ | ✅ |
| Baking | ✅ | ✅ |
| System | ✅ | ✅ |
| Curve | ✅ | 🔄 |
| Router | ✅ | ✅ |

### Router & Workflow Subsystems

| Subsystem | Unit Tests | E2E Tests | Related Tasks |
|-----------|------------|-----------|---------------|
| **Ensemble Matching** | ✅ | ✅ | TASK-053, TASK-054 |
| **Parameter Resolution** | ✅ | ✅ | TASK-055-FIX |
| **Workflow Execution** | ✅ | ✅ | TASK-041, TASK-052 |
| **Expression Evaluator** | ✅ | 📋 Planned | **TASK-056-1**: Extended math functions (13 new) ✅ DONE |
| **Condition Evaluator** | ✅ | 📋 Planned | **TASK-056-2**: Parentheses support, operator precedence ✅ DONE |
| **Parameter Validation** | ✅ | 📋 Planned | **TASK-056-3**: Enum constraints ✅ DONE |
| **Step Dependencies** | ✅ | 📋 Planned | **TASK-056-4**: Topological sort, timeout, retry ✅ DONE |
| **Computed Parameters** | ✅ | 📋 Planned | **TASK-056-5**: Dependency graph, expression eval ✅ DONE |
| **Dynamic Workflow Steps** | 📋 Planned | 📋 Planned | **TASK-055-FIX-7**: Conditional planks, adaptive count |

---

## E2E Test Runner Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. BUILD ADDON                                              │
│    python scripts/build_addon.py → outputs/blender_ai_mcp.zip│
├─────────────────────────────────────────────────────────────┤
│ 2. CHECK & UNINSTALL OLD ADDON                              │
│    Blender --background → addon_utils.disable + rmtree      │
├─────────────────────────────────────────────────────────────┤
│ 3. INSTALL NEW ADDON                                        │
│    Blender --background → extract ZIP + addon_utils.enable  │
├─────────────────────────────────────────────────────────────┤
│ 4. START BLENDER WITH RPC                                   │
│    Blender (GUI mode) - RPC server requires main event loop │
│    Wait for port 8765...                                    │
├─────────────────────────────────────────────────────────────┤
│ 5. RUN E2E TESTS                                            │
│    poetry run pytest tests/e2e/ -v --tb=short               │
├─────────────────────────────────────────────────────────────┤
│ 6. SAVE LOG & CLEANUP                                       │
│    tests/e2e/e2e_test_{PASSED|FAILED}_{timestamp}.log       │
│    Kill Blender process                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Latest E2E Test Run

See [EXAMPLE_E2E_TESTS_RESULT.md](./EXAMPLE_E2E_TESTS_RESULT.md) for full output.

**Summary (2025-11-30):**
- **142 tests passed** in 12.25s
- Platform: macOS (Darwin), Python 3.13.9, Blender 5.0
- All tool areas covered

---

## Directory Structure

```
tests/
├── unit/                    # Fast tests with mocked bpy (CI/CD)
│   └── tools/
│       ├── mesh/
│       ├── modeling/
│       ├── scene/
│       ├── sculpt/
│       └── ...
├── e2e/                     # Integration tests with real Blender
│   ├── conftest.py          # RPC fixtures
│   └── tools/
│       ├── baking/
│       ├── collection/
│       ├── export/
│       ├── import_tool/
│       ├── knife_cut/
│       ├── material/
│       ├── mesh/
│       ├── scene/
│       ├── sculpt/
│       ├── system/
│       └── uv/
└── fixtures/                # Shared test fixtures
```

---

## CI/CD

GitHub Actions run **only unit tests** (no Blender available in CI):

- `pr_checks.yml` - Runs on pull requests
- `release.yml` - Runs on push to main

---

## Upcoming Test Requirements

### TASK-056: Workflow System Enhancements

**New Unit Tests Required:**

```
tests/unit/router/application/evaluator/
├── test_expression_evaluator_extended.py   # TASK-056-1: 13 new math functions
├── test_condition_evaluator_parentheses.py # TASK-056-2: Parentheses & precedence
└── test_parameter_validation_enum.py       # TASK-056-3: Enum constraints

tests/unit/router/infrastructure/
├── test_dependency_resolver.py             # TASK-056-4: Step dependencies
└── test_computed_parameters.py             # TASK-056-5: Computed param resolution
```

**Test Coverage Goals:**
- Expression evaluator: Each new function (tan, atan2, log, exp, etc.)
- Condition evaluator: Operator precedence `not` > `and` > `or`, nested parentheses
- Parameter validation: Enum constraints, rejection of invalid values
- Dependency resolver: Graph construction, circular dependency detection
- Computed parameters: Evaluation order, dependency tracking

**E2E Integration Tests:**
- Workflow loading with new features
- End-to-end execution with dependencies
- Error handling and retry logic
- Complex boolean conditions in real workflows

### TASK-055-FIX-7: Dynamic Plank System

**Manual Verification Required:**

```bash
# Test simple_table.yaml with different widths
ROUTER_ENABLED=true poetry run python -c "
from server.router.application.router import SupervisorRouter
router = SupervisorRouter()

# Test cases:
# 1. Default (0.8m) → 8 planks × 0.10m each
result = router.set_goal('prosty stół 0.8m szerokości')

# 2. Narrow (0.45m) → 5 planks × 0.09m each (fractional)
result = router.set_goal('stół 0.45m szerokości')

# 3. Wide (1.2m) → 12 planks × 0.10m each
result = router.set_goal('stół 1.2m szerokości')

# 4. Fractional (0.83m) → 9 planks × 0.0922m each
result = router.set_goal('stół 0.83m szerokości')
"
```

**Visual Verification:**
- Use `scene_get_viewport` to verify plank count and spacing
- Check plank width adapts correctly (`table_width / ceil(table_width / 0.10)`)
- Verify no gaps or overlaps in table top
- Confirm fractional widths work correctly

**Acceptance Criteria:**
- Parameter names: `leg_offset_x`, `leg_offset_y` (not old verbose names)
- New parameter: `plank_max_width` (default 0.10)
- 15 conditional planks with `condition: "ceil(table_width / plank_max_width) >= N"`
- Plank count adapts to table width dynamically
- No visual artifacts in generated tables

---

## Documentation

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Detailed test architecture, patterns, and guidelines
- **[EXAMPLE_E2E_TESTS_RESULT.md](./EXAMPLE_E2E_TESTS_RESULT.md)** - Example E2E test output

## See Also

- [TASK-028: E2E Testing Infrastructure](../_TASKS/TASK-028_E2E_Testing_Infrastructure.md)
- [TASK-056: Workflow System Enhancements](../_TASKS/TASK-056_Workflow_System_Enhancements.md)
- [TASK-055-FIX-7: Dynamic Plank System](../_TASKS/TASK-055-FIX-7_Dynamic_Plank_System_Simple_Table.md)
