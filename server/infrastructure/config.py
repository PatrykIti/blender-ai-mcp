import os
from pydantic import BaseModel, Field

class Config(BaseModel):
    """Application Configuration"""
    
    # Blender RPC Connection
    BLENDER_RPC_HOST: str = Field(default="127.0.0.1", description="Host where Blender Addon is running")
    BLENDER_RPC_PORT: int = Field(default=8765, description="Port where Blender Addon is running")

    class Config:
        env_file = ".env"

def get_config() -> Config:
    """Returns configuration loaded from environment variables."""
    return Config(
        BLENDER_RPC_HOST=os.getenv("BLENDER_RPC_HOST", "127.0.0.1"),
        BLENDER_RPC_PORT=int(os.getenv("BLENDER_RPC_PORT", 8765))
    )
