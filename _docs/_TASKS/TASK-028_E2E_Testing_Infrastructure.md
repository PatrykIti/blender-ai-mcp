# TASK-028: E2E Testing Infrastructure

**Status:** To Do
**Priority:** 🔴 High
**Category:** Testing Infrastructure

---

## Overview

Implement end-to-end (E2E) testing infrastructure that runs tests against a real Blender instance. Currently all tests are unit tests with mocked `bpy` - they verify that handlers call correct Blender operators, but don't verify actual Blender execution results.

---

## Why E2E Tests Are Critical

### Current Unit Test Limitations

```python
# Unit test - only verifies the call was made
bpy.ops.mesh.extrude_region_move.assert_called()
# Does NOT verify:
# - Blender actually creates geometry
# - The operator works in current Blender version
# - Context/poll requirements are met
```

### What E2E Tests Would Catch

1. **Blender API Changes** - Operators renamed/removed between versions
2. **Context Errors** - `poll()` failures in wrong mode/selection state
3. **Geometry Validation** - Actual vertex/face counts after operations
4. **RPC Integration** - Full communication stack works correctly
5. **Addon Registration** - All handlers properly registered

---

## Architecture

### Test Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     E2E Test Execution                          │
├─────────────────────────────────────────────────────────────────┤
│  1. pytest fixture: start_blender_with_addon                    │
│     └─ blender --background --python load_addon.py              │
│     └─ Addon starts RPC server on port 8765                     │
│                                                                 │
│  2. Test connects via RpcClient                                 │
│     └─ client = RpcClient(host='127.0.0.1', port=8765)         │
│                                                                 │
│  3. Test sends RPC command                                      │
│     └─ result = client.send_request("create_primitive", {...}) │
│                                                                 │
│  4. Test queries scene state                                    │
│     └─ objects = client.send_request("list_objects")           │
│                                                                 │
│  5. Test asserts on actual Blender state                        │
│     └─ assert "Cube" in objects                                │
│     └─ assert objects["Cube"]["vertex_count"] == 8             │
│                                                                 │
│  6. Fixture cleanup: stop Blender process                       │
└─────────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
tests/
├── unit/                          # Existing unit tests (mocked bpy)
│   ├── conftest.py                # bpy/bmesh mocks
│   ├── tools/
│   │   ├── mesh/
│   │   ├── scene/
│   │   ├── modeling/
│   │   ├── curve/
│   │   └── ...
│   └── infrastructure/
│
├── e2e/                           # New E2E tests (real Blender)
│   ├── conftest.py                # Blender process fixtures
│   ├── tools/
│   │   ├── mesh/
│   │   │   ├── test_extrude_e2e.py
│   │   │   ├── test_bevel_e2e.py
│   │   │   └── ...
│   │   ├── scene/
│   │   │   ├── test_create_primitive_e2e.py
│   │   │   └── ...
│   │   └── modeling/
│   └── integration/
│       ├── test_rpc_connection_e2e.py
│       └── test_full_workflow_e2e.py
│
└── fixtures/                      # Shared test data
    ├── blend_files/               # Pre-made .blend files for testing
    └── scripts/
        └── load_addon.py          # Script to load addon in Blender
```

---

## Implementation Details

### TASK-028-1: Blender Process Fixture

**Priority:** 🔴 High

Create pytest fixture that manages Blender subprocess.

```python
# tests/e2e/conftest.py
import pytest
import subprocess
import time
import os
from server.adapters.rpc.client import RpcClient

BLENDER_PATH = os.environ.get("BLENDER_PATH", "blender")
ADDON_PATH = os.path.abspath("blender_addon")
RPC_PORT = 8766  # Different port for tests to avoid conflicts

@pytest.fixture(scope="session")
def blender_process():
    """Start Blender with addon loaded for entire test session."""

    # Script to load addon
    load_script = f'''
import sys
sys.path.insert(0, "{ADDON_PATH}")
import blender_addon
blender_addon.register()

# Keep Blender running
import time
while True:
    time.sleep(1)
'''

    # Start Blender in background
    process = subprocess.Popen(
        [BLENDER_PATH, "--background", "--python-expr", load_script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for RPC server to start
    time.sleep(3)

    yield process

    # Cleanup
    process.terminate()
    process.wait(timeout=5)


@pytest.fixture
def rpc_client(blender_process):
    """Provide RPC client connected to test Blender instance."""
    client = RpcClient(host="127.0.0.1", port=RPC_PORT)
    connected = client.connect()
    assert connected, "Failed to connect to Blender RPC server"

    yield client

    client.close()


@pytest.fixture
def clean_scene(rpc_client):
    """Ensure clean scene before each test."""
    rpc_client.send_request("clean_scene")
    yield
```

### TASK-028-2: Scene Verification Helpers

**Priority:** 🔴 High

Create helper functions for asserting Blender state.

```python
# tests/e2e/helpers.py

def assert_object_exists(client, name: str):
    """Assert that object exists in scene."""
    result = client.send_request("list_objects")
    objects = result.get("objects", [])
    object_names = [obj["name"] for obj in objects]
    assert name in object_names, f"Object '{name}' not found. Existing: {object_names}"


def assert_object_vertex_count(client, name: str, expected: int):
    """Assert object has expected vertex count."""
    result = client.send_request("inspect_mesh_topology", {"object_name": name})
    actual = result.get("vertices", 0)
    assert actual == expected, f"Expected {expected} vertices, got {actual}"


def assert_object_face_count(client, name: str, expected: int):
    """Assert object has expected face count."""
    result = client.send_request("inspect_mesh_topology", {"object_name": name})
    actual = result.get("faces", 0)
    assert actual == expected, f"Expected {expected} faces, got {actual}"


def assert_mode(client, expected: str):
    """Assert current Blender mode."""
    result = client.send_request("get_mode")
    actual = result.get("mode", "")
    assert actual == expected, f"Expected mode '{expected}', got '{actual}'"


def assert_selection_count(client, expected: int, component: str = "objects"):
    """Assert number of selected items."""
    result = client.send_request("list_selection")
    if component == "objects":
        actual = len(result.get("selected_objects", []))
    elif component == "vertices":
        actual = result.get("selected_vertices", 0)
    elif component == "faces":
        actual = result.get("selected_faces", 0)
    else:
        actual = result.get(f"selected_{component}", 0)
    assert actual == expected, f"Expected {expected} selected {component}, got {actual}"
```

### TASK-028-3: Example E2E Tests

**Priority:** 🟡 Medium

#### Scene Tools E2E

```python
# tests/e2e/tools/scene/test_create_primitive_e2e.py
import pytest
from tests.e2e.helpers import assert_object_exists, assert_object_vertex_count

class TestCreatePrimitiveE2E:

    def test_create_cube(self, rpc_client, clean_scene):
        """Test creating a cube primitive."""
        result = rpc_client.send_request("create_primitive", {
            "primitive_type": "CUBE",
            "name": "TestCube"
        })

        assert "TestCube" in result
        assert_object_exists(rpc_client, "TestCube")
        assert_object_vertex_count(rpc_client, "TestCube", 8)

    def test_create_sphere(self, rpc_client, clean_scene):
        """Test creating a UV sphere."""
        result = rpc_client.send_request("create_primitive", {
            "primitive_type": "UV_SPHERE",
            "name": "TestSphere",
            "segments": 16,
            "rings": 8
        })

        assert_object_exists(rpc_client, "TestSphere")
        # UV sphere with 16 segments, 8 rings = specific vertex count
```

#### Mesh Tools E2E

```python
# tests/e2e/tools/mesh/test_extrude_e2e.py
import pytest
from tests.e2e.helpers import (
    assert_object_exists,
    assert_object_vertex_count,
    assert_object_face_count,
    assert_mode
)

class TestExtrudeE2E:

    @pytest.fixture
    def cube_in_edit_mode(self, rpc_client, clean_scene):
        """Create cube and enter Edit Mode."""
        rpc_client.send_request("create_primitive", {
            "primitive_type": "CUBE",
            "name": "ExtrudeCube"
        })
        rpc_client.send_request("set_mode", {"mode": "EDIT"})
        assert_mode(rpc_client, "EDIT_MESH")
        return "ExtrudeCube"

    def test_extrude_all_faces(self, rpc_client, cube_in_edit_mode):
        """Test extruding all faces of a cube."""
        # Select all
        rpc_client.send_request("select_all", {"action": "SELECT"})

        # Extrude
        result = rpc_client.send_request("extrude_region", {
            "move": [0, 0, 1]
        })

        # Verify geometry changed
        # Original cube: 8 verts, 6 faces
        # After extrude all: more vertices and faces
        assert_object_vertex_count(rpc_client, "ExtrudeCube", expected=16)

    def test_extrude_single_face(self, rpc_client, cube_in_edit_mode):
        """Test extruding a single face."""
        # Deselect all, then select top face by index
        rpc_client.send_request("select_all", {"action": "DESELECT"})
        rpc_client.send_request("select_by_index", {
            "indices": [5],  # Top face
            "mode": "FACE"
        })

        # Extrude
        rpc_client.send_request("extrude_region", {"move": [0, 0, 0.5]})

        # Verify: 1 new face extruded = 4 new verts, 5 new faces (4 sides + 1 cap)
        assert_object_vertex_count(rpc_client, "ExtrudeCube", expected=12)
```

#### Full Workflow E2E

```python
# tests/e2e/integration/test_full_workflow_e2e.py
import pytest

class TestFullWorkflowE2E:
    """Test complete modeling workflows."""

    def test_phone_base_workflow(self, rpc_client, clean_scene):
        """Test creating a basic phone shape."""
        # 1. Create cube
        rpc_client.send_request("create_primitive", {
            "primitive_type": "CUBE",
            "name": "Phone"
        })

        # 2. Scale to phone proportions
        rpc_client.send_request("transform_object", {
            "object_name": "Phone",
            "scale": [0.4, 0.8, 0.05]
        })

        # 3. Add bevel modifier
        rpc_client.send_request("add_modifier", {
            "object_name": "Phone",
            "modifier_type": "BEVEL",
            "params": {"width": 0.02, "segments": 3}
        })

        # 4. Verify final state
        result = rpc_client.send_request("inspect_object", {
            "object_name": "Phone"
        })

        assert result["modifiers"][0]["type"] == "BEVEL"
        assert result["dimensions"]["x"] < result["dimensions"]["y"]  # Taller than wide
```

---

### TASK-028-4: CI/CD Integration

**Priority:** 🟡 Medium

Configure GitHub Actions to run E2E tests.

```yaml
# .github/workflows/e2e-tests.yml
name: E2E Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  e2e-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install Blender
        run: |
          sudo apt-get update
          sudo apt-get install -y blender
          blender --version

      - name: Install dependencies
        run: |
          pip install poetry
          poetry install

      - name: Run E2E tests
        env:
          BLENDER_PATH: blender
        run: |
          poetry run pytest tests/e2e/ -v --tb=short

      - name: Upload test artifacts
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: e2e-test-logs
          path: tests/e2e/logs/
```

---

### TASK-028-5: Test Markers and Configuration

**Priority:** 🟢 Low

Configure pytest markers for selective test execution.

```python
# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
markers = [
    "unit: Unit tests (mocked bpy)",
    "e2e: End-to-end tests (real Blender)",
    "slow: Slow tests (> 5 seconds)",
    "blender_version(version): Requires specific Blender version",
]
testpaths = ["tests"]
```

```bash
# Run only unit tests
pytest tests/unit/ -v

# Run only E2E tests
pytest tests/e2e/ -v

# Run all tests
pytest -v

# Run specific area
pytest tests/e2e/tools/mesh/ -v
```

---

## Deliverables

| Task | Priority | Description |
|------|----------|-------------|
| TASK-028-1 | 🔴 High | Blender process fixture |
| TASK-028-2 | 🔴 High | Scene verification helpers |
| TASK-028-3 | 🟡 Medium | Example E2E tests (scene, mesh, workflow) |
| TASK-028-4 | 🟡 Medium | CI/CD integration |
| TASK-028-5 | 🟢 Low | Test markers and configuration |

---

## Dependencies

- Blender installed on test machine (or Docker image)
- pytest-timeout for hanging test protection
- Access to headless Blender (`--background` mode)

---

## Notes

1. **Test Isolation** - Each test should clean scene before running
2. **Performance** - Session-scoped Blender fixture to avoid restart overhead
3. **Debugging** - Save .blend file on test failure for investigation
4. **Version Matrix** - Consider testing against multiple Blender versions
