from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from server.domain.models.rpc import RpcResponse

class IRpcClient(ABC):
    @abstractmethod
    def send_request(
        self,
        cmd: str,
        args: Dict[str, Any] = None,
        timeout_seconds: Optional[float] = None,
    ) -> RpcResponse:
        """Sends an RPC request and returns the response."""
        pass
