---
type: task
id: TASK-005_Dockerize_Server
title: Konteneryzacja MCP Servera (Docker)
status: done
priority: medium
assignee: unassigned
depends_on: TASK-004_Modeling_Tools
---

# 🎯 Cel
Utworzenie obrazu Docker dla serwera MCP (`blender-ai-mcp`) w celu ułatwienia dystrybucji i uruchamiania w izolowanym środowisku.
Umożliwi to uruchamianie serwera bez konieczności lokalnej instalacji Pythona/Poetry przez użytkownika końcowego (wymagany tylko Docker i Blender).

# 📋 Zakres prac

1. **Dockerfile (`server/Dockerfile` lub `./Dockerfile`)**
   - Bazowy obraz: `python:3.10-slim`.
   - Instalacja zależności systemowych (jeśli potrzebne).
   - Instalacja Poetry.
   - Kopiowanie plików projektu (`pyproject.toml`, `poetry.lock`, `server/`).
   - Instalacja zależności projektu (`poetry install --no-dev`).
   - Entrypoint: `python -m server.main`.

2. **Docker Compose (`docker-compose.yml`) - Opcjonalnie**
   - Dla wygody uruchamiania z mapowaniem portów (chociaż MCP działa na stdio, więc Docker Compose jest mniej przydatny dla Cline, ale przydatny do testów manualnych lub TCP transportu w przyszłości).
   - Skupmy się na `docker build` i `docker run`.

3. **Obsługa sieci (Host Networking)**
   - **Wyzwanie:** Serwer w kontenerze musi połączyć się z Blenderem działającym na hoście (`localhost:8765`).
   - W Dockerze `localhost` oznacza kontener. Aby połączyć się z hostem, trzeba użyć `host.docker.internal` (Mac/Windows) lub `--network host` (Linux).
   - Wymagana parametryzacja hosta RPC w `RpcClient` przez zmienne środowiskowe (`RPC_HOST`, `RPC_PORT`).

4. **Aktualizacja Kodu (`server/infrastructure/config.py`?)**
   - Dodać obsługę zmiennych środowiskowych dla konfiguracji połączenia RPC.

5. **Dokumentacja**
   - Instrukcja budowania i uruchamiania w `README.md`.
   - Przykładowa konfiguracja dla Cline (używając `docker run ...`).

# ✅ Kryteria Akceptacji
- Można zbudować obraz: `docker build -t blender-ai-mcp .`
- Można uruchomić kontener, który łączy się z Blenderem na hoście.
- Narzędzia MCP działają poprawnie z poziomu kontenera.