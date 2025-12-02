# 78 - Router E2E Test Fixes

**Data:** 2025-12-02
**TASK:** TASK-039 (Router Supervisor Implementation)
**Status:** Done

## Problem

Po implementacji Router Supervisor, 6 testów E2E nie przechodziło z powodu kilku różnych błędów:

1. **Błędny parametr RPC** - testy używały `{"type": "CUBE"}` zamiast `{"primitive_type": "CUBE"}`
2. **Błędny dostęp do ProportionInfo** - testy używały `.get()` (metoda dict) na dataclass
3. **Błędne oczekiwania wzorców** - test szukał "flat" w nazwach wzorców, ale taki wzorzec nie istnieje
4. **Błędny logger w teście telemetrii** - test używał globalnego singletona zamiast loggera routera

## Naprawy

### 1. Parametr RPC `primitive_type`

**Problem:** `ModelingHandler.create_primitive()` oczekuje `primitive_type`, nie `type`

**Pliki:**
- `tests/e2e/router/test_pattern_detection.py`
- `tests/e2e/router/test_full_pipeline.py`
- `tests/e2e/router/test_router_scenarios.py`
- `tests/e2e/router/test_workflow_execution.py`

**Zmiana:**
```python
# Przed
rpc_client.send_request("modeling.create_primitive", {"type": "CUBE"})

# Po
rpc_client.send_request("modeling.create_primitive", {"primitive_type": "CUBE"})
```

### 2. Dostęp do atrybutów ProportionInfo

**Problem:** `ProportionInfo` to dataclass, nie dict - nie ma metody `.get()`

**Plik:** `tests/e2e/router/test_pattern_detection.py:124-153`

**Zmiana:**
```python
# Przed
context.proportions.get("is_flat", False)
context.proportions.get("aspect_xz", 1)
context.proportions.get("is_tall", False)
context.proportions.get("dominant_axis")

# Po
context.proportions.is_flat
context.proportions.aspect_xz
context.proportions.is_tall
context.proportions.dominant_axis
```

**Dodatkowa zmiana:** Dodano fallback gdy wymiary zwracają domyślne [1,1,1] (Blender rozróżnia scale od dimensions)

### 3. Oczekiwania wzorców dla płaskich obiektów

**Problem:** Test szukał wzorców zawierających "flat" lub "phone" w nazwie, ale:
- Nie ma wzorca `flat_like` - `is_flat` to tylko flaga boolean
- Wzorce wskazujące na płaskie obiekty to: `phone_like`, `table_like`, `wheel_like`

**Plik:** `tests/e2e/router/test_pattern_detection.py:46-51`

**Zmiana:**
```python
# Przed
has_flat = any("flat" in name.lower() for name in pattern_names)
has_phone = any("phone" in name.lower() for name in pattern_names)
assert has_flat or has_phone

# Po
flat_patterns = {"phone_like", "table_like", "wheel_like"}
has_flat_pattern = any(name in flat_patterns for name in pattern_names)
assert has_flat_pattern
```

### 4. Logger w teście telemetrii

**Problem:** `SupervisorRouter` tworzy własną instancję `RouterLogger()` (linia 90 w router.py), nie używa globalnego singletona `get_router_logger()`

**Plik:** `tests/e2e/router/test_full_pipeline.py:70-86`

**Zmiana:**
```python
# Przed
from server.router.infrastructure.logger import get_router_logger
logger = get_router_logger()
logger.clear_events()
events = logger.get_events()

# Po
router.logger.clear_events()
events = router.logger.get_events()
```

## Wynik

- **Przed:** 32 passed, 6 failed
- **Po:** 38 passed, 0 failed

## Lista zmienionych plików

| Plik | Typ zmiany |
|------|------------|
| `tests/e2e/router/test_pattern_detection.py` | Naprawiono parametr RPC, dostęp do ProportionInfo, oczekiwania wzorców |
| `tests/e2e/router/test_full_pipeline.py` | Naprawiono parametr RPC, logger telemetrii |
| `tests/e2e/router/test_router_scenarios.py` | Naprawiono parametr RPC |
| `tests/e2e/router/test_workflow_execution.py` | Naprawiono parametr RPC |
