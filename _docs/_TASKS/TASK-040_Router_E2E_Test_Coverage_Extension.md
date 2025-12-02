# TASK-040: Router E2E Test Coverage Extension

**Status:** 🚧 To Do
**Priority:** 🟡 Medium
**Category:** Testing / Quality Assurance
**Estimated Sub-Tasks:** 10
**Depends On:** TASK-039 (Router Supervisor Implementation)

---

## Overview

Rozszerzyć pokrycie testów E2E routera, aby weryfikować wszystkie zaimplementowane funkcje i scenariusze projektowe. Obecne 38 testów pokrywa podstawowe scenariusze, ale brakuje testów dla kluczowych funkcji jak Error Firewall blocking, Tool Override, Intent Classifier i edge cases.

**Cel:** Zwiększyć liczbę testów E2E z 38 do ~56, pokrywając wszystkie zaimplementowane komponenty routera.

---

## Analiza luk w pokryciu

### Zaimplementowane komponenty vs Testy

| Komponent | Zaimplementowane funkcje | Przetestowane | Brakujące |
|-----------|-------------------------|---------------|-----------|
| **Error Firewall** | 8 reguł | 5 | 3 |
| **Tool Override** | 2 reguły | 0 | 2 |
| **Intent Classifier** | PL/EN + LaBSE | 1 | 3 |
| **Edge Cases** | - | 0 | 5 |
| **Dynamic Params** | - | 0 | 2 |

---

## Phase 1: Error Firewall Tests

### TASK-040-1: Test blokowania operacji

**Priority:** 🔴 High
**File:** `tests/e2e/router/test_error_firewall.py`

Testowanie reguł blokujących (action=block):

```python
class TestFirewallBlocking:
    def test_delete_on_empty_scene_is_blocked(self, router, rpc_client, clean_scene):
        """Firewall blokuje delete gdy brak obiektów."""
        # Scene is empty, try to delete
        tools = router.process_llm_tool_call("scene_delete_object", {"name": "NonExistent"})
        # Should be blocked or return error
```

**Testy:**
- `test_delete_on_empty_scene_is_blocked` - reguła `delete_no_object`

### TASK-040-2: Test auto-naprawy trybu

**Priority:** 🔴 High
**File:** `tests/e2e/router/test_error_firewall.py`

```python
class TestFirewallModeAutoFix:
    def test_sculpt_tool_in_object_mode_adds_mode_switch(self, router, rpc_client, clean_scene):
        """Firewall dodaje przełączenie do SCULPT mode."""
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        tools = router.process_llm_tool_call("sculpt_draw", {"strength": 0.5})
        tool_names = [t["tool"] for t in tools]
        assert "system_set_mode" in tool_names
```

**Testy:**
- `test_sculpt_tool_in_object_mode_adds_mode_switch` - reguła `sculpt_in_wrong_mode`

### TASK-040-3: Test auto-naprawy selekcji

**Priority:** 🔴 High
**File:** `tests/e2e/router/test_error_firewall.py`

```python
class TestFirewallSelectionAutoFix:
    def test_bevel_without_selection_adds_select_all(self, router, rpc_client, clean_scene):
        """Firewall dodaje selekcję przed bevel."""
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("system.set_mode", {"mode": "EDIT"})
        rpc_client.send_request("mesh.select", {"action": "none"})

        tools = router.process_llm_tool_call("mesh_bevel", {"width": 0.1})
        tool_names = [t["tool"] for t in tools]
        assert any("select" in name for name in tool_names)
```

**Testy:**
- `test_bevel_without_selection_adds_select_all` - reguła `bevel_no_selection`

---

## Phase 2: Tool Override Tests

### TASK-040-4: Test override dla wzorca phone

**Priority:** 🔴 High
**File:** `tests/e2e/router/test_tool_override.py`

```python
class TestPatternBasedOverride:
    def test_extrude_on_phone_pattern_adds_inset(self, router, rpc_client, clean_scene):
        """Override: extrude na phone → inset + extrude."""
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

**Testy:**
- `test_extrude_on_phone_pattern_adds_inset` - reguła `extrude_for_screen`

### TASK-040-5: Test override dla wzorca tower

**Priority:** 🔴 High
**File:** `tests/e2e/router/test_tool_override.py`

```python
    def test_subdivide_on_tower_pattern_adds_taper(self, router, rpc_client, clean_scene):
        """Override: subdivide na tower → subdivide + taper."""
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

**Testy:**
- `test_subdivide_on_tower_pattern_adds_taper` - reguła `subdivide_tower`

---

## Phase 3: Intent Classifier Tests

### TASK-040-6: Test klasyfikacji wielojęzycznej

**Priority:** 🟡 Medium
**File:** `tests/e2e/router/test_intent_classifier.py`

```python
class TestMultilingualClassification:
    def test_polish_prompt_classification(self, router):
        """Klasyfikacja polskiego prompta."""
        # Test that Polish prompts are correctly classified
        tools = router.process_llm_tool_call(
            "mesh_extrude_region",
            {"depth": 0.5},
            prompt="wyciągnij górną ścianę"
        )
        assert len(tools) > 0

    def test_english_prompt_classification(self, router):
        """Klasyfikacja angielskiego prompta."""
        tools = router.process_llm_tool_call(
            "mesh_bevel",
            {"width": 0.1},
            prompt="bevel the edges smoothly"
        )
        assert len(tools) > 0

    def test_unknown_prompt_fallback(self, router):
        """Nieznany prompt używa fallback."""
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

### TASK-040-7: Test przypadków brzegowych

**Priority:** 🟡 Medium
**File:** `tests/e2e/router/test_edge_cases.py`

```python
class TestEdgeCases:
    def test_operation_without_active_object(self, router, rpc_client, clean_scene):
        """Router obsługuje brak aktywnego obiektu."""
        # Empty scene, no active object
        tools = router.process_llm_tool_call("mesh_extrude_region", {"depth": 0.5})
        # Should not crash, may return empty or error
        assert isinstance(tools, list)

    def test_operation_with_multiple_selected(self, router, rpc_client, clean_scene):
        """Router obsługuje wiele zaznaczonych obiektów."""
        # Create multiple objects
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "SPHERE"})
        # Select all
        rpc_client.send_request("scene.select_object", {"name": "Cube", "extend": True})
        rpc_client.send_request("scene.select_object", {"name": "Sphere", "extend": True})

        tools = router.process_llm_tool_call("modeling_transform_object", {"scale": [2, 2, 2]})
        assert isinstance(tools, list)
```

### TASK-040-8: Test obsługi błędów workflow

**Priority:** 🟡 Medium
**File:** `tests/e2e/router/test_edge_cases.py`

```python
    def test_workflow_with_failing_step_continues(self, router, rpc_client, clean_scene):
        """Workflow kontynuuje mimo błędu w jednym kroku."""
        # This is already partially tested in test_workflow_continues_on_non_fatal_error
        # Extend with more specific scenarios
```

---

## Phase 5: Dynamic Parameters Tests

### TASK-040-9: Test parametrów dynamicznych

**Priority:** 🟢 Low
**File:** `tests/e2e/router/test_dynamic_params.py`

```python
class TestDynamicParameters:
    def test_bevel_width_scales_with_object_size(self, router, rpc_client, clean_scene):
        """Bevel width jest proporcjonalny do rozmiaru obiektu."""
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
        """Extrude depth jest rozsądny względem wymiarów."""
        rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
        rpc_client.send_request("modeling.transform_object", {"scale": [0.05, 0.05, 0.05]})

        tools = router.process_llm_tool_call("mesh_extrude_region", {"depth": 50.0})
        # Depth should be reasonable
```

---

## Phase 6: Configuration Tests

### TASK-040-10: Test wyłączania funkcji routera

**Priority:** 🟢 Low
**File:** `tests/e2e/router/test_full_pipeline.py` (rozszerzenie)

```python
class TestRouterConfiguration:
    # Already exists: test_disabled_mode_switch, test_disabled_workflow_expansion

    def test_disabled_firewall(self, rpc_client, clean_scene, shared_classifier):
        """Router z wyłączonym firewall."""
        config = RouterConfig(enable_firewall=False)
        router = SupervisorRouter(config=config, rpc_client=rpc_client, classifier=shared_classifier)
        # Firewall rules should not apply

    def test_disabled_overrides(self, rpc_client, clean_scene, shared_classifier):
        """Router z wyłączonymi override."""
        config = RouterConfig(enable_overrides=False)
        router = SupervisorRouter(config=config, rpc_client=rpc_client, classifier=shared_classifier)
        # Override rules should not apply
```

---

## Pliki do utworzenia/modyfikacji

| Plik | Akcja | Estymowane testy |
|------|-------|------------------|
| `tests/e2e/router/test_error_firewall.py` | CREATE | 5 |
| `tests/e2e/router/test_tool_override.py` | CREATE | 4 |
| `tests/e2e/router/test_intent_classifier.py` | CREATE | 4 |
| `tests/e2e/router/test_edge_cases.py` | CREATE | 4 |
| `tests/e2e/router/test_dynamic_params.py` | CREATE | 3 |
| `tests/e2e/router/test_full_pipeline.py` | MODIFY | +2 |

**Szacowana liczba nowych testów:** ~22
**Po implementacji:** ~60 testów E2E dla routera

---

## Acceptance Criteria

1. ✅ Wszystkie nowe testy przechodzą
2. ✅ Każda reguła Error Firewall ma test
3. ✅ Każda reguła Tool Override ma test
4. ✅ Intent Classifier testowany dla PL i EN
5. ✅ Edge cases nie powodują crashów
6. ✅ Łączne pokrycie testów E2E > 55

---

## Documentation Updates

Po zakończeniu:
- [ ] `_docs/_CHANGELOG/79-YYYY-MM-DD-router-e2e-coverage.md` - changelog
- [ ] `_docs/_TASKS/README.md` - update status
- [ ] `_docs/_ROUTER/README.md` - update test coverage info
