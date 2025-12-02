import os
from pydantic import BaseModel, Field, ConfigDict

class Config(BaseModel):
    """Application Configuration"""

    model_config = ConfigDict(env_file=".env")

    # Blender RPC Connection
    BLENDER_RPC_HOST: str = Field(default="127.0.0.1", description="Host where Blender Addon is running")
    BLENDER_RPC_PORT: int = Field(default=8765, description="Port where Blender Addon is running")

    # Router Supervisor
    ROUTER_ENABLED: bool = Field(default=True, description="Enable Router Supervisor for LLM tool calls")
    ROUTER_LOG_DECISIONS: bool = Field(default=True, description="Log router decisions")

def get_config() -> Config:
    """Returns configuration loaded from environment variables."""
    return Config(
        BLENDER_RPC_HOST=os.getenv("BLENDER_RPC_HOST", "127.0.0.1"),
        BLENDER_RPC_PORT=int(os.getenv("BLENDER_RPC_PORT", 8765)),
        ROUTER_ENABLED=os.getenv("ROUTER_ENABLED", "true").lower() in ("true", "1", "yes"),
        ROUTER_LOG_DECISIONS=os.getenv("ROUTER_LOG_DECISIONS", "true").lower() in ("true", "1", "yes"),
    )
