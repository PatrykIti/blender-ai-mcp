---
type: task
id: TASK-003_2_Refactor_Main_DI
title: Refaktoryzacja Main i DI (Separation of Concerns)
status: done
priority: high
assignee: unassigned
depends_on: TASK-003_1_Refactor_Architecture
---

# 🎯 Cel
Dalsza refaktoryzacja serwera w celu usunięcia logiki konfiguracyjnej i adapterów z `server/main.py`.
Wydzielenie kontenera Dependency Injection oraz definicji narzędzi MCP do odpowiednich warstw.

# 📋 Analiza
Obecnie `server/main.py` robi trzy rzeczy na raz:
1. Tworzy instancje obiektów (`RpcClient`, `SceneToolHandler`).
2. Definiuje adaptery wejściowe MCP (`@mcp.tool`).
3. Uruchamia serwer.

# 🛠 Plan Prac

1. **Infrastructure Layer (`server/infrastructure/`)**
   - Utworzyć `server/infrastructure/container.py`: Klasa `Container` (lub prosta funkcja), która tworzy i łączy wszystkie zależności (`RpcClient` -> `Handlers`). Zwraca gotowe handlery.

2. **Adapters Layer (`server/adapters/mcp/`)**
   - Utworzyć `server/adapters/mcp/server.py`:
     - Tu przeniesiemy instancję `FastMCP`.
     - Tu zdefiniujemy funkcje `@mcp.tool`.
     - Funkcje te będą korzystać z handlerów dostarczonych przez kontener DI.

3. **Entry Point (`server/main.py`)**
   - Oczyścić plik.
   - Ma tylko zaimportować `server` z adapterów i wywołać `run()`.

# ✅ Struktura Docelowa

```
server/
  infrastructure/
    container.py       # Dependency Injection Container
  
  adapters/
    mcp/
      server.py        # FastMCP tools definition (korzysta z containera)
  
  main.py              # from server.adapters.mcp.server import run; run()
```

# ✅ Kryteria Akceptacji
- `main.py` ma mniej niż 10 linii kodu.
- Brak logiki budowania obiektów w `main.py`.
- Narzędzia MCP są zdefiniowane w `adapters/mcp/`.
- Aplikacja działa tak samo jak wcześniej.