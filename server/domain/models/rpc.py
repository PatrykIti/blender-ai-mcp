import uuid
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class RpcRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cmd: str
    args: Dict[str, Any] = Field(default_factory=dict)
    timeout_seconds: Optional[float] = None
    deadline_unix_ms: Optional[int] = None


class RpcResponse(BaseModel):
    request_id: str
    status: str  # "ok" or "error"
    result: Optional[Any] = None
    error: Optional[str] = None
    error_code: Optional[str] = None
    error_boundary: Optional[str] = None
