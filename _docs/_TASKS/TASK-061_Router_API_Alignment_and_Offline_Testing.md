# TASK-061: Router – zgodność API MCP, mega-tools, offline/test stability

**Status**: ✅ DONE (zmiany w repo, bez PR)
**Priority**: P1
**Created**: 2025-12-12
**Related**: TASK-049 (dispatcher mapping), TASK-048 (DI/LaBSE), TASK-041 (workflows), TASK-055-FIX (ensemble/modifiers)

---

## Cel

Szybki sanity-check routera (Supervisor Layer) pod kątem:
- spójności z faktycznym API narzędzi MCP,
- wykonywalności „mega-tools” (`mesh_select*`) przez dispatcher,
- stabilności testów/offline (bez pobierania LaBSE/HF w pytest).

## Dlaczego to ważne

Router jest „supervisorem” nad tool-callami LLM. Jeśli router:
- emituje tool-calle niezgodne z MCP (złe nazwy tooli/parametrów),
- opiera się o metadata, które nie odpowiadają realnym toolom,
- albo w testach dotyka sieci / pobiera modele,

to cała warstwa „bezpieczeństwa” działa pozornie: wygląda dobrze na papierze, ale realnie nie da się jej wykonać lub jest niestabilna w CI/offline.

---

## Spostrzeżenia (co było nie tak)

### 1) Drift API: Router/docs vs realne narzędzia MCP

W kilku miejscach router (engines + przykłady w `_docs/_ROUTER`) używał starych nazw parametrów / narzędzi:
- `mesh_bevel.width` vs aktualne `mesh_bevel.offset`
- `mesh_extrude_region.depth` vs aktualne `mesh_extrude_region.move`
- przykłady z `mesh_extrude` (narzędzie nie istnieje w MCP; jest `mesh_extrude_region`)
- override reguły dla `mesh_select_targeted` używały nieistniejących parametrów (`location`/`threshold`) zamiast `axis/min_coord/max_coord/...`

Efekt: router mógł generować tool-calle, których serwer nie potrafił wykonać (albo które nie miały sensu).

### 2) Router emitował mega-tools, których dispatcher nie mapował

Router w auto-fixach i workflowach używa `mesh_select` / `mesh_select_targeted`, ale dispatcher miał mapowania głównie dla legacy nazw (`mesh_select_all`, itd.). W praktyce część „napraw” routera była niewykonywalna.

### 3) Metadata drift (tools_metadata)

`server/router/infrastructure/tools_metadata/*` zawierało definicje niezsynchronizowane z realnym MCP:
- param `width` w `mesh_bevel.json` (powinno być `offset`)
- referencje do nieistniejącego narzędzia `mesh_extrude` (JSON + część docs)

To jest naturalny „drift” jeśli metadata są utrzymywane ręcznie.

### 4) Testy wieszały się (LaBSE / sieć)

`test_supervisor_router.py` potrafił zawieszać się przez lazy init ensemble matchera, który w tle próbował ładować `SentenceTransformer("LaBSE")` (co pod restricted network prowadzi do prób downloadu/timeoutów).

Wniosek: testy unit nie mogą zależeć od pobierania dużych modeli ani od internetu.

### 5) Workflow source of truth: docs vs runtime

W repo są pełne workflow YAML w `_docs/_ROUTER/WORKFLOWS/*`, ale runtime loader ładuje tylko z `server/router/application/workflows/custom/*.yaml`.

Efekt uboczny: testy (i użytkownicy) mogą zakładać istnienie workflowów z docs, których runtime w ogóle nie widzi.

---

## Decyzja projektowa

Zamiast dodawać aliasy/kompatybilność wsteczną w routerze (np. akceptować `depth` i mapować na `move`), wybrano:
- **uściślenie routera do aktualnego API MCP**,
- oraz aktualizację najbardziej istotnych docs/testów.

Powód: router jest warstwą „supervisora” – powinien emitować dokładnie to, co MCP potrafi wykonać; aliasowanie w supervisorze łatwo ukrywa drift i utrudnia wykrywanie regresji.

---

## Co zostało poprawione (co + dlaczego + gdzie)

Poniżej lista zmian z uzasadnieniem. (Ścieżki odnoszą się do workspace.)

### Runtime / kod serwera

- `server/adapters/mcp/dispatcher.py`
  - **Co:** dodane mapowania dla mega-tools `mesh_select` i `mesh_select_targeted`.
  - **Dlaczego:** router w auto-fixach generuje `mesh_select*`; bez mapowania dispatcher nie potrafił tego wykonać → poprawki routera były „martwe”.

- `server/router/application/engines/tool_correction_engine.py`
  - **Co:** ujednolicenie limitów parametrów do aktualnych nazw (`mesh_bevel.offset`, `mesh_extrude_region.move`), clamping wektorów/list (clamp per komponent).
  - **Dlaczego:** router clampował/naprawiał parametry w starym formacie (`width`, `depth`), a `move` jest wektorem (wymaga innego clampa).

- `server/router/application/engines/error_firewall.py`
  - **Co:** reguła bevel działa na `offset` zamiast `width`.
  - **Dlaczego:** firewall ma blokować realnie niebezpieczne parametry, a nie parametry, których MCP nie zna.

- `server/router/application/engines/tool_override_engine.py`
  - **Co:** poprawione override’y pod poprawne sygnatury MCP:
    - phone-like: `mesh_extrude_region.move` zamiast `depth`
    - tower-like: poprawne parametry `mesh_select_targeted` (`axis/min_coord/max_coord/...`)
  - **Dlaczego:** override engine ma generować sekwencje wykonywalne; wcześniej część override’ów była niepoprawna semantycznie.

- `server/router/infrastructure/tools_metadata/mesh/mesh_bevel.json`
  - **Co:** `width`→`offset`, dodanie `profile`, aktualizacja opisów/related_tools.
  - **Dlaczego:** metadata są wejściem do klasyfikatora i docs; drift powoduje błędne podpowiedzi i błędne embeddingi.

- `server/router/infrastructure/tools_metadata/mesh/mesh_inset.json`
  - **Co:** usunięcie nieistniejącego parametru `use_boundary`.
  - **Dlaczego:** nie można dokumentować/klasyfikować parametrów, których MCP tool nie przyjmuje.

- `server/router/infrastructure/tools_metadata/mesh/mesh_extrude.json`
  - **Co:** usunięte.
  - **Dlaczego:** narzędzie `mesh_extrude` nie istnieje w MCP; utrzymywanie tej definicji generowało fałszywe ścieżki i drift w docs.

- `server/infrastructure/di.py`
  - **Co:** pod pytestem LaBSE nie jest ładowany; w trybie offline (`HF_HUB_OFFLINE`) używane jest `local_files_only`.
  - **Dlaczego:** testy unit nie mogą próbować pobierać modeli (restricted network) – powodowało timeout/hang.

- `server/router/application/classifier/intent_classifier.py`
- `server/router/application/classifier/workflow_intent_classifier.py`
  - **Co:** analogiczne zabezpieczenie jak wyżej (pytest skip + `local_files_only`).
  - **Dlaczego:** nawet jeśli DI zwróci `None`, klasyfikator potrafił próbować pobrać model w swojej ścieżce `_load_model()`.

- `server/router/application/matcher/modifier_extractor.py`
  - **Co:** semantic matching respektuje `similarity_threshold` także na poziomie avg similarity; per-word threshold wyprowadzony z `similarity_threshold`.
  - **Dlaczego:** zachowanie miało być konfigurowalne przez `similarity_threshold`; wcześniej było częściowo „zahardkodowane”.

- `server/router/application/workflows/registry.py`
  - **Co:** przy custom workflowach `$CALCULATE(...)` widzi również `dimensions` z kontekstu (nie gubimy kontekstu przy resetowaniu evaluator context).
  - **Dlaczego:** bez tego `min_dim` było „Unknown variable”, mimo że workflow miał kontekst `dimensions`.

- `server/router/application/workflows/custom/picnic_table.yaml`
  - **Co:** dodany minimalny `picnic_table_workflow` z defaultami i modyfikatorem `"straight legs"` oraz użyciem `$leg_angle_*` w krokach.
  - **Dlaczego:** testy/feature zakładają istnienie workflow w runtime loaderze; workflow z `_docs/_ROUTER/WORKFLOWS` nie jest automatycznie ładowany przez aplikację.

### Docs (najbardziej „frontowe”)

- `_docs/_ROUTER/QUICK_START.md`, `_docs/_ROUTER/API.md`
  - **Co:** przykłady `mesh_extrude_region` przepisane na `move` zamiast `depth`.
  - **Dlaczego:** Quick Start/API to pierwsze miejsca, z których ludzie kopiują przykłady.

- `_docs/_ROUTER/README.md`
  - **Co:** scenariusz „extrude” przepisany z `mesh_extrude(depth)` na `mesh_extrude_region(move)` i usunięcie nieistniejącego `mode: FACE` w `mesh_select`.
  - **Dlaczego:** README ma opisywać działający flow i realne parametry.

- `_docs/_ROUTER/PATTERNS.md`
  - **Co:** `inherit_params: ["depth"]` → `inherit_params: ["move"]` w przykładzie override.
  - **Dlaczego:** spójność z aktualnym API.

### Testy

Zaktualizowane zostały testy routera i workflow systemu tak, aby:
- używały aktualnych nazw parametrów (`offset`, `move`),
- odzwierciedlały aktualne zachowanie ensemble/modifier extractor (normalizacja confidence, „modifiers only”),
- oraz nie zakładały obecności workflowów wyłącznie w `_docs`.

---

## Walidacja / jak sprawdzić

Polecenia:
```bash
poetry run pytest tests/unit/router -q
```

---

## Ryzyka / uwagi kompatybilności

- Jeśli jakiś zewnętrzny klient nadal wysyła `mesh_bevel.width` lub `mesh_extrude_region.depth`, to nie jest to kompatybilne z aktualnym MCP API (to drift po stronie klienta). Router nie powinien tego „maskować” bez wyraźnej polityki kompatybilności.

---

## Rekomendacje (następne kroki)

1) Doc sweep: `_docs/_ROUTER` nadal ma dużo referencji do `mesh_extrude`/`depth`/`width` (np. `ROUTER_HIGH_LEVEL_OVERVIEW.md`, część `IMPLEMENTATION/*`). Warto zrobić globalny update i/lub generator.

2) Anti-drift guard:
- dodać prosty test/skrypt CI porównujący:
  - tool signatures w `server/adapters/mcp/areas/*` vs `server/router/infrastructure/tools_metadata/*`
  - oraz sanity-check, że router nie emituje nieistniejących tool names.

3) Offline mode spójnie w całym repo:
- `vector_db_manage` też ładuje `SentenceTransformer("LaBSE")` bez `local_files_only`; warto ujednolicić z DI.

---

## Podsumowanie realizacji rekomendacji (2025-12-12)

### 1) Doc sweep (`_docs/_ROUTER`)

- Zrobiony globalny update przykładów workflow pod aktualne API:
  - `mesh_bevel.width` → `mesh_bevel.offset`
  - `mesh_extrude_region.depth` → `mesh_extrude_region.move`
  - usunięcie legacy `mesh_extrude`
- Najważniejsze pliki zaktualizowane w tej rundzie:
  - `_docs/_ROUTER/WORKFLOWS/creating-workflows-tutorial.md`
  - `_docs/_ROUTER/WORKFLOWS/yaml-workflow-guide.md`
  - `_docs/_ROUTER/WORKFLOWS/README.md`
  - `_docs/_ROUTER/WORKFLOWS/expression-reference.md`

### 2) Anti-drift guard (test/CI)

- Dodany test: `tests/unit/router/infrastructure/test_mcp_tools_metadata_alignment.py`
  - porównuje `server/adapters/mcp/areas/*.py` vs `server/router/infrastructure/tools_metadata/**/*.json`
  - weryfikuje też stałe `tool_name="..."` emitowane przez router
- Przy okazji naprawione realne drift-y wykryte przez test:
  - `modeling_create_primitive`: `type` → `primitive_type`
  - `scene_list_objects`: usunięty nieistniejący parametr `filter_type`
  - `text_create`/`text_edit`: `content` → `text`

### 3) Offline mode (vector_db_manage)

- `server/adapters/mcp/areas/vector_db.py` używa teraz wspólnego `get_labse_model()` (DI), więc:
  - pod pytestem nie próbuje ładować/pobierać LaBSE
  - przy `HF_HUB_OFFLINE=1` używa local-only (bez sieci)
  - zwraca czytelny błąd, gdy embeddings są niedostępne

### Changelog

- Dodane: `_docs/_CHANGELOG/109-2025-12-12-router-api-alignment-offline-guards.md`
- Zaktualizowany indeks: `_docs/_CHANGELOG/README.md`

### Walidacja

```bash
poetry run pytest tests/unit/router -q
```
Wynik: `1377 passed, 2 skipped`.
