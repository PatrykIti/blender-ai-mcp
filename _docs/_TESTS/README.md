# Tests Documentation

## Quick Start

```bash
# Run unit tests (no Blender required)
PYTHONPATH=. poetry run pytest tests/unit/ -v

# Run E2E tests (requires running Blender with addon)
PYTHONPATH=. poetry run pytest tests/e2e/ -v

# Run all tests
PYTHONPATH=. poetry run pytest tests/ -v
```

## Test Statistics

| Type | Count | Execution Time |
|------|-------|----------------|
| Unit Tests | 250+ | ~2-3 seconds |
| E2E Tests | 19 | ~0.2 seconds* |

*With session-scoped RPC connection

## Documentation

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Detailed test architecture, patterns, and guidelines

## Directory Structure

```
tests/
|-- unit/           # Fast tests with mocked bpy (CI/CD)
|-- e2e/            # Integration tests with real Blender (local only)
+-- fixtures/       # Shared test data
```

## CI/CD

GitHub Actions run **only unit tests** (no Blender available in CI):

- `pr_checks.yml` - Runs on pull requests
- `release.yml` - Runs on push to main

## See Also

- [TASK-028: E2E Testing Infrastructure](../_TASKS/TASK-028_E2E_Testing_Infrastructure.md)
