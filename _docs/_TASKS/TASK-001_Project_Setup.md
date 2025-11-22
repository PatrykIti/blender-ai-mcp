---
type: task
id: TASK-001
title: Inicjalizacja Projektu i Struktury
status: in_progress
priority: high
assignee: unassigned
---

# 🎯 Cel
Przygotowanie środowiska pracy, repozytorium oraz podstawowej struktury plików zgodnej z architekturą "Clean Architecture" opisaną w głównym README, wykorzystując **Poetry** do zarządzania zależnościami.

# 📋 Zakres prac

1. **Struktura Katalogów**
   - Utworzyć katalogi:
     - `server/domain/models`
     - `server/domain/tools`
     - `server/application/tool_handlers`
     - `server/adapters/rpc`
     - `server/adapters/mcp`
     - `server/infrastructure`
     - `blender_addon/api`
     - `blender_addon/utils`

2. **Zależności (Poetry)**
   - Zainicjować projekt `poetry init`.
   - Dodać zależności:
     - `mcp`
     - `pydantic`
     - `uvicorn`

3. **Konfiguracja Git**
   - `.gitignore` (ignorowanie `__pycache__`, `.venv`, `*.zip`, `.DS_Store`).

4. **Dokumentacja Deweloperska**
   - Dodać instrukcję instalacji i uruchamiania (`poetry install`) w `README.md`.

# ✅ Kryteria Akceptacji
- Struktura katalogów istnieje.
- Plik `pyproject.toml` i `poetry.lock` są obecne.
- Zależności instalują się poprawnie (`poetry install`).
- Repozytorium jest czyste.