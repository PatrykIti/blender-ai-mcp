from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from server.domain.models.rpc import RpcResponse


class IRpcClient(ABC):
    @abstractmethod
    def send_request(
        self,
        cmd: str,
        args: Dict[str, Any] = None,
        timeout_seconds: Optional[float] = None,
        *,
        rpc_timeout_seconds: Optional[float] = None,
    ) -> RpcResponse:
        """Sends an RPC request and returns the response."""
        pass

    def launch_background_job(
        self,
        cmd: str,
        args: Optional[Dict[str, Any]] = None,
        *,
        timeout_seconds: Optional[float] = None,
    ) -> RpcResponse:
        raise NotImplementedError

    def get_background_job_status(self, job_id: str, *, timeout_seconds: Optional[float] = None) -> RpcResponse:
        raise NotImplementedError

    def cancel_background_job(self, job_id: str) -> RpcResponse:
        raise NotImplementedError

    def collect_background_job_result(self, job_id: str, *, timeout_seconds: Optional[float] = None) -> RpcResponse:
        raise NotImplementedError
