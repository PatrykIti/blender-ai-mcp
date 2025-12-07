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

## Documentation

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Detailed test architecture, patterns, and guidelines
- **[EXAMPLE_E2E_TESTS_RESULT.md](./EXAMPLE_E2E_TESTS_RESULT.md)** - Example E2E test output

## See Also

- [TASK-028: E2E Testing Infrastructure](../_TASKS/TASK-028_E2E_Testing_Infrastructure.md)
