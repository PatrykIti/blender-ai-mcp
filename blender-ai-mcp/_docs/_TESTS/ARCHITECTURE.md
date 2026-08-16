# Test Architecture

## Overview

The blender-ai-mcp project uses a two-tier testing strategy:

1. **Unit Tests** - Fast, isolated tests with mocked Blender API (`bpy`/`bmesh`)
2. **E2E Tests** - Integration tests that connect to a running Blender instance via RPC

```
tests/
|-- conftest.py                 # Root config (markers)
|-- unit/                       # Unit tests (mocked bpy)
|   |-- conftest.py             # bpy/bmesh mock fixtures
|   |-- infrastructure/         # Config, RPC client tests
|   +-- tools/                  # Tool handler tests
|       |-- mesh/               # Mesh tools
|       |-- scene/              # Scene tools
|       |-- modeling/           # Modeling tools
|       |-- curve/              # Curve tools
|       |-- collection/         # Collection tools
|       |-- material/           # Material tools
|       +-- uv/                 # UV tools
|-- e2e/                        # E2E/Integration tests
|   |-- conftest.py             # RPC connection fixtures
|   +-- tools/                  # Real Blender tests
|       |-- collection/
|       |-- material/
|       |-- scene/
|       +-- uv/
+-- fixtures/                   # Shared test data
```

---

## Unit Tests

### Purpose
- Test server-side logic in isolation
- Verify tool handlers work correctly with mocked Blender responses
- Fast execution (~2-3 seconds for 250+ tests)
- Run in CI/CD without Blender

### Mock Strategy

The `tests/unit/conftest.py` provides comprehensive mocks for:

```python
# bpy module mock
@pytest.fixture(autouse=True)
def mock_bpy():
    """Auto-applied fixture that mocks bpy module."""
    mock = MagicMock()
    mock.context.active_object = None
    mock.context.selected_objects = []
    mock.data.objects = {}
    # ... comprehensive mock setup
    sys.modules['bpy'] = mock
    yield mock
```

### Running Unit Tests

```bash
# All unit tests
PYTHONPATH=. poetry run pytest tests/unit/ -v

# Specific area
PYTHONPATH=. poetry run pytest tests/unit/tools/mesh/ -v

# With coverage
PYTHONPATH=. poetry run pytest tests/unit/ --cov=server --cov-report=html
```

---

## E2E Tests

### Purpose
- Verify end-to-end integration with real Blender
- Test actual RPC communication
- Validate tool results against real Blender state

### Requirements
- Running Blender instance with addon enabled
- RPC server listening on configured port (default: 9876)

### Connection Management

The `tests/e2e/conftest.py` provides:

```python
@pytest.fixture(scope="session")
def rpc_client():
    """Session-scoped RPC client shared by all E2E tests.

    Prevents connection exhaustion by reusing single connection.
    """
    config = get_config()
    client = RpcClient(host=config.BLENDER_RPC_HOST, port=config.BLENDER_RPC_PORT)
    client.connect()
    yield client
    client.close()
```

**Key features:**
- Session-scoped connection (created once, reused by all tests)
- Automatic skip if Blender not available
- Proper cleanup on test session end

### Running E2E Tests

```bash
# 1. Start Blender with addon enabled
# 2. Run tests
PYTHONPATH=. poetry run pytest tests/e2e/ -v

# With detailed output
PYTHONPATH=. poetry run pytest tests/e2e/ -v -s
```

---

## Test Markers

Defined in `tests/conftest.py`:

| Marker | Description | Auto-applied |
|--------|-------------|--------------|
| `@pytest.mark.unit` | Unit tests | Yes, for `/unit/` |
| `@pytest.mark.e2e` | E2E tests | Yes, for `/e2e/` |
| `@pytest.mark.slow` | Slow tests (>5s) | Manual |

### Running by marker

```bash
# Only unit tests
PYTHONPATH=. poetry run pytest -m unit

# Only E2E tests
PYTHONPATH=. poetry run pytest -m e2e

# Exclude slow tests
PYTHONPATH=. poetry run pytest -m "not slow"
```

---

## CI/CD Integration

### GitHub Actions

Both `pr_checks.yml` and `release.yml` run **only unit tests**:

```yaml
- name: Run Unit Tests
  run: poetry run pytest tests/unit/ -v
```

E2E tests are excluded from CI because they require a running Blender instance.

### Local Development

For complete test coverage:

```bash
# 1. Run unit tests (always)
PYTHONPATH=. poetry run pytest tests/unit/ -v

# 2. Start Blender with addon
# 3. Run E2E tests
PYTHONPATH=. poetry run pytest tests/e2e/ -v

# Or run all at once (E2E will skip if no Blender)
PYTHONPATH=. poetry run pytest tests/ -v
```

---

## Writing Tests

### Unit Test Template

```python
"""Unit tests for {ToolName}."""
import pytest
from unittest.mock import MagicMock
from blender_addon.application.handlers.{area} import {Area}Handler


@pytest.fixture
def handler():
    return {Area}Handler()


@pytest.fixture
def mock_object():
    obj = MagicMock()
    obj.name = "TestObject"
    obj.type = "MESH"
    return obj


def test_tool_success(handler, mock_object, mock_bpy):
    """Test successful tool execution."""
    mock_bpy.data.objects = {"TestObject": mock_object}

    result = handler.some_tool("TestObject")

    assert "success" in result.lower()


def test_tool_invalid_input(handler, mock_bpy):
    """Test error handling for invalid input."""
    mock_bpy.data.objects = {}

    with pytest.raises(ValueError, match="not found"):
        handler.some_tool("NonExistent")
```

### E2E Test Template

```python
"""E2E tests for {ToolName}."""
import pytest
from server.application.tool_handlers.{area}_handler import {Area}ToolHandler


@pytest.fixture
def handler(rpc_client):
    """Uses shared RPC client from conftest."""
    return {Area}ToolHandler(rpc_client)


def test_tool_real_blender(handler):
    """Test against real Blender."""
    try:
        result = handler.some_tool(param="value")

        assert isinstance(result, dict)
        assert "expected_key" in result

    except RuntimeError as e:
        if "could not connect" in str(e).lower():
            pytest.skip(f"Blender not available: {e}")
        raise
```

---

## Test Coverage Goals

| Area | Unit Coverage | E2E Coverage |
|------|---------------|--------------|
| Scene Tools | High | Partial |
| Modeling Tools | High | Planned |
| Mesh Tools | High | Planned |
| Curve Tools | High | Planned |
| Collection Tools | Medium | Done |
| Material Tools | Medium | Done |
| UV Tools | Medium | Done |

---

## Troubleshooting

### E2E Tests Skip with "RPC not available"

1. Ensure Blender is running
2. Verify addon is enabled in Blender preferences
3. Check RPC port (default 9876) is not blocked
4. Test connection manually:
   ```python
   from server.adapters.rpc.client import RpcClient
   client = RpcClient(host="localhost", port=9876)
   print(client.connect())  # Should return True
   ```

### Unit Tests Fail with Import Errors

Ensure `PYTHONPATH` is set:
```bash
PYTHONPATH=. poetry run pytest tests/unit/
```

### Tests Hang or Timeout

- Check if Blender is frozen (E2E tests)
- Increase timeout: `pytest --timeout=60`
- Run with verbose: `pytest -v -s` to see progress
