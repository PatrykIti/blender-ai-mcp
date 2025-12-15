# RPC Communication and Concurrency

## Threading Model
Blender is a single-threaded application regarding the Python API (`bpy`). Operations on scene data must be executed on the **Main Thread**.

### The Problem
Standard `socket.accept()` or `recv()` operations are blocking. Running them on the main thread would freeze the Blender UI.

### The Solution
1. **Network Thread**: The RPC Server (`rpc_server.py`) runs in a separate thread (`threading.Thread`). It accepts requests and parses JSON.
2. **Main Thread Bridge**: Upon receiving a command, the network thread does not execute it directly. Instead:
   - It pushes the task to a queue.
   - It registers an execution function using `bpy.app.timers.register(func)`.
3. **Execution**: On the next Event Loop tick, Blender executes the function from the timer, which has safe access to `bpy`.

## Protocol
Communication occurs via **TCP Sockets** using JSON.

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
or
```json
{
    "request_id": "uuid",
    "status": "error", 
    "error": "Message string"
}
```
