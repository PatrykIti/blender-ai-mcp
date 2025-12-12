# TASK-058: Loop System & String Interpolation for Workflows

## Overview

Rozszerzenie systemu workflow o **loops** i **string interpolation** tak, aby nawet złożone workflow (meble/urządzenia/makiety) dało się opisać krótko i parametrycznie (np. `simple_table.yaml` bez 15 ręcznie powielonych desek).

Kluczowe założenie: **nic nie może “omijać pipeline”** (szczególnie adaptacja z TASK-051). Loops/interpolacja muszą działać identycznie w ścieżce standardowej i adaptacyjnej.

---

## Założenia DSL (TASK-058)

### 1) String interpolation: `{var}` (MUST)

- Placeholdery `{var}` są podmieniane w **każdym stringu workflow**: `params`, `description`, `condition`, `id`, `depends_on` (+ opcjonalnie w dynamic attrs).
- Interpolacja jest uruchamiana **przed** `$CALCULATE/$AUTO_/$variable` i przed ewaluacją `condition`, dzięki czemu `{i}` może pojawić się wewnątrz `$CALCULATE(...)` i `condition`.
- Interpolacja jest wspólna dla loopów i “normalnych” kroków (to nie jest tylko feature pętli).
- Escaping: `{{` i `}}` oznaczają literalne `{` i `}` (bez interpolacji).
- Brak `$FORMAT(...)` w core DSL. Jedna składnia `{var}` upraszcza authoring i automatycznie wspiera nested loops.

### 2) Loops: `loop` (MUST)

Loop jest konfigurowany na poziomie kroku (`WorkflowStep.loop`) i rozwijany przez `LoopExpander`.

Obsługiwane warianty:

**A. Pojedyncza zmienna:**
```yaml
loop:
  variable: i
  range: "1..plank_count"   # inclusive
```

**B. Nested loops (wiele zmiennych, cross‑product):**
```yaml
loop:
  variables: [row, col]
  ranges: ["0..3", "0..4"]
```

**C. Iteracja po wartościach (opcjonalnie, ale bardzo przydatne):**
```yaml
loop:
  variable: side
  values: ["L", "R"]
```

### 3) Kolejność wykonania w pętli: `loop.group` (MUST)

Domyślnie loop ekspanduje “krok po kroku” (najpierw cały loop dla kroku A, potem cały loop dla kroku B).

Żeby uzyskać poprawną kolejność per‑iteracja (np. `create_i → transform_i → edit_i`), kroki mogą mieć wspólny:
```yaml
loop:
  group: planks
  variable: i
  range: "1..plank_count"
```

`LoopExpander` interleavuje (zipuje) ekspansję *kolejnych, sąsiadujących* kroków o tym samym `loop.group` i tej samej przestrzeni iteracji.

### 4) Bezpieczniki (MUST)

- `LoopExpander` ma limit maksymalnej liczby wygenerowanych kroków (ochrona przed przypadkowym `1..100000`).
- Interpolacja jest strict: jeśli w stringu występuje `{var}`, a `var` nie istnieje w kontekście → błąd (żeby uniknąć “fail‑open” w `condition`).

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
    ├── LoopExpander.expand()         # TASK-058 (loop expansion + {var} interpolation)
    ├── _resolve_definition_params()  # $variable, $CALCULATE substitution
    └── _steps_to_calls()             # Walidacja condition, → CorrectedToolCall[]
```

### ⚠️ Krytyczne: Adaptacja (TASK-051) obecnie omija pipeline

W momencie gdy workflow adaptacja jest włączona (`TASK-051`) router ma osobną ścieżkę, która **nie** używa `WorkflowRegistry.expand_workflow()` i przez to omija kluczowe elementy pipeline.

**Obecne zachowanie (BUG):** `server/router/application/router.py:_expand_triggered_workflow()` w gałęzi `should_adapt == True`:
- nie uruchamia computed params (`resolve_computed_parameters()` w registry),
- nie rozwiązuje `$CALCULATE(...)` i `$AUTO_*`,
- nie odpala `condition` + `simulate_step_effect()` (czyli conditional steps przestają działać),
- tym samym będzie też omijać loop system z TASK-058.

**Wymóg TASK-058:** adaptacja ma być tylko filtrem kroków (core vs optional), a **reszta** ekspansji musi iść tą samą ścieżką co standardowa ekspansja w registry.

### Kluczowe Pliki (Clean Architecture)

| Warstwa | Plik | Rola |
|---------|------|------|
| **Application/Workflows** | `server/router/application/workflows/base.py:17-136` | `WorkflowStep` dataclass (pola: tool, params, condition, loop?) |
| **Infrastructure** | `server/router/infrastructure/workflow_loader.py:300` | `_parse_step()` - parsowanie YAML → WorkflowStep |
| **Application/Evaluator** | `server/router/application/evaluator/expression_evaluator.py:57-60` | `$CALCULATE` patterns + `$variable` |
| **Application/Evaluator** | `server/router/application/evaluator/unified_evaluator.py:45` | Whitelist funkcji + AST core (TASK-060) |
| **Application/Workflows** | `server/router/application/workflows/registry.py:202` | `expand_workflow()` - główna ekspansja |
| **Application/Workflows** | `server/router/application/workflows/registry.py:541` | `_resolve_definition_params()` / `$CALCULATE` + `$variable` |
| **Application/Router** | `server/router/application/router.py:433` | `_expand_triggered_workflow()` - ścieżka adaptacji (TASK-051) |
| **Application/Engines** | `server/router/application/engines/workflow_adapter.py` | `WorkflowAdapter` - filtrowanie optional steps |

---

## Propozycja Implementacji

## Definition of Done (Akceptacja)

- [ ] Adaptacja (TASK-051) nie omija pipeline: computed params, `$CALCULATE`, `$AUTO_*`, `condition` + `simulate_step_effect()` oraz loops/interpolacja działają identycznie jak bez adaptacji.
- [ ] `WorkflowRegistry.expand_workflow()` przyjmuje `steps_override` i wykorzystuje je jako źródło kroków (wspólna ścieżka dla adaptacji).
- [ ] `loop` w YAML jest parsowany automatycznie przez `WorkflowLoader` (bez zmian w loaderze).
- [ ] `LoopExpander` wspiera: `range` (inclusive), `values`, nested loops (`variables`+`ranges`) oraz `loop.group` (interleaving).
- [ ] String interpolation `{var}` działa w: `params`, `description`, `condition`, `id`, `depends_on` (+ dynamic attrs jeśli są typu str/list/dict).
- [ ] Interpolacja jest uruchamiana przed `$CALCULATE/$AUTO_/$variable` i przed ewaluacją `condition`.
- [ ] Loop expansion usuwa `loop` w krokach wynikowych (kroki po ekspansji są “konkretne”).
- [ ] `_resolve_definition_params()` zachowuje wszystkie pola `WorkflowStep` oraz dynamiczne atrybuty (nie gubi: `optional/tags/disable_adaptation/id/depends_on/...`).
- [ ] Limit maksymalnej liczby wygenerowanych kroków + błąd dla nieznanych placeholderów `{var}`.
- [ ] Testy: regresja adaptacji + unit testy loopów/interpolacji (+ test interleaving).

### FAZA 0: Naprawa adaptacji workflow (P0 - MUST)

**Cel:** Niezależnie od tego czy adaptacja jest włączona, workflow powinno przechodzić przez **ten sam** pipeline ekspansji co standard (`WorkflowRegistry.expand_workflow()`), żeby nie psuć:
- `condition` + symulacji kontekstu,
- `$CALCULATE(...)` / `$AUTO_*`,
- computed params,
- loopów (TASK-058).

#### 0.1 Zasada

1. Router wybiera `adapted_steps` (to jest jedyna logika adaptacji).
2. Następnie deleguje “całą resztę” (computed params, loop expansion, param resolution, condition evaluation) do `WorkflowRegistry`.

#### 0.2 Minimalna zmiana w API registry (rekomendowane)

Dodać opcjonalny parametr do `WorkflowRegistry.expand_workflow()`:

```python
def expand_workflow(
    self,
    workflow_name: str,
    params: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None,
    user_prompt: Optional[str] = None,
    steps_override: Optional[List[WorkflowStep]] = None,  # TASK-058/TASK-051: NEW
) -> List[CorrectedToolCall]:
    ...
```

W gałęzi “custom definition” używać:
```python
steps_source = steps_override if steps_override is not None else definition.steps
```

#### 0.3 Zmiana w router (TASK-051)

W gałęzi `should_adapt == True` w `server/router/application/router.py:_expand_triggered_workflow()` usunąć ręczne budowanie `CorrectedToolCall` i zastąpić je:

```python
calls = registry.expand_workflow(
    workflow_name,
    merged_params,
    eval_context,
    user_prompt=self._current_goal or "",
    steps_override=adapted_steps,  # <<<< klucz
)
```

**Akceptacja:** workflow z adaptacją ma identyczne wsparcie dla `$CALCULATE/$AUTO_/computed/condition` jak bez adaptacji (różni się tylko listą kroków).

### FAZA 1: Loops + String Interpolation (P0 - Critical)

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
  # A) Single variable range (inclusive)
  variable: i
  range: "1..plank_count"          # start/end mogą być liczbami, nazwami lub wyrażeniami
  # range: [1, 15]                 # alternatywnie: static [start, end]

  # (opcjonalnie) C) Iteracja po liście wartości (zamiast range)
  # values: ["L", "R"]

  # (opcjonalnie) Interleaving kolejnych kroków o tej samej pętli
  # group: "planks"

  # B) Nested loops (zamiast variable/range):
  # variables: [row, col]
  # ranges: ["0..(rows - 1)", "0..(cols - 1)"]
```

**Użycie zmiennej pętli w parametrach/warunkach (MUST):**

- LoopExpander robi **podstawienie placeholderów** w stringach: `{i}` → `3` (analogicznie `{row}`, `{col}`, `{side}`, itd.).
- Żeby użyć zmiennej pętli w `$CALCULATE(...)` lub `condition`, używaj zawsze **`{var}`**, nie gołego `var`.

Przykłady:
```yaml
params:
  name: "TablePlank_{i}"  # rekomendowane (bez $FORMAT)
  location:
    - "$CALCULATE(-table_width/2 + plank_actual_width * ({i} - 0.5))"
    - 0
    - "$CALCULATE(leg_length + 0.0114)"

condition: "{i} <= plank_count"
description: "Create plank {i}"
```

To jest krytyczne, bo bez dodatkowej logiki “wstrzykiwania i do kontekstu evaluatora” wyrażenie z samym `i` nie zadziała.

#### 1.2 LoopExpander - NOWY PLIK (Application Layer)

**Plik**: `server/router/application/evaluator/loop_expander.py` (NEW FILE)

> **Clean Architecture**: `LoopExpander` to logika aplikacyjna (transformacja danych),
> więc należy do warstwy `application/evaluator/` obok `expression_evaluator.py`.

```python
"""
LoopExpander (TASK-058).

Odpowiada za:
- ekspansję loopów (range/values, single + nested)
- string interpolation `{var}` (strict, z escapingiem {{ }})
- interleaving kroków z tym samym loop.group
- zachowanie pól WorkflowStep + dynamic attrs
"""

import dataclasses
import itertools
import logging
import re
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from server.router.application.evaluator.unified_evaluator import UnifiedEvaluator
from server.router.application.workflows.base import WorkflowStep

logger = logging.getLogger(__name__)


class LoopExpander:
    def __init__(self, max_expanded_steps: int = 2000):
        self._max_expanded_steps = max_expanded_steps
        self._evaluator = UnifiedEvaluator()

    def expand(self, steps: List[WorkflowStep], context: Dict[str, Any]) -> List[WorkflowStep]:
        """Expand loops + interpolate `{var}`.

        - Kroki bez loop: tylko interpolacja.
        - Kroki z loop bez group: ekspansja “krok po kroku”.
        - Kroki z tym samym loop.group (kolejne, sąsiadujące): interleaving per iteracja.
        """
        expanded: List[WorkflowStep] = []
        i = 0
        while i < len(steps):
            step = steps[i]
            loop_cfg = step.loop or {}

            group = loop_cfg.get("group")
            if group:
                block = self._consume_group_block(steps, i)
                expanded.extend(self._expand_group_block(block, context))
                i += len(block)
                continue

            expanded.extend(self._expand_step(step, context))
            i += 1

        if len(expanded) > self._max_expanded_steps:
            raise ValueError(
                f"Loop expansion produced {len(expanded)} steps "
                f"(limit={self._max_expanded_steps})."
            )
        return expanded

    def _expand_group_block(self, steps: Sequence[WorkflowStep], ctx: Dict[str, Any]) -> List[WorkflowStep]:
        # 1) zweryfikuj, że wszystkie kroki mają kompatybilny loop “iteration space”
        # 2) wygeneruj wszystkie iteracje (iter contexts)
        # 3) dla każdej iteracji: emituj kroki w kolejności z YAML (zip/interleave)
        ...

    def _expand_step(self, step: WorkflowStep, ctx: Dict[str, Any]) -> List[WorkflowStep]:
        if not step.loop:
            return [self._interpolate_step(step, ctx)]

        out: List[WorkflowStep] = []
        for iter_ctx in self._iter_loop_contexts(step.loop, ctx):
            concrete = self._clone_step(step, loop=None)
            out.append(self._interpolate_step(concrete, iter_ctx))
        return out

    def _iter_loop_contexts(self, loop_cfg: Dict[str, Any], ctx: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
        # Single variable + range
        if "variable" in loop_cfg and "range" in loop_cfg:
            var = loop_cfg["variable"]
            for v in self._resolve_range(loop_cfg["range"], ctx):
                yield {**ctx, var: v}
            return

        # Single variable + values
        if "variable" in loop_cfg and "values" in loop_cfg:
            var = loop_cfg["variable"]
            for v in loop_cfg["values"]:
                yield {**ctx, var: v}
            return

        # Nested loops
        if "variables" in loop_cfg and "ranges" in loop_cfg:
            vars_ = list(loop_cfg["variables"])
            ranges = [list(self._resolve_range(r, ctx)) for r in loop_cfg["ranges"]]
            for combo in itertools.product(*ranges):
                yield {**ctx, **dict(zip(vars_, combo))}
            return

        raise ValueError(f"Invalid loop config: {loop_cfg}")

    def _resolve_range(self, range_spec: Any, ctx: Dict[str, Any]) -> range:
        # [start, end]
        if isinstance(range_spec, (list, tuple)) and len(range_spec) == 2:
            start, end = range_spec
            return range(int(start), int(end) + 1)

        # "start..end" (inclusive) — start/end mogą być wyrażeniami
        if isinstance(range_spec, str) and ".." in range_spec:
            start_expr, end_expr = [p.strip() for p in range_spec.split("..", 1)]
            start = self._eval_int(start_expr, ctx)
            end = self._eval_int(end_expr, ctx)
            return range(start, end + 1)

        raise ValueError(f"Invalid range spec: {range_spec}")

    def _eval_int(self, expr: str, ctx: Dict[str, Any]) -> int:
        self._evaluator.set_context(ctx)
        return int(self._evaluator.evaluate_as_float(expr))

    def _interpolate_step(self, step: WorkflowStep, ctx: Dict[str, Any]) -> WorkflowStep:
        # Interpoluje: params/description/condition/id/depends_on + (opcjonalnie) dynamic attrs.
        ...

    def _clone_step(self, step: WorkflowStep, **overrides: Any) -> WorkflowStep:
        # Klonuje wszystkie pola dataclass + przenosi dynamic attrs.
        data = dataclasses.asdict(step)
        data.update(overrides)
        cloned = WorkflowStep(**{k: v for k, v in data.items() if k != "_known_fields"})

        # TODO: copy dynamic attrs (TASK-055-FIX-6 Phase 2)
        return cloned
```

#### 1.3 String interpolation: `{var}` (P0)

W TASK-058 **nie** dodajemy `$FORMAT(...)` — trzymamy jedną składnię `{var}`.

Implementacja: interpolacja jest częścią `LoopExpander.expand()` (działa dla kroków w pętli i poza pętlą).

Wymagania:
- wspiera escaping `{{`/`}}`,
- działa rekurencyjnie w `params` (list/dict),
- działa w `description`, `condition`, `id`, `depends_on`,
- jest strict: nieznany `{var}` → `ValueError`.

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
    self._loop_expander = LoopExpander()  # TASK-058: NEW
```

**Krok 3**: W `expand_workflow()` (linia 289-295 w aktualnym kodzie) dodać loop expansion PRZED `_resolve_definition_params()`:

```python
# Try custom definition
definition = self._custom_definitions.get(workflow_name)
if definition:
    steps_source = steps_override if steps_override is not None else definition.steps

    # Build variable context from defaults + modifiers (TASK-052)
    variables = self._build_variables(definition, user_prompt)
    # Merge with params (params override variables)
    all_params = {**variables, **(params or {})}

    # TASK-055-FIX-7 Phase 0: Resolve computed parameters
    if definition.parameters:
        # ... existing computed params code ...

    # Set evaluator context with all resolved parameters
    self._evaluator.set_context({**base_context, **all_params})

    # TASK-058: Loop expansion + {var} interpolation BEFORE other processing
    expanded_steps = self._loop_expander.expand(
        steps_source,
        {**base_context, **all_params}  # Includes plank_count + any other context
    )

    steps = self._resolve_definition_params(expanded_steps, all_params)
    return self._steps_to_calls(steps, workflow_name, workflow_params=all_params)
```

#### 1.5 Integracja loopów + param resolution z adaptacją (TASK-051)

Po wdrożeniu **FAZA 0** (steps_override), loop system będzie działał automatycznie także w adaptacji:
- adaptacja wybiera `adapted_steps`,
- registry robi: computed params → loop expansion → param resolution → `condition` + simulation.

To zamyka “split brain” pomiędzy ścieżką standardową i adaptacyjną.

---

### ✅ Conditional Expressions w `$CALCULATE(...)` (Zrobione w TASK-060)

> **Zaimplementowane**: Operatory porównania (`<`, `<=`, `>`, `>=`, `==`, `!=`), operatory logiczne (`and`, `or`, `not`) oraz ternary expressions (`x if cond else y`) są dostępne po **TASK-060: Unified Expression Evaluator**.
>
> **Uwaga historyczna**: wcześniej było to wydzielone do TASK-059, ale TASK-059 jest oznaczony jako superseded przez TASK-060 i pozostaje tylko jako referencja:
> [TASK-059: Expression Evaluator - Logical & Comparison Operators](./TASK-059_Expression_Evaluator_Logical_Operators.md)

---

### Nested Loops (P0 - część FAZY 1)

Nested loops są częścią core funkcjonalności (nie “future”), bo znacząco skracają workflow dla gridów (np. okna w elewacji, klawisze telefonu, moduły regału).

Przykład (grid 3x4):
```yaml
- tool: modeling_create_primitive
  params:
    name: "Button_{row}_{col}"
  loop:
    variables: [row, col]
    ranges: ["0..(rows - 1)", "0..(cols - 1)"]
    group: buttons
  description: "Create button r={row}, c={col}"
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
      name: "TablePlank_{i}"  # Rekomendowane (LoopExpander podstawi {i})
    loop:
      variable: "i"
      range: "1..plank_count"
      group: "planks"
    description: "Create table plank {i}"

  - tool: modeling_transform_object
    params:
      name: "TablePlank_{i}"
      scale: ["$CALCULATE(plank_actual_width / 2)", "$CALCULATE(table_length / 2)", 0.0114]
      location: ["$CALCULATE(-table_width/2 + plank_actual_width * ({i} - 0.5))", 0, "$CALCULATE(leg_length + 0.0114)"]
    loop:
      variable: "i"
      range: "1..plank_count"
      group: "planks"
    description: "Position plank {i}"
```

> **Tip (czytelność):** powtarzające się `loop:` łatwo skrócić YAML anchorami (`&`/`*`) i `<<` merge (PyYAML `safe_load` to wspiera).

---

## Pliki Do Modyfikacji (Clean Architecture)

### Faza 0 (Adaptacja nie omija pipeline - TASK-051)

| Warstwa | Plik | Zmiana | Priorytet |
|---------|------|--------|-----------|
| **Application/Workflows** | `server/router/application/workflows/registry.py` | Dodać `steps_override` do `expand_workflow()` i użyć jako źródło kroków dla custom workflows | P0 |
| **Application/Router** | `server/router/application/router.py` | W adaptacji wywołać `registry.expand_workflow(..., steps_override=adapted_steps)` zamiast ręcznie budować tool calle | P0 |

### Faza 1 (Loop + String Interpolation)

| Warstwa | Plik | Zmiana | Priorytet |
|---------|------|--------|-----------|
| **Application/Workflows** | `server/router/application/workflows/base.py` | Dodać `loop: Optional[Dict]` do `WorkflowStep`, dodać `"loop"` do `_known_fields`, uwzględnić `loop` w `to_dict()` | P0 |
| **Infrastructure** | `server/router/infrastructure/workflow_loader.py` | Automatyczna obsługa `loop` przez istniejący `_parse_step()` (bez zmian) | P0 |
| **Application/Evaluator** | `server/router/application/evaluator/loop_expander.py` | **NOWY PLIK**: `LoopExpander` class | P0 |
| **Application/Evaluator** | `server/router/application/evaluator/__init__.py` | Dodać eksport `LoopExpander` do `__all__` | P0 |
| **Application/Workflows** | `server/router/application/workflows/registry.py` | Import `LoopExpander`, dodać `_loop_expander`, integracja loop expansion w `expand_workflow()` (dla custom + `steps_override`) | P0 |
| **Application/Workflows** | `server/router/application/workflows/registry.py` | Naprawić `_resolve_definition_params()` żeby nie gubić pól kroku (optional/tags/depends_on/loop/dynamic attrs) | P0 |
| **Custom Workflows** | `server/router/application/workflows/custom/simple_table.yaml` | Przepisać na loop syntax (opcjonalne w Fazie 1) | P0 |
| **Docs** | `_docs/_ROUTER/WORKFLOWS/yaml-workflow-guide.md` | Dodać sekcję Loops + `{var}` interpolation | P0 |
| **Docs** | `_docs/_ROUTER/WORKFLOWS/creating-workflows-tutorial.md` | Dodać sekcję Loops + przykład refaktoru | P0 |
| **Docs** | `_docs/_ROUTER/WORKFLOWS/expression-reference.md` | Dodać `{var}` interpolation + kolejność pipeline | P0 |

### ✅ Conditional Expressions (już dostępne)

> Funkcjonalność porównań/logiki/ternary w `$CALCULATE(...)` jest dostępna po TASK-060. W ramach TASK-058 nie trzeba tu nic implementować.

---

## Testy (Clean Architecture)

### Unit Tests

```
tests/unit/router/application/workflows/test_workflow_adaptation_pipeline.py
- test_adaptation_uses_registry_pipeline_resolves_calculate_and_auto
- test_adaptation_respects_condition_and_simulation
- test_adaptation_supports_steps_override

tests/unit/router/application/evaluator/test_loop_expander.py
- test_expand_static_range
- test_expand_dynamic_range_expressions
- test_expand_values_list
- test_expand_nested_loops_cross_product
- test_interleaves_grouped_loops
- test_substitutes_placeholders_in_params_condition_description_id_depends_on
- test_substitutes_placeholders_inside_calculate_expression
- test_no_loop_passthrough
- test_invalid_loop_config_raises_error
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

### Faza 0 - Naprawa adaptacji (P0)

| Krok | Warstwa | Plik | Opis |
|------|---------|------|------|
| 0.1 | Application/Workflows | `registry.py` | Dodać `steps_override` do `expand_workflow()` i użyć jako źródło kroków |
| 0.2 | Application/Router | `router.py` | Adaptacja ma delegować do `registry.expand_workflow(..., steps_override=adapted_steps)` |
| 0.3 | Tests | `test_workflow_adaptation_pipeline.py` | Regression testy na: `$CALCULATE/$AUTO_`, `condition`, symulację kontekstu |

### Faza 1 - Core Loop System (P0)

| Krok | Warstwa | Plik | Opis |
|------|---------|------|------|
| 1 | Application/Workflows | `base.py` | Dodać `loop: Optional[Dict]` do `WorkflowStep` + `_known_fields` + `to_dict()` |
| 2 | Infrastructure | `workflow_loader.py` | Weryfikacja - pole `loop` parsowane automatycznie (bez zmian) |
| 3 | Application/Evaluator | `loop_expander.py` | **NOWY PLIK** - `LoopExpander` class |
| 4 | Application/Evaluator | `__init__.py` | Dodać import i eksport `LoopExpander` do `__all__` |
| 5 | Application/Workflows | `registry.py` | Integracja: loop expansion + `{var}` interpolation przed `_resolve_definition_params()` (także dla `steps_override`) |
| 6 | Application/Workflows | `registry.py` | Naprawa `_resolve_definition_params()` (nie gubić pól/dynamic attrs) |
| 7 | Tests | `test_loop_expander.py` | Unit testy: range/values/nested/group + `{var}` interpolation |
| 8 | Custom Workflows | `simple_table.yaml` | Refaktor na loop syntax (opcjonalnie) |
| 9 | Docs | `_docs/_ROUTER/WORKFLOWS/*.md` | Dodać Loops + `{var}` interpolation do guideów |

### ✅ Faza 2 - Conditional Expressions (zamknięte przez TASK-060)

> Brak prac w TASK-058 (zrobione w TASK-060).

---

## Decyzje Architektoniczne

1. **Jedna interpolacja**: `{var}` dla wszystkich stringów (bez `$FORMAT`).
2. **Loops w core**: single + nested loops oraz `values`.
3. **Kolejność per‑iteracja**: `loop.group` umożliwia interleaving bez nowych “block nodes”.
4. **LoopExpander lokalizacja**: `application/evaluator/` (transformacja danych, bez I/O).
5. **Strict interpolation + limity**: zapobiega “cichym” błędom i eksplozjom liczby kroków.

Kolejność przetwarzania w pipeline (custom workflows):
1. computed params (TASK-056-5)
2. `LoopExpander.expand()` (loop expansion + `{var}` interpolation)
3. `_resolve_definition_params()` (`$CALCULATE`, `$AUTO_*`, `$variable`)
4. `_steps_to_calls()` (`condition` + `simulate_step_effect()`)

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

**Rekomendacja**: Przy okazji TASK-058 naprawić ten dług przez wspólny helper klonowania kroku (np. `_clone_step(step, **overrides)`), który kopiuje wszystkie pola dataclass + dynamic attrs; użyć go w `LoopExpander` i w `_resolve_definition_params()`.

---

## Szacowany Czas Implementacji

| Krok | Czas |
|------|------|
| FAZA 0: Adaptacja używa registry pipeline | 10-20 min |
| `WorkflowStep.loop` + `_known_fields` | 5 min |
| Loop parsing verification | 0 min (automatyczne) |
| `LoopExpander` class (nested + group + strict interpolation) | 45-60 min |
| `__init__.py` update | 2 min |
| Registry integration | 10 min |
| Fix `_resolve_definition_params()` (dług techniczny) | 5 min |
| Unit tests (`LoopExpander`) | 20 min |
| `simple_table.yaml` refaktor (opcjonalne) | 15 min |
| Aktualizacja docs (_docs/_ROUTER/WORKFLOWS/*) | 20-30 min |
| **TOTAL TASK-058** | **~2-3h** |

> **Uwaga**: Conditional expressions (ternary, porównania, operatory logiczne) są już dostępne po **TASK-060**, więc nie zwiększają scope TASK-058.

---

## Weryfikacja Zgodności z Kodem (2025-12-12)

### ✅ Zweryfikowane Lokalizacje Plików

| Element | Ścieżka w TASK-058 | Status |
|---------|-------------------|--------|
| `WorkflowStep` | `server/router/application/workflows/base.py` | ✅ Poprawna |
| `ExpressionEvaluator` | `server/router/application/evaluator/expression_evaluator.py` | ✅ Poprawna |
| `WorkflowRegistry` | `server/router/application/workflows/registry.py` | ✅ Poprawna |
| `Router` (adaptacja) | `server/router/application/router.py` | ✅ Do poprawki (FAZA 0) |
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
| `_expand_triggered_workflow()` (adaptacja) | - | `router.py:433-543` | ⚠️ Wymaga FAZA 0 |

### ✅ Zgodność z Clean Architecture

| Aspekt | Ocena |
|--------|-------|
| `LoopExpander` w `application/evaluator/` | ✅ Poprawna warstwa (logika aplikacyjna) |
| Dependency direction | ✅ Inner → Outer |
| Separation of concerns | ✅ Transformacja danych oddzielona od I/O |

### 📝 Ilustracja Zmian

#### Zmiana 0: Adaptacja nie omija registry pipeline (FAZA 0)

**PRZED** (`router.py:_expand_triggered_workflow()`):
- ręczne budowanie `CorrectedToolCall`,
- brak `$CALCULATE/$AUTO_`, brak `condition`, brak `simulate_step_effect()`.

**PO** (FAZA 0):
```python
calls = registry.expand_workflow(
    workflow_name,
    merged_params,
    eval_context,
    user_prompt=self._current_goal or "",
    steps_override=adapted_steps,
)
```

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
self._evaluator.set_context({**base_context, **all_params})

steps = self._resolve_definition_params(definition.steps, all_params)
return self._steps_to_calls(steps, workflow_name, workflow_params=all_params)
```

**PO** (TASK-058):
```python
# Set evaluator context with all resolved parameters
self._evaluator.set_context({**base_context, **all_params})

steps_source = steps_override if steps_override is not None else definition.steps

# TASK-058: Loop expansion + {var} interpolation BEFORE other processing
expanded_steps = self._loop_expander.expand(
    steps_source,
    {**base_context, **all_params}
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
