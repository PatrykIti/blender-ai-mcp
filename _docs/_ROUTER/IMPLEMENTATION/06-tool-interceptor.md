# Tool Interceptor

**Task:** TASK-039-6
**Layer:** Application
**Status:** ✅ Done

## Overview

Captures and records LLM tool calls for router processing.

## File

- `server/router/application/interceptor/tool_interceptor.py`

## Implementation

```python
class ToolInterceptor(IToolInterceptor):
    def intercept(self, tool_name: str, params: Dict, prompt: str = None) -> InterceptedToolCall
    def get_history(self, limit: int = 10) -> List[InterceptedToolCall]
    def clear_history() -> None
    def get_session_calls(session_id: str) -> List[InterceptedToolCall]
    def start_session(session_id: str = None) -> str
    def end_session() -> None
    def get_last_call() -> Optional[InterceptedToolCall]
    def get_calls_by_tool(tool_name: str, limit: int = 10) -> List[InterceptedToolCall]
    def get_calls_since(since: datetime) -> List[InterceptedToolCall]
```

## Features

- Captures all incoming tool calls from LLM
- Maintains call history with configurable max size
- Session management for grouping related calls
- Query methods for filtering history
- Timestamps for all calls

## Usage

```python
interceptor = ToolInterceptor(max_history=100)

# Start a session
session_id = interceptor.start_session()

# Intercept a call
call = interceptor.intercept("mesh_extrude_region", {"move": [0.0, 0.0, 1.0]}, prompt="extrude up")

# Query history
last = interceptor.get_last_call()
recent = interceptor.get_history(limit=5)
session_calls = interceptor.get_session_calls(session_id)
```

## Tests

- `tests/unit/router/application/test_tool_interceptor.py` - 24 tests
