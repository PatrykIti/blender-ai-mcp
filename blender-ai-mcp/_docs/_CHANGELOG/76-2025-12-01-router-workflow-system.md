# Changelog 76: Router Workflow System

**Date:** 2025-12-01
**Type:** Feature
**Task:** TASK-039-20, TASK-039-22

## Summary

Implemented the complete workflow system including WorkflowRegistry, WorkflowLoader, and custom workflow support via YAML/JSON files.

## Changes

### New/Updated Files

- `server/router/application/workflows/base.py` - Base classes
- `server/router/application/workflows/registry.py` - Central registry
- `server/router/infrastructure/workflow_loader.py` - YAML/JSON loader
- `server/router/application/workflows/custom/example_table.yaml` - Example
- `server/router/application/workflows/custom/example_chair.json` - Example
- `tests/unit/router/application/workflows/test_registry.py` - 22 tests
- `tests/unit/router/infrastructure/test_workflow_loader.py` - 32 tests

### Features

1. **Base Classes**
   - `WorkflowStep` - Single step in workflow
   - `WorkflowDefinition` - Complete workflow definition
   - `BaseWorkflow` - Abstract base for workflow classes

2. **Workflow Registry**
   - Central access to all workflows
   - Pattern-based and keyword-based lookup
   - Workflow expansion to tool calls
   - Custom workflow registration

3. **Custom Workflow Loader**
   - Load from YAML (.yaml, .yml) files
   - Load from JSON (.json) files
   - Parameter inheritance with `$param` syntax
   - Validation and error reporting
   - Save workflow templates

4. **Example Custom Workflows**
   - `example_table.yaml` - Table with legs
   - `example_chair.json` - Chair with back support

### API

```python
# Registry
from server.router.application.workflows import get_workflow_registry

registry = get_workflow_registry()
workflow_name = registry.find_by_pattern("phone_like")
calls = registry.expand_workflow("phone_workflow")

# Custom loader
from server.router.infrastructure.workflow_loader import get_workflow_loader

loader = get_workflow_loader()
workflows = loader.load_all()
template = loader.create_workflow_template()
```

## Test Coverage

- 22 unit tests for WorkflowRegistry
- 32 unit tests for WorkflowLoader
- 559 total router tests passing

## Related

- Completes Phase 5: Workflows & Patterns
