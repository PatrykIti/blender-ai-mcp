# 42 - E2E Testing Infrastructure (TASK-028)

**Date:** 2025-11-29
**Version:** 1.15.1

---

## Summary

Improved E2E testing infrastructure with session-scoped RPC connections, comprehensive documentation, and CI/CD workflow updates.

---

## Changes

### Test Infrastructure

| Change | Description |
|--------|-------------|
| Session-scoped RPC client | Shared connection across all E2E tests (prevents exhaustion) |
| Test execution time | Reduced from ~38s to ~0.2s for 19 E2E tests |
| Snapshot hash fix | Exclude timestamp from hash calculation for consistency |

### Documentation

| File | Description |
|------|-------------|
| `_docs/_TESTS/README.md` | Quick start guide and test statistics |
| `_docs/_TESTS/ARCHITECTURE.md` | Full test architecture, patterns, templates |

### CI/CD Updates

| Workflow | Change |
|----------|--------|
| `pr_checks.yml` | Run only unit tests (`tests/unit/`) |
| `release.yml` | Run only unit tests (`tests/unit/`) |

---

## Files Changed

```
.github/workflows/pr_checks.yml
.github/workflows/release.yml
_docs/_TASKS/README.md
_docs/_TASKS/TASK-028_E2E_Testing_Infrastructure.md
_docs/_TESTS/ARCHITECTURE.md (new)
_docs/_TESTS/README.md (new)
tests/e2e/conftest.py
tests/e2e/tools/collection/test_collection_tools.py
tests/e2e/tools/material/test_material_tools.py
tests/e2e/tools/scene/test_scene_inspect_material_slots.py
tests/e2e/tools/scene/test_snapshot_tools.py
tests/e2e/tools/uv/test_uv_tools.py
```

---

## Test Results

```
Unit tests:  250 passed in 2.4s
E2E tests:   19 passed in 0.2s
Total:       269 passed
```

---

## Related

- [TASK-028: E2E Testing Infrastructure](../_TASKS/TASK-028_E2E_Testing_Infrastructure.md) (In Progress)
