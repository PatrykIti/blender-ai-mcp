# TASK-058: Loop System & String Interpolation for Workflows

## Overview

Rozszerzenie systemu workflow o **loop parameter** i **string interpolation** aby upraszczać złożone YAML definicje (jak `simple_table.yaml` z 15 powtarzającymi się plankami).

## Architektura Obecnie

### Pipeline Przetwarzania Workflow

```
YAML File
    ↓
WorkflowLoader._parse_step()          # Parsuje YAML → WorkflowStep
    ↓
WorkflowRegistry.expand_workflow()    # Główna metoda ekspansji
    ├── _build_variables()            # defaults + modifiers
    ├── resolve_computed_parameters() # TASK-056-5 (computed params)
    ├── _resolve_definition_params()  # $variable, $CALCULATE substitution
    └── _steps_to_calls()             # Walidacja condition, → CorrectedToolCall[]
```

### Kluczowe Pliki (Clean Architecture)

| Warstwa | Plik | Rola |
|---------|------|------|
| **Application/Workflows** | `server/router/application/workflows/base.py:17-136` | `WorkflowStep` dataclass (pola: tool, params, condition, loop?) |
| **Infrastructure** | `server/router/infrastructure/workflow_loader.py:300` | `_parse_step()` - parsowanie YAML → WorkflowStep |
| **Application/Evaluator** | `server/router/application/evaluator/expression_evaluator.py:57-60` | `$CALCULATE` patterns + `$variable` |
| **Application/Evaluator** | `server/router/application/evaluator/unified_evaluator.py:45` | Whitelist funkcji + AST core (TASK-060) |
| **Application/Workflows** | `server/router/application/workflows/registry.py:202` | `expand_workflow()` - główna ekspansja |
| **Application/Workflows** | `server/router/application/workflows/registry.py:541` | `_resolve_definition_params()` / `$CALCULATE` + `$variable` |
| **Application/Engines** | `server/router/application/engines/workflow_adapter.py` | `WorkflowAdapter` - filtrowanie optional steps |

---

## Propozycja Implementacji

### FAZA 1: Loop Expansion (P0 - Critical)

#### 1.1 Nowy `loop` Parameter w WorkflowStep

**Plik**: `server/router/application/workflows/base.py:17-95`

Dodać nowe pole do dataclass `WorkflowStep` (po linii 58, przed `def __post_init__`):

```python
@dataclass
class WorkflowStep:
    # ... existing fields (tool, params, description, condition, optional, etc.) ...

    # TASK-058: Loop parameter for step repetition
    loop: Optional[Dict[str, Any]] = None
```

**WAŻNE**: Dodać `"loop"` do `_known_fields` w `__post_init__()` (linia 69-74 w aktualnym kodzie):
```python
self._known_fields = {
    "tool", "params", "description", "condition",
    "optional", "disable_adaptation", "tags",
    "id", "depends_on", "timeout", "max_retries",
    "retry_delay", "on_failure", "priority",
    "loop"  # TASK-058: NEW
}
```

**Loop Schema**:
```yaml
loop:
  variable: "i"                    # Loop variable name
  range: "1..plank_count"          # Range expression (computed at runtime)
  # LUB:
  range: [1, 15]                   # Static range [start, end]
```

#### 1.2 LoopExpander - NOWY PLIK (Application Layer)

**Plik**: `server/router/application/evaluator/loop_expander.py` (NEW FILE)

> **Clean Architecture**: `LoopExpander` to logika aplikacyjna (transformacja danych),
> więc należy do warstwy `application/evaluator/` obok `expression_evaluator.py`.

```python
"""
Loop Expander for Workflow Steps.

Expands loop steps into multiple concrete steps.
TASK-058: Loop System for Workflows.
"""

import copy
import logging
import re
from typing import Dict, Any, List, Tuple, Optional

from server.router.application.workflows.base import WorkflowStep
from server.router.application.evaluator.expression_evaluator import ExpressionEvaluator

logger = logging.getLogger(__name__)


class LoopExpander:
    """Expands loop steps into multiple concrete steps.

    Handles:
    - Static ranges: [1, 15]
    - Dynamic ranges: "1..plank_count" (resolved from context)
    - Loop variable injection into step params and description
    """

    # Pattern for range expression: "start..end" where start/end can be int or variable
    RANGE_PATTERN = re.compile(r"^(\d+|[a-zA-Z_][a-zA-Z0-9_]*)\.\.(\d+|[a-zA-Z_][a-zA-Z0-9_]*)$")

    def __init__(self, evaluator: Optional[ExpressionEvaluator] = None):
        """Initialize loop expander.

        Args:
            evaluator: ExpressionEvaluator for resolving range expressions.
                      If None, creates new instance.
        """
        self._evaluator = evaluator or ExpressionEvaluator()

    def expand_loops(
        self,
        steps: List[WorkflowStep],
        context: Dict[str, Any]
    ) -> List[WorkflowStep]:
        """Expand all loop steps into concrete steps.

        Args:
            steps: List of workflow steps (may contain loop steps).
            context: Variable context for range resolution.

        Returns:
            List of expanded steps (loop steps replaced with multiple concrete steps).
        """
        expanded = []
        for step in steps:
            if step.loop:
                loop_steps = self._expand_single_loop(step, context)
                expanded.extend(loop_steps)
                logger.debug(
                    f"Expanded loop step '{step.tool}' into {len(loop_steps)} steps"
                )
            else:
                expanded.append(step)
        return expanded

    def _expand_single_loop(
        self,
        step: WorkflowStep,
        context: Dict[str, Any]
    ) -> List[WorkflowStep]:
        """Expand single loop step into multiple concrete steps.

        Args:
            step: Workflow step with loop configuration.
            context: Variable context for range resolution.

        Returns:
            List of expanded steps.

        Raises:
            ValueError: If loop configuration is invalid.
        """
        loop_config = step.loop
        if not loop_config:
            return [step]

        # Extract loop variable name
        var_name = loop_config.get("variable")
        if not var_name:
            raise ValueError(f"Loop step missing 'variable' in loop config: {step.tool}")

        # Resolve range
        range_spec = loop_config.get("range")
        if range_spec is None:
            raise ValueError(f"Loop step missing 'range' in loop config: {step.tool}")

        start, end = self._resolve_range(range_spec, context)

        # Generate expanded steps
        expanded = []
        for i in range(int(start), int(end) + 1):
            # Create loop context with current iteration variable
            loop_context = {**context, var_name: i}
            new_step = self._clone_step_with_loop_var(step, var_name, i, loop_context)
            expanded.append(new_step)

        return expanded

    def _resolve_range(
        self,
        range_spec: Any,
        context: Dict[str, Any]
    ) -> Tuple[int, int]:
        """Resolve range specification to (start, end) tuple.

        Args:
            range_spec: Range as [start, end] list or "start..end" string.
            context: Variable context for expression resolution.

        Returns:
            Tuple of (start, end) integers.

        Raises:
            ValueError: If range specification is invalid.
        """
        # Static range: [1, 15]
        if isinstance(range_spec, (list, tuple)):
            if len(range_spec) != 2:
                raise ValueError(f"Range list must have exactly 2 elements: {range_spec}")
            return int(range_spec[0]), int(range_spec[1])

        # Dynamic range: "1..plank_count" or "0..15"
        if isinstance(range_spec, str):
            match = self.RANGE_PATTERN.match(range_spec)
            if not match:
                raise ValueError(f"Invalid range expression: {range_spec}")

            start_str, end_str = match.groups()

            # Resolve start
            if start_str.isdigit():
                start = int(start_str)
            elif start_str in context:
                start = int(context[start_str])
            else:
                raise ValueError(f"Unknown variable in range start: {start_str}")

            # Resolve end
            if end_str.isdigit():
                end = int(end_str)
            elif end_str in context:
                end = int(context[end_str])
            else:
                raise ValueError(f"Unknown variable in range end: {end_str}")

            return start, end

        raise ValueError(f"Unsupported range type: {type(range_spec)}")

    def _clone_step_with_loop_var(
        self,
        step: WorkflowStep,
        var_name: str,
        var_value: int,
        loop_context: Dict[str, Any]
    ) -> WorkflowStep:
        """Clone step with loop variable substituted.

        Args:
            step: Original step to clone.
            var_name: Loop variable name (e.g., "i").
            var_value: Current loop iteration value.
            loop_context: Full context including loop variable.

        Returns:
            New WorkflowStep with loop variable substituted in params.
        """
        # Deep copy params to avoid mutating original
        new_params = self._substitute_loop_var_in_params(
            copy.deepcopy(step.params),
            var_name,
            var_value
        )

        # Substitute in description if present
        new_description = step.description
        if new_description:
            new_description = new_description.replace(f"{{{var_name}}}", str(var_value))

        # Create new step WITHOUT loop (expanded step is concrete)
        return WorkflowStep(
            tool=step.tool,
            params=new_params,
            description=new_description,
            condition=step.condition,
            optional=step.optional,
            disable_adaptation=step.disable_adaptation,
            tags=list(step.tags),
            id=f"{step.id}_{var_value}" if step.id else None,
            depends_on=list(step.depends_on),
            timeout=step.timeout,
            max_retries=step.max_retries,
            retry_delay=step.retry_delay,
            on_failure=step.on_failure,
            priority=step.priority,
            loop=None  # Expanded step has no loop
        )

    def _substitute_loop_var_in_params(
        self,
        params: Dict[str, Any],
        var_name: str,
        var_value: int
    ) -> Dict[str, Any]:
        """Substitute loop variable in params (recursive).

        Handles {var_name} placeholders in string values.

        Args:
            params: Parameters dictionary.
            var_name: Loop variable name.
            var_value: Current loop iteration value.

        Returns:
            New params dict with substituted values.
        """
        result = {}
        for key, value in params.items():
            result[key] = self._substitute_in_value(value, var_name, var_value)
        return result

    def _substitute_in_value(
        self,
        value: Any,
        var_name: str,
        var_value: int
    ) -> Any:
        """Substitute loop variable in a single value.

        Args:
            value: Value to process.
            var_name: Loop variable name.
            var_value: Current loop iteration value.

        Returns:
            Processed value with substitutions.
        """
        if isinstance(value, str):
            # Replace {i} with actual value
            return value.replace(f"{{{var_name}}}", str(var_value))
        elif isinstance(value, list):
            return [self._substitute_in_value(v, var_name, var_value) for v in value]
        elif isinstance(value, dict):
            return {k: self._substitute_in_value(v, var_name, var_value) for k, v in value.items()}
        else:
            return value
```

#### 1.3 String Interpolation: `$FORMAT(...)`

**Plik**: `server/router/application/evaluator/expression_evaluator.py:57-60`

Dodać nowy pattern (obok `CALCULATE_PATTERN` i `VARIABLE_PATTERN`) i metodę:

```python
# Pattern for $FORMAT(...) string interpolation (TASK-058)
FORMAT_PATTERN = re.compile(r"^\$FORMAT\((.+)\)$")
```

Dodać nową metodę w klasie `ExpressionEvaluator`:

```python
def resolve_format(self, template: str) -> str:
    """Resolve $FORMAT(Plank_{i}) to concrete string.

    TASK-058: String interpolation for loop-generated names.

    Args:
        template: String with $FORMAT(...) wrapper.

    Returns:
        Resolved string with {var} placeholders replaced,
        or original string if not a $FORMAT expression.

    Example:
        context = {"i": 3}
        resolve_format("$FORMAT(Plank_{i})") -> "Plank_3"
    """
    match = self.FORMAT_PATTERN.match(template)
    if not match:
        return template

    format_str = match.group(1)
    # Replace {var} with current evaluator context (TASK-060: stored in UnifiedEvaluator)
    result = format_str
    for var_name, value in self._unified.get_context().items():
        result = result.replace(f"{{{var_name}}}", str(value))

    return result
```

**WAŻNE**: Zmodyfikować `resolve_param_value()` (linia 168-205 w aktualnym kodzie) aby obsługiwał `$FORMAT`:

```python
def resolve_param_value(self, value: Any) -> Any:
    """Resolve a parameter value, evaluating $CALCULATE or $FORMAT if present.
    ...
    """
    if not isinstance(value, str):
        return value

    # Check for $FORMAT(...) - TASK-058
    format_match = self.FORMAT_PATTERN.match(value)
    if format_match:
        return self.resolve_format(value)

    # Check for $CALCULATE(...)
    calc_match = self.CALCULATE_PATTERN.match(value)
    # ... rest of existing code ...
```

#### 1.4 Integracja w WorkflowRegistry

**Plik**: `server/router/application/workflows/registry.py:34-41`

**Krok 1**: Dodać import na początku pliku (po linii 22, obok innych importów z evaluator):

```python
from server.router.application.evaluator.loop_expander import LoopExpander
```

**Krok 2**: Dodać `_loop_expander` w `__init__()` (linia 34-41 w aktualnym kodzie, po linii 41):

```python
def __init__(self):
    """Initialize registry with workflows from YAML/JSON files."""
    self._workflows: Dict[str, BaseWorkflow] = {}
    self._custom_definitions: Dict[str, WorkflowDefinition] = {}
    self._custom_loaded: bool = False
    self._evaluator = ExpressionEvaluator()
    self._condition_evaluator = ConditionEvaluator()
    self._proportion_resolver = ProportionResolver()
    self._loop_expander = LoopExpander(self._evaluator)  # TASK-058: NEW
```

**Krok 3**: W `expand_workflow()` (linia 289-295 w aktualnym kodzie) dodać loop expansion PRZED `_resolve_definition_params()`:

```python
# Try custom definition
definition = self._custom_definitions.get(workflow_name)
if definition:
    # Build variable context from defaults + modifiers (TASK-052)
    variables = self._build_variables(definition, user_prompt)
    # Merge with params (params override variables)
    all_params = {**variables, **(params or {})}

    # TASK-055-FIX-7 Phase 0: Resolve computed parameters
    if definition.parameters:
        # ... existing computed params code ...

    # Set evaluator context with all resolved parameters
    self._evaluator.set_context(all_params)

    # TASK-058: Expand loop steps BEFORE other processing
    expanded_steps = self._loop_expander.expand_loops(
        definition.steps,
        all_params  # Contains plank_count, etc.
    )

    steps = self._resolve_definition_params(expanded_steps, all_params)
    return self._steps_to_calls(steps, workflow_name, workflow_params=all_params)
```

---

### ✅ Conditional Expressions w `$CALCULATE(...)` (Zrobione w TASK-060)

> **Zaimplementowane**: Operatory porównania (`<`, `<=`, `>`, `>=`, `==`, `!=`), operatory logiczne (`and`, `or`, `not`) oraz ternary expressions (`x if cond else y`) są dostępne po **TASK-060: Unified Expression Evaluator**.
>
> **Uwaga historyczna**: wcześniej było to wydzielone do TASK-059, ale TASK-059 jest oznaczony jako superseded przez TASK-060 i pozostaje tylko jako referencja:
> [TASK-059: Expression Evaluator - Logical & Comparison Operators](./TASK-059_Expression_Evaluator_Logical_Operators.md)

---

### FAZA 2: Nested Loops (P2 - Medium, Future)

Dla 2D grids (telefon z przyciskami 3x4):

```yaml
loop:
  variables: ["row", "col"]
  ranges: ["0..3", "0..4"]
```

---

## Przykład Po Implementacji

### simple_table.yaml (BEFORE - 200+ linii)

```yaml
steps:
  # Plank 1
  - tool: modeling_create_primitive
    params:
      name: "TablePlank_1"
  - tool: modeling_transform_object
    params:
      name: "TablePlank_1"
      location: ["$CALCULATE(-table_width/2 + plank_actual_width * 0.5)", ...]

  # Plank 2 (condition: plank_count >= 2)
  - tool: modeling_create_primitive
    params:
      name: "TablePlank_2"
    condition: "plank_count >= 2"
  # ... repeat for 15 planks ...
```

### simple_table.yaml (AFTER - ~30 linii)

```yaml
steps:
  # All planks via loop
  - tool: modeling_create_primitive
    params:
      name: "$FORMAT(TablePlank_{i})"
    loop:
      variable: "i"
      range: "1..plank_count"
    description: "Create table plank {i}"

  - tool: modeling_transform_object
    params:
      name: "$FORMAT(TablePlank_{i})"
      scale: ["$CALCULATE(plank_actual_width / 2)", "$CALCULATE(table_length / 2)", 0.0114]
      location: ["$CALCULATE(-table_width/2 + plank_actual_width * (i - 0.5))", 0, "$CALCULATE(leg_length + 0.0114)"]
    loop:
      variable: "i"
      range: "1..plank_count"
    description: "Position plank {i}"
```

---

## Pliki Do Modyfikacji (Clean Architecture)

### Faza 1 (Loop + String Interpolation)

| Warstwa | Plik | Zmiana | Priorytet |
|---------|------|--------|-----------|
| **Application/Workflows** | `server/router/application/workflows/base.py` | Dodać `loop: Optional[Dict]` do `WorkflowStep`, dodać `"loop"` do `_known_fields` | P0 |
| **Infrastructure** | `server/router/infrastructure/workflow_loader.py` | Automatyczna obsługa `loop` przez istniejący `_parse_step()` (bez zmian) | P0 |
| **Application/Evaluator** | `server/router/application/evaluator/loop_expander.py` | **NOWY PLIK**: `LoopExpander` class | P0 |
| **Application/Evaluator** | `server/router/application/evaluator/__init__.py` | Dodać eksport `LoopExpander` do `__all__` | P0 |
| **Application/Evaluator** | `server/router/application/evaluator/expression_evaluator.py` | Dodać `FORMAT_PATTERN`, `resolve_format()`, zmodyfikować `resolve_param_value()` | P0 |
| **Application/Workflows** | `server/router/application/workflows/registry.py` | Import `LoopExpander`, dodać `_loop_expander`, integracja w `expand_workflow()` | P0 |
| **Custom Workflows** | `server/router/application/workflows/custom/simple_table.yaml` | Przepisać na loop syntax (opcjonalne w Fazie 1) | P0 |

### ✅ Conditional Expressions (już dostępne)

> Funkcjonalność porównań/logiki/ternary w `$CALCULATE(...)` jest dostępna po TASK-060. W ramach TASK-058 nie trzeba tu nic implementować.

---

## Testy (Clean Architecture)

### Unit Tests

```
tests/unit/router/application/evaluator/test_loop_expander.py
- test_expand_static_range
- test_expand_computed_range
- test_expand_dynamic_range_with_variables
- test_format_string_interpolation_in_params
- test_no_loop_passthrough
- test_invalid_loop_config_raises_error
- test_nested_loops (FAZA 3 - skip dla teraz)

tests/unit/router/application/evaluator/test_expression_evaluator_format.py
- test_format_pattern_simple
- test_format_pattern_multiple_vars
- test_format_not_matched_returns_original
- test_resolve_param_value_with_format
```

### E2E Tests

```
tests/e2e/router/test_simple_table_with_loops.py
- test_table_with_8_planks_via_loop
- test_table_width_0_73m_fractional_planks
- test_loop_expansion_in_registry
```

---

## Kolejność Implementacji (Clean Architecture)

### Faza 1 - Core Loop System

| Krok | Warstwa | Plik | Opis |
|------|---------|------|------|
| 1 | Application/Workflows | `base.py` | Dodać `loop: Optional[Dict]` do `WorkflowStep` + `_known_fields` |
| 2 | Infrastructure | `workflow_loader.py` | Weryfikacja - pole `loop` parsowane automatycznie (bez zmian) |
| 3 | Application/Evaluator | `loop_expander.py` | **NOWY PLIK** - `LoopExpander` class |
| 4 | Application/Evaluator | `__init__.py` | Dodać import i eksport `LoopExpander` do `__all__` |
| 5 | Application/Evaluator | `expression_evaluator.py` | Dodać `FORMAT_PATTERN` + `resolve_format()` + zmodyfikować `resolve_param_value()` |
| 6 | Application/Workflows | `registry.py` | Import + instancja `_loop_expander` + integracja w `expand_workflow()` |
| 7 | Tests | `test_loop_expander.py` | Unit testy dla `LoopExpander` |
| 8 | Tests | `test_expression_evaluator_format.py` | Unit testy dla `$FORMAT` |
| 9 | Custom Workflows | `simple_table.yaml` | Refaktor na loop syntax (opcjonalnie) |

### ✅ Faza 2 - Conditional Expressions (zamknięte przez TASK-060)

> Brak prac w TASK-058 (zrobione w TASK-060).

---

## Decyzje Architektoniczne

1. **Loop range syntax**: `"1..plank_count"` - spójna z innymi DSL, czytelna
2. **String interpolation**: `$FORMAT(Plank_{i})` - spójna z istniejącym `$CALCULATE()`
3. **LoopExpander lokalizacja**: `application/evaluator/` - logika transformacji danych (nie infrastructure)
4. **Nested loops**: FAZA 3 (przyszłość) - podstawowe pętle w FAZA 1

### `$FORMAT` vs `$CALCULATE` - różnice

| Aspekt | `$CALCULATE(...)` | `$FORMAT(...)` |
|--------|-------------------|----------------|
| **Cel** | Obliczenia matematyczne | Interpolacja stringów |
| **Zwraca** | `float` / `int` | `string` |
| **Użycie** | `location`, `scale`, `rotation` | `name`, `material_name` |
| **Przykład** | `$CALCULATE(width / 2)` → `0.4` | `$FORMAT(Plank_{i})` → `"Plank_3"` |
| **Obsługuje** | Arytmetyka, funkcje math | Placeholder `{zmienna}` |

**WAŻNE**: `$FORMAT` i `$CALCULATE` są **wzajemnie wykluczające się** - oba patterny matchują cały string (`^...$`). Nie można ich zagnieżdżać:

```yaml
# ❌ NIE MOŻNA:
name: "$FORMAT(Plank_$CALCULATE(i + 1))"

# ✅ MOŻNA (loop variable podstawiana przed $FORMAT):
name: "$FORMAT(Plank_{i})"
```

Kolejność przetwarzania w pipeline:
1. `LoopExpander` podstawia `{i}` → wartość (np. `3`)
2. `ExpressionEvaluator.resolve_param_value()` sprawdza `$FORMAT` → zwraca string
3. Lub sprawdza `$CALCULATE` → zwraca liczbę

---

## Znany Dług Techniczny

### `_resolve_definition_params()` w registry.py (linia 539-579)

Istniejąca metoda **nie przekazuje wszystkich pól** `WorkflowStep` przy tworzeniu resolved steps:

```python
# AKTUALNA IMPLEMENTACJA (registry.py:570-577):
resolved_steps.append(
    WorkflowStep(
        tool=step.tool,
        params=resolved_params,
        description=step.description,
        condition=step.condition,  # Tylko te 4 pola!
    )
)
```

**Brakujące pola**: `optional`, `disable_adaptation`, `tags`, `id`, `depends_on`, `timeout`, `max_retries`, `retry_delay`, `on_failure`, `priority`

**Rekomendacja**: Przy okazji TASK-058 naprawić ten dług - metoda `_clone_step_with_loop_var()` w `LoopExpander` już poprawnie przekazuje wszystkie pola.

---

## Szacowany Czas Implementacji

| Krok | Czas |
|------|------|
| `WorkflowStep.loop` + `_known_fields` | 5 min |
| Loop parsing verification | 0 min (automatyczne) |
| `LoopExpander` class | 30 min |
| `__init__.py` update | 2 min |
| `$FORMAT` pattern + `resolve_format()` | 15 min |
| Registry integration | 10 min |
| Fix `_resolve_definition_params()` (dług techniczny) | 5 min |
| Unit tests (`LoopExpander`) | 20 min |
| Unit tests (`$FORMAT`) | 10 min |
| `simple_table.yaml` refaktor (opcjonalne) | 15 min |
| **TOTAL TASK-058** | **~2h** |

> **Uwaga**: Conditional expressions (ternary, porównania, operatory logiczne) są już dostępne po **TASK-060**, więc nie zwiększają scope TASK-058.

---

## Weryfikacja Zgodności z Kodem (2025-12-12)

### ✅ Zweryfikowane Lokalizacje Plików

| Element | Ścieżka w TASK-058 | Status |
|---------|-------------------|--------|
| `WorkflowStep` | `server/router/application/workflows/base.py` | ✅ Poprawna |
| `ExpressionEvaluator` | `server/router/application/evaluator/expression_evaluator.py` | ✅ Poprawna |
| `WorkflowRegistry` | `server/router/application/workflows/registry.py` | ✅ Poprawna |
| `workflow_loader` | `server/router/infrastructure/workflow_loader.py` | ✅ Poprawna |
| `evaluator/__init__.py` | `server/router/application/evaluator/__init__.py` | ✅ Poprawna |

### ✅ Zweryfikowane Numery Linii

| Element | Linie w TASK-058 | Aktualne linie | Status |
|---------|-----------------|----------------|--------|
| `WorkflowStep` dataclass | 17-95 | 17-136 | ✅ OK (rozszerzono) |
| `_known_fields` | 69-74 | 69-74 | ✅ Dokładnie |
| `CALCULATE_PATTERN` | 83-87 | 57 | ✅ OK |
| `VARIABLE_PATTERN` | 87 | 60 | ✅ OK |
| `resolve_param_value()` | 168-205 | 158-191 | ✅ OK |
| `_eval_node()` | 262-336 | `unified_evaluator.py:231` | ✅ Przeniesione w TASK-060 |
| `expand_workflow()` | 202-297 | 202-297 | ✅ Dokładnie |
| `_resolve_definition_params()` | 539-632 | 541 | ✅ OK |
| `_parse_step()` | 300-350 | 300-350 | ✅ OK |

### ✅ Zgodność z Clean Architecture

| Aspekt | Ocena |
|--------|-------|
| `LoopExpander` w `application/evaluator/` | ✅ Poprawna warstwa (logika aplikacyjna) |
| Dependency direction | ✅ Inner → Outer |
| Separation of concerns | ✅ Transformacja danych oddzielona od I/O |

### 📝 Ilustracja Zmian

#### Zmiana 1: `_known_fields` w WorkflowStep

**PRZED** (`base.py:69-74`):
```python
self._known_fields = {
    "tool", "params", "description", "condition",
    "optional", "disable_adaptation", "tags",
    "id", "depends_on", "timeout", "max_retries",
    "retry_delay", "on_failure", "priority"
}
```

**PO** (TASK-058):
```python
self._known_fields = {
    "tool", "params", "description", "condition",
    "optional", "disable_adaptation", "tags",
    "id", "depends_on", "timeout", "max_retries",
    "retry_delay", "on_failure", "priority",
    "loop"  # TASK-058: NEW
}
```

#### Zmiana 2: Integracja w `expand_workflow()`

**PRZED** (`registry.py:289-295`):
```python
# Set evaluator context with all resolved parameters
self._evaluator.set_context(all_params)

steps = self._resolve_definition_params(definition.steps, all_params)
return self._steps_to_calls(steps, workflow_name, workflow_params=all_params)
```

**PO** (TASK-058):
```python
# Set evaluator context with all resolved parameters
self._evaluator.set_context(all_params)

# TASK-058: Expand loop steps BEFORE other processing
expanded_steps = self._loop_expander.expand_loops(
    definition.steps,
    all_params  # Contains plank_count, etc.
)

steps = self._resolve_definition_params(expanded_steps, all_params)
return self._steps_to_calls(steps, workflow_name, workflow_params=all_params)
```

### ✅ Potwierdzenie Automatycznej Obsługi `loop` w WorkflowLoader

Metoda `_parse_step()` (`workflow_loader.py:323-340`) używa dynamicznego ładowania pól:

```python
step_fields = {f.name: f for f in dataclasses.fields(WorkflowStep)}
step_data = {}
for field_name, field_info in step_fields.items():
    if field_name in data:
        step_data[field_name] = data[field_name]
    # ... defaults handling
```

Po dodaniu `loop: Optional[Dict[str, Any]] = None` do `WorkflowStep` dataclass, pole `loop` będzie **automatycznie parsowane** z YAML bez zmian w `workflow_loader.py`.

### 🎯 Podsumowanie Weryfikacji

| Kategoria | Status |
|-----------|--------|
| Ścieżki plików | ✅ 100% zgodne |
| Numery linii | ✅ Zaktualizowane po TASK-060 |
| Clean Architecture | ✅ Przestrzegana |
| Dług techniczny | ✅ Poprawnie zidentyfikowany |
| Kolejność implementacji | ✅ Sensowna |

**TASK-058 jest zgodny z aktualnym kodem po TASK-060 i może być implementowany bez zmian w architekturze.**

---

## Related Tasks

| Task | Relacja | Opis |
|------|---------|------|
| **TASK-060** | **Odblokowuje** | Porównania/logika/ternary w `$CALCULATE` + math w `condition` (już zaimplementowane) |
| TASK-059 | Superseded | Pozostawiony jako referencja (zastąpiony przez TASK-060) |
| TASK-056-1 | Prerequisite | Extended Expression Evaluator (22 funkcje math) |
| TASK-056-5 | Prerequisite | Computed Parameters |
| TASK-055-FIX-8 | Documentation | Dokumentacja funkcji expression evaluator |

> **Kolejność implementacji**: TASK-060 (✅) → TASK-058 (Loop System) → pełna funkcjonalność dynamicznych workflow
