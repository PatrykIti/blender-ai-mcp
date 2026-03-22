import os
from pydantic import BaseModel, Field, ConfigDict, model_validator

class Config(BaseModel):
    """Application Configuration"""

    model_config = ConfigDict(env_file=".env")

    # Blender RPC Connection
    BLENDER_RPC_HOST: str = Field(default="127.0.0.1", description="Host where Blender Addon is running")
    BLENDER_RPC_PORT: int = Field(default=8765, description="Port where Blender Addon is running")

    # Router Supervisor
    ROUTER_ENABLED: bool = Field(default=True, description="Enable Router Supervisor for LLM tool calls")
    ROUTER_LOG_DECISIONS: bool = Field(default=True, description="Log router decisions")

    # MCP Surface / Factory
    MCP_SURFACE_PROFILE: str = Field(default="legacy-flat", description="Bootstrap surface profile")
    MCP_DEFAULT_CONTRACT_LINE: str | None = Field(default=None, description="Optional default public contract line")
    MCP_LIST_PAGE_SIZE: int = Field(default=100, description="Default MCP list page size")
    MCP_TOOL_TIMEOUT_SECONDS: float = Field(default=30.0, gt=0, description="Foreground MCP tool timeout")
    MCP_TASK_TIMEOUT_SECONDS: float = Field(default=300.0, gt=0, description="Background MCP task timeout")
    RPC_TIMEOUT_SECONDS: float = Field(default=30.0, gt=0, description="RPC socket timeout")
    ADDON_EXECUTION_TIMEOUT_SECONDS: float = Field(default=30.0, gt=0, description="Blender addon execution timeout")

    @model_validator(mode="after")
    def validate_timeout_hierarchy(self):
        """Validate deterministic timeout hierarchy across runtime boundaries."""

        if self.RPC_TIMEOUT_SECONDS < self.ADDON_EXECUTION_TIMEOUT_SECONDS:
            raise ValueError("RPC_TIMEOUT_SECONDS must be >= ADDON_EXECUTION_TIMEOUT_SECONDS")
        if self.MCP_TASK_TIMEOUT_SECONDS < self.MCP_TOOL_TIMEOUT_SECONDS:
            raise ValueError("MCP_TASK_TIMEOUT_SECONDS must be >= MCP_TOOL_TIMEOUT_SECONDS")
        return self

def get_config() -> Config:
    """Returns configuration loaded from environment variables."""
    return Config(
        BLENDER_RPC_HOST=os.getenv("BLENDER_RPC_HOST", "127.0.0.1"),
        BLENDER_RPC_PORT=int(os.getenv("BLENDER_RPC_PORT", 8765)),
        ROUTER_ENABLED=os.getenv("ROUTER_ENABLED", "true").lower() in ("true", "1", "yes"),
        ROUTER_LOG_DECISIONS=os.getenv("ROUTER_LOG_DECISIONS", "true").lower() in ("true", "1", "yes"),
        MCP_SURFACE_PROFILE=os.getenv("MCP_SURFACE_PROFILE", "legacy-flat"),
        MCP_DEFAULT_CONTRACT_LINE=os.getenv("MCP_DEFAULT_CONTRACT_LINE") or None,
        MCP_LIST_PAGE_SIZE=int(os.getenv("MCP_LIST_PAGE_SIZE", 100)),
        MCP_TOOL_TIMEOUT_SECONDS=float(os.getenv("MCP_TOOL_TIMEOUT_SECONDS", 30.0)),
        MCP_TASK_TIMEOUT_SECONDS=float(os.getenv("MCP_TASK_TIMEOUT_SECONDS", 300.0)),
        RPC_TIMEOUT_SECONDS=float(os.getenv("RPC_TIMEOUT_SECONDS", 30.0)),
        ADDON_EXECUTION_TIMEOUT_SECONDS=float(os.getenv("ADDON_EXECUTION_TIMEOUT_SECONDS", 30.0)),
    )
