---
type: task
id: TASK-003
title: MVP MCP Server i Scene Tools
status: done
priority: medium
assignee: unassigned
depends_on: TASK-002
---

# 🎯 Cel
Uruchomienie serwera MCP i implementacja pierwszej grupy narzędzi (Scene Tools) pozwalających na zarządzanie obiektami.

# 📋 Zakres prac

1. **Inicjalizacja FastMCP**
   - Utworzenie instancji serwera w `server/main.py`.
   - Konfiguracja nazwy serwera i wersji.

2. **Implementacja Handlerów (Scene)**
   - `scene.list_objects()`: Zwraca listę nazw i typów obiektów na scenie.
   - `scene.delete_object(name)`: Usuwa obiekt o podanej nazwie.
   - `scene.clean_scene()`: Usuwa wszystko (przydatne dla AI do startu od zera).

3. **Rejestracja w MCP**
   - Otagowanie funkcji dekoratorem `@mcp.tool`.
   - Podpięcie handlerów do klienta RPC.

4. **Obsługa błędów**
   - Co jeśli obiekt nie istnieje? (Zwróć czytelny błąd JSON, nie stacktrace).

# ✅ Kryteria Akceptacji
- Można podłączyć MCP Server do klienta (np. Claude Desktop / CLI).
- Wywołanie narzędzia `scene.list_objects` zwraca poprawny JSON.
- AI potrafi wyczyścić scenę w Blenderze.
