# Komunikacja RPC i Concurrency

## Model Wątkowości
Blender jest aplikacją jednowątkową w kontekście API Python (`bpy`). Operacje na danych sceny muszą być wykonywane w głównym wątku (Main Thread).

### Problem
Standardowy `socket.accept()` lub `recv()` jest operacją blokującą. Uruchomienie go w głównym wątku zamrozi interfejs użytkownika (UI) Blendera.

### Rozwiązanie
1. **Network Thread**: Serwer RPC (`rpc_server.py`) działa w osobnym wątku (`threading.Thread`). Odbiera żądania i parsuje JSON.
2. **Main Thread Bridge**: Po odebraniu komendy, wątek sieciowy nie wykonuje jej bezpośrednio. Zamiast tego:
   - Dodaje zadanie do kolejki.
   - Rejestruje funkcję wykonawczą używając `bpy.app.timers.register(func)`.
3. **Execution**: Przy następnym odświeżeniu pętli wydarzeń (Event Loop), Blender wykonuje funkcję z timera, która ma bezpieczny dostęp do `bpy`.

## Protokół
Komunikacja odbywa się po **TCP Sockets** przy użyciu JSON.

### Request
```json
{
    "request_id": "uuid",
    "cmd": "command_name",
    "args": { "arg1": "val1" }
}
```

### Response
```json
{
    "request_id": "uuid",
    "status": "ok", 
    "result": { ... }
}
```
lub
```json
{
    "request_id": "uuid",
    "status": "error", 
    "error": "Message string"
}
```
