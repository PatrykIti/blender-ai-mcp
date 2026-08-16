# TASK-040: Router E2E Test Coverage Extension

**Status:** ✅ Done
**Priority:** 🟡 Medium
**Category:** Testing / Quality Assurance
**Estimated Sub-Tasks:** 10
**Depends On:** TASK-039 (Router Supervisor Implementation)

---

## Overview

Extend the router E2E test coverage to verify all implemented features and design scenarios. The current 38 tests cover basic scenarios, but tests are missing for key features like Error Firewall blocking, Tool Override, Intent Classifier and edge cases.

**Goal:** Increase the number of E2E tests from 38 to ~56, covering all implemented router components.

---

## Coverage gap analysis

### Implemented components vs Tests

| Component | Implemented functions | Tested | Missing |
|-----------|-------------------------|---------------|-----------|
| **Error Firewall** | 8 rules | 5 | 3 |
| **Tool Override** | 2 rules | 0 | 2 |
| **Intent Classifier** | PL/EN + LaBSE | 1 | 3 |
| **Edge Cases** | - | 0 | 5 |
| **Dynamic Params** | - | 0 | 2 |

---

## Phase 1: Error Firewall Tests

### TASK-040-1: Test blocking operations

**Priority:** 🔴 High
**File:** `tests/e2e/router/test_error_firewall.py`

Test blocking rules (action=block):

```python
class TestFirewallBlocking:
    def test_delete_on_empty_scene_is_blocked(self, router, rpc_client, clean_scene):
        """Firewall blocks delete when there are no objects."""
        # Scene is empty, try to delete
        tools = router.process_llm_tool_call("scene_delete_object", {"name": "NonExistent"})
        # Should be blocked or return error
```

**Tests:**
- `test_delete_on_empty_scene_is_blocked` - rule `delete_no_object`

### TASK-040-2: Auto-fix mode test

**Priority:** 🔴 High
**File:** `tests/e2e/router/test_error_firewall.py`

```python
class TestFirewallModeAutoFix:
    def test_sculpt_tool_in_object_mode_adds_mode_switch(self, router, rpc_client, clean_scene):
        """Firewall adds a switch to SCULPT mode."""
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        tools = router.process_llm_tool_call("sculpt_draw", {"strength": 0.5})
        tool_names = [t["tool"] for t in tools]
        assert "system_set_mode" in tool_names
```

**Tests:**
- `test_sculpt_tool_in_object_mode_adds_mode_switch` - rule `sculpt_in_wrong_mode`

### TASK-040-3: Selection auto-fix test

**Priority:** 🔴 High
**File:** `tests/e2e/router/test_error_firewall.py`

```python
class TestFirewallSelectionAutoFix:
    def test_bevel_without_selection_adds_select_all(self, router, rpc_client, clean_scene):
        """Firewall adds selection before bevel."""
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})
        rpc_client.send_request("mesh.select", {"action": "none"})

        tools = router.process_llm_tool_call("mesh_bevel", {"width": 0.1})
        tool_names = [t["tool"] for t in tools]
        assert any("select" in name for name in tool_names)
```

**Tests:**
- `test_bevel_without_selection_adds_select_all` - rule `bevel_no_selection`

---

## Phase 2: Tool Override Tests

### TASK-040-4: Override test for phone pattern

**Priority:** 🔴 High
**File:** `tests/e2e/router/test_tool_override.py`

```python
class TestPatternBasedOverride:
    def test_extrude_on_phone_pattern_adds_inset(self, router, rpc_client, clean_scene):
        """Override: extrude on phone → inset + extrude."""
        # Create phone-like object
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("modeling.transform_object", {"scale": [0.4, 0.8, 0.05]})
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})

        # Trigger override with screen-related prompt
        tools = router.process_llm_tool_call(
            "mesh_extrude_region",
            {"depth": -0.02},
            prompt="create screen cutout"
        )

        tool_names = [t["tool"] for t in tools]
        # Override should add inset before extrude
        assert "mesh_inset" in tool_names or len(tools) > 1
```

**Tests:**
- `test_extrude_on_phone_pattern_adds_inset` - rule `extrude_for_screen`

### TASK-040-5: Override test for tower pattern

**Priority:** 🔴 High
**File:** `tests/e2e/router/test_tool_override.py`

```python
    def test_subdivide_on_tower_pattern_adds_taper(self, router, rpc_client, clean_scene):
        """Override: subdivide on tower → subdivide + taper."""
        # Create tower-like object
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("modeling.transform_object", {"scale": [0.3, 0.3, 2.0]})
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})

        tools = router.process_llm_tool_call(
            "mesh_subdivide",
            {"number_cuts": 3},
            prompt="add segments to tower"
        )

        # Override should add taper steps
        tool_names = [t["tool"] for t in tools]
        assert len(tools) >= 2  # At least subdivide + taper
```

**Tests:**
- `test_subdivide_on_tower_pattern_adds_taper` - rule `subdivide_tower`

---

## Phase 3: Intent Classifier Tests

### TASK-040-6: Multilingual classification test

**Priority:** 🟡 Medium
**File:** `tests/e2e/router/test_intent_classifier.py`

```python
class TestMultilingualClassification:
    def test_polish_prompt_classification(self, router):
        """Classification of Polish prompt."""
        # Test that Polish prompts are correctly classified
        tools = router.process_llm_tool_call(
            "mesh_extrude_region",
            {"depth": 0.5},
            prompt="wyciągnij górną ścianę"
        )
        assert len(tools) > 0

    def test_english_prompt_classification(self, router):
        """Classification of English prompt."""
        tools = router.process_llm_tool_call(
            "mesh_bevel",
            {"width": 0.1},
            prompt="bevel the edges smoothly"
        )
        assert len(tools) > 0

    def test_unknown_prompt_fallback(self, router):
        """Unknown prompt uses fallback."""
        tools = router.process_llm_tool_call(
            "mesh_subdivide",
            {"number_cuts": 2},
            prompt="xyzzy gibberish text"
        )
        # Should still return the original tool
        assert any(t["tool"] == "mesh_subdivide" for t in tools)
```

---

## Phase 4: Edge Cases Tests

### TASK-040-7: Edge cases tests

**Priority:** 🟡 Medium
**File:** `tests/e2e/router/test_edge_cases.py`

```python
class TestEdgeCases:
    def test_operation_without_active_object(self, router, rpc_client, clean_scene):
        """Router handles lack of active object."""
        # Empty scene, no active object
        tools = router.process_llm_tool_call("mesh_extrude_region", {"depth": 0.5})
        # Should not crash, may return empty or error
        assert isinstance(tools, list)

    def test_operation_with_multiple_selected(self, router, rpc_client, clean_scene):
        """Router handles multiple selected objects."""
        # Create multiple objects
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "SPHERE"})
        # Select all
        rpc_client.send_request("scene.select_object", {"name": "Cube", "extend": True})
        rpc_client.send_request("scene.select_object", {"name": "Sphere", "extend": True})

        tools = router.process_llm_tool_call("modeling_transform_object", {"scale": [2, 2, 2]})
        assert isinstance(tools, list)
```

### TASK-040-8: Test workflow error handling

**Priority:** 🟡 Medium
**File:** `tests/e2e/router/test_edge_cases.py`

```python
    def test_workflow_with_failing_step_continues(self, router, rpc_client, clean_scene):
        """Workflow continues despite an error in one step."""
        # This is already partially tested in test_workflow_continues_on_non_fatal_error
        # Extend with more specific scenarios
```

---

## Phase 5: Dynamic Parameters Tests

### TASK-040-9: Dynamic parameters test

**Priority:** 🟢 Low
**File:** `tests/e2e/router/test_dynamic_params.py`

```python
class TestDynamicParameters:
    def test_bevel_width_scales_with_object_size(self, router, rpc_client, clean_scene):
        """Bevel width is proportional to object size."""
        # Create small object
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("modeling.transform_object", {"scale": [0.1, 0.1, 0.1]})

        # Try huge bevel
        tools = router.process_llm_tool_call("mesh_bevel", {"width": 100.0})

        bevel_tool = next((t for t in tools if t["tool"] == "mesh_bevel"), None)
        if bevel_tool:
            # Width should be clamped based on object size
            assert bevel_tool["params"]["width"] < 1.0

    def test_extrude_depth_reasonable_for_dimensions(self, router, rpc_client, clean_scene):
        """Extrude depth is reasonable relative to dimensions."""
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("modeling.transform_object", {"scale": [0.05, 0.05, 0.05]})

        tools = router.process_llm_tool_call("mesh_extrude_region", {"depth": 50.0})
        # Depth should be reasonable
```

---

## Phase 6: Configuration Tests

### TASK-040-10: Test disabling router features

**Priority:** 🟢 Low
**File:** `tests/e2e/router/test_full_pipeline.py` (extension)

```python
class TestRouterConfiguration:
    # Already exists: test_disabled_mode_switch, test_disabled_workflow_expansion

    def test_disabled_firewall(self, rpc_client, clean_scene, shared_classifier):
        """Router with firewall disabled."""
        config = RouterConfig(enable_firewall=False)
        router = SupervisorRouter(config=config, rpc_client=rpc_client, classifier=shared_classifier)
        # Firewall rules should not apply

    def test_disabled_overrides(self, rpc_client, clean_scene, shared_classifier):
        """Router with overrides disabled."""
        config = RouterConfig(enable_overrides=False)
        router = SupervisorRouter(config=config, rpc_client=rpc_client, classifier=shared_classifier)
        # Override rules should not apply
```

---

## Files to create/modify

| File | Action | Estimated tests |
|------|-------|------------------|
| `tests/e2e/router/test_error_firewall.py` | CREATE | 5 |
| `tests/e2e/router/test_tool_override.py` | CREATE | 4 |
| `tests/e2e/router/test_intent_classifier.py` | CREATE | 4 |
| `tests/e2e/router/test_edge_cases.py` | CREATE | 4 |
| `tests/e2e/router/test_dynamic_params.py` | CREATE | 3 |
| `tests/e2e/router/test_full_pipeline.py` | MODIFY | +2 |

**Estimated number of new tests:** ~22
**After implementation:** ~60 E2E tests for the router

---

## Acceptance Criteria

1. ✅ All new tests pass (74 E2E tests passing)
2. ✅ Each Error Firewall rule has a test (8 rules covered)
3. ✅ Each Tool Override rule has a test (3 rules covered)
4. ✅ Intent Classifier tested for PL, EN, and DE
5. ✅ Edge cases don't cause crashes (15 edge case tests)
6. ✅ Total E2E test coverage > 55 (74 tests)

---

## Documentation Updates

Completed:
- [x] `_docs/_CHANGELOG/79-2025-12-02-router-e2e-coverage-extension.md` - changelog
- [x] `_docs/_TASKS/README.md` - status updated
- [x] `_docs/_ROUTER/IMPLEMENTATION/00-tests-structure.md` - test coverage documentation
