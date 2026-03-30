# Reference-Guided Creature Build

Use this on the `llm-guided` surface when you want staged manual building with
reference images and bounded vision feedback after each checkpoint.

## Best Fit

- low-poly animal / creature blockouts
- staged character-like models with separate parts
- front + side reference-driven work where exact realism is not required

## Recommended Flow

1. `router_get_status()`
2. `scene_clean_scene(...)` if needed
3. `reference_images(action="attach", ...)` for:
   - front reference
   - side reference
4. `router_set_goal("create a low-poly squirrel matching front and side reference images")`
5. if the router returns `continuation_mode="guided_manual_build"`, continue on
   the shaped manual build surface
6. build in short stages:
   - head + ears
   - face details
   - body + tail
   - paws + final cleanup
7. after each stage run:
   - `reference_iterate_stage_checkpoint(target_object="Squirrel", checkpoint_label="<stage>", preset_profile="compact")`
8. use the response in this order:
   - `loop_disposition`
   - `correction_focus`
   - `shape_mismatches`
   - `proportion_mismatches`
   - `next_corrections`
9. repeat the next stage or correction step

## Prompt Template

```text
Użyj aktywnego profilu MCP Blendera z MLX vision i zbuduj low-poly squirrel na bazie dwóch lokalnych referencji.

Reference files:
- FRONT_REFERENCE_PATH=<ABSOLUTE_PATH>
- SIDE_REFERENCE_PATH=<ABSOLUTE_PATH>

Zasady:
- pracuj na aktywnym `llm-guided` shaped surface
- nie zgaduj hidden/internal tool names
- `call_tool(...)` używaj tylko dla tooli bezpośrednio widocznych albo właśnie odkrytych przez `search_tools(...)`
- keep parts as separate objects
- skup się na low-poly shape match, nie na materiałach i futrze
- po każdym etapie użyj `reference_iterate_stage_checkpoint(...)`
- dla etapów z jedną główną bryłą możesz używać `target_object=...`
- dla złożonej pełnej sylwetki użyj:
  - `target_objects=[...]`
  - albo `collection_name="Squirrel"`
  - albo nic, jeśli chcesz compare całej złożonej sceny/sylwetki

Workflow:
1. `router_get_status()`
2. wyczyść scenę, zostaw światła i kamery
3. dołącz obie referencje przez `reference_images(...)`
4. ustaw cel:
   `create a low-poly squirrel matching front and side reference images`
5. jeśli router zwróci `guided_manual_build`, kontynuuj ręcznie na shaped build surface
6. buduj w 4 etapach:
   - etap 1: head + ears
   - etap 2: snout + eyes + nose
   - etap 3: body + tail
   - etap 4: paws + final proportion cleanup
7. po każdym etapie wywołaj:
   `reference_iterate_stage_checkpoint(target_object="Squirrel", checkpoint_label="<stage_name>", preset_profile="compact")`
8. przy kolejnej iteracji priorytetyzuj:
   - `loop_disposition`
   - `correction_focus`
   - potem `shape_mismatches`
   - potem `proportion_mismatches`
   - dopiero potem `next_corrections`
9. jeśli `loop_disposition == "inspect_validate"`, zatrzymaj free-form modelowanie i przejdź do inspect/measure/assert zanim zrobisz kolejną dużą zmianę

Na końcu każdego etapu zwróć tylko:
- co zostało zrobione
- `loop_disposition`
- `correction_focus`
- co nadal nie zgadza się z referencją
- następny krok
```

## Practical Notes

- `compact` profile jest dobrym defaultem do częstych checkpointów
- `rich` profile ma sens dopiero, gdy jeden etap jest już dość stabilny i
  chcesz szerszego wielowidokowego porównania
- `correction_focus` powinno być traktowane jako pierwsza lista do działania,
  bo jest już ograniczona i uporządkowana pod iteracyjne poprawki
- `loop_disposition="inspect_validate"` oznacza, że system wykrywa powtarzający
  się focus i lepiej przejść chwilowo do truth-layer verification niż dalej
  zgadywać korekty
- dla pełnej wieloczęściowej wiewiórki nie zawężaj finalnych iteracji do samego
  `Squirrel_Body`, bo loop oceni wtedy tylko korpus
