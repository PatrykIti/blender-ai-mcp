from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
import uuid

class RpcRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cmd: str
    args: Dict[str, Any] = Field(default_factory=dict)

class RpcResponse(BaseModel):
    request_id: str
    status: str  # "ok" or "error"
    result: Optional[Any] = None
    error: Optional[str] = None
