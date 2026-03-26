import os

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Application Configuration"""

    model_config = SettingsConfigDict(env_file=".env")

    # Blender RPC Connection
    BLENDER_RPC_HOST: str = Field(default="127.0.0.1", description="Host where Blender Addon is running")
    BLENDER_RPC_PORT: int = Field(default=8765, description="Port where Blender Addon is running")

    # Router Supervisor
    ROUTER_ENABLED: bool = Field(default=True, description="Enable Router Supervisor for LLM tool calls")
    ROUTER_LOG_DECISIONS: bool = Field(default=True, description="Log router decisions")
    OTEL_ENABLED: bool = Field(default=False, description="Enable OpenTelemetry bootstrap")
    OTEL_EXPORTER: str = Field(default="none", description="OpenTelemetry exporter: none|console|memory")
    OTEL_SERVICE_NAME: str = Field(default="blender-ai-mcp", description="OpenTelemetry service.name")

    # MCP Surface / Factory
    MCP_SURFACE_PROFILE: str = Field(default="legacy-flat", description="Bootstrap surface profile")
    MCP_DEFAULT_CONTRACT_LINE: str | None = Field(default=None, description="Optional default public contract line")
    MCP_LIST_PAGE_SIZE: int = Field(default=100, description="Default MCP list page size")
    MCP_TOOL_TIMEOUT_SECONDS: float = Field(default=30.0, gt=0, description="Foreground MCP tool timeout")
    MCP_TASK_TIMEOUT_SECONDS: float = Field(default=300.0, gt=0, description="Background MCP task timeout")
    RPC_TIMEOUT_SECONDS: float = Field(default=30.0, gt=0, description="RPC socket timeout")
    ADDON_EXECUTION_TIMEOUT_SECONDS: float = Field(default=30.0, gt=0, description="Blender addon execution timeout")

    # Vision runtime scaffold
    VISION_ENABLED: bool = Field(default=False, description="Enable bounded vision-assist runtime")
    VISION_PROVIDER: str = Field(
        default="transformers_local",
        description="Vision backend provider: transformers_local|openai_compatible_external",
    )
    VISION_ALLOW_ON_GUIDED: bool = Field(default=True, description="Allow vision assistance on llm-guided")
    VISION_MAX_IMAGES: int = Field(default=8, gt=0, description="Maximum images per bounded vision request")
    VISION_MAX_TOKENS: int = Field(default=400, gt=0, description="Maximum output tokens for vision assistance")
    VISION_TIMEOUT_SECONDS: float = Field(default=20.0, gt=0, description="Timeout for one bounded vision request")
    VISION_LOCAL_MODEL_ID: str | None = Field(default=None, description="Local HF vision model id")
    VISION_LOCAL_MODEL_PATH: str | None = Field(default=None, description="Local HF vision model path")
    VISION_LOCAL_DEVICE: str = Field(default="cpu", description="Device for local vision backend")
    VISION_LOCAL_DTYPE: str = Field(default="auto", description="Dtype for local vision backend")
    VISION_EXTERNAL_BASE_URL: str | None = Field(default=None, description="Base URL for external OpenAI-compatible vision")
    VISION_EXTERNAL_MODEL: str | None = Field(default=None, description="Model name for external OpenAI-compatible vision")
    VISION_EXTERNAL_API_KEY: str | None = Field(default=None, description="Inline API key for external vision endpoint")
    VISION_EXTERNAL_API_KEY_ENV: str | None = Field(
        default=None,
        description="Environment variable name containing the API key for external vision endpoint",
    )

    @model_validator(mode="after")
    def validate_timeout_hierarchy(self):
        """Validate deterministic timeout hierarchy across runtime boundaries."""

        if self.RPC_TIMEOUT_SECONDS < self.ADDON_EXECUTION_TIMEOUT_SECONDS:
            raise ValueError("RPC_TIMEOUT_SECONDS must be >= ADDON_EXECUTION_TIMEOUT_SECONDS")
        if self.MCP_TASK_TIMEOUT_SECONDS < self.MCP_TOOL_TIMEOUT_SECONDS:
            raise ValueError("MCP_TASK_TIMEOUT_SECONDS must be >= MCP_TOOL_TIMEOUT_SECONDS")
        return self

    @model_validator(mode="after")
    def validate_vision_provider(self):
        """Keep the vision provider vocabulary explicit."""

        if self.VISION_PROVIDER not in {"transformers_local", "openai_compatible_external"}:
            raise ValueError("VISION_PROVIDER must be one of: transformers_local, openai_compatible_external")
        return self


def get_config() -> Config:
    """Returns configuration loaded from environment variables."""
    return Config(
        BLENDER_RPC_HOST=os.getenv("BLENDER_RPC_HOST", "127.0.0.1"),
        BLENDER_RPC_PORT=int(os.getenv("BLENDER_RPC_PORT", 8765)),
        ROUTER_ENABLED=os.getenv("ROUTER_ENABLED", "true").lower() in ("true", "1", "yes"),
        ROUTER_LOG_DECISIONS=os.getenv("ROUTER_LOG_DECISIONS", "true").lower() in ("true", "1", "yes"),
        OTEL_ENABLED=os.getenv("OTEL_ENABLED", "false").lower() in ("true", "1", "yes"),
        OTEL_EXPORTER=os.getenv("OTEL_EXPORTER", "none"),
        OTEL_SERVICE_NAME=os.getenv("OTEL_SERVICE_NAME", "blender-ai-mcp"),
        MCP_SURFACE_PROFILE=os.getenv("MCP_SURFACE_PROFILE", "legacy-flat"),
        MCP_DEFAULT_CONTRACT_LINE=os.getenv("MCP_DEFAULT_CONTRACT_LINE") or None,
        MCP_LIST_PAGE_SIZE=int(os.getenv("MCP_LIST_PAGE_SIZE", 100)),
        MCP_TOOL_TIMEOUT_SECONDS=float(os.getenv("MCP_TOOL_TIMEOUT_SECONDS", 30.0)),
        MCP_TASK_TIMEOUT_SECONDS=float(os.getenv("MCP_TASK_TIMEOUT_SECONDS", 300.0)),
        RPC_TIMEOUT_SECONDS=float(os.getenv("RPC_TIMEOUT_SECONDS", 30.0)),
        ADDON_EXECUTION_TIMEOUT_SECONDS=float(os.getenv("ADDON_EXECUTION_TIMEOUT_SECONDS", 30.0)),
        VISION_ENABLED=os.getenv("VISION_ENABLED", "false").lower() in ("true", "1", "yes"),
        VISION_PROVIDER=os.getenv("VISION_PROVIDER", "transformers_local"),
        VISION_ALLOW_ON_GUIDED=os.getenv("VISION_ALLOW_ON_GUIDED", "true").lower() in ("true", "1", "yes"),
        VISION_MAX_IMAGES=int(os.getenv("VISION_MAX_IMAGES", 8)),
        VISION_MAX_TOKENS=int(os.getenv("VISION_MAX_TOKENS", 400)),
        VISION_TIMEOUT_SECONDS=float(os.getenv("VISION_TIMEOUT_SECONDS", 20.0)),
        VISION_LOCAL_MODEL_ID=os.getenv("VISION_LOCAL_MODEL_ID") or None,
        VISION_LOCAL_MODEL_PATH=os.getenv("VISION_LOCAL_MODEL_PATH") or None,
        VISION_LOCAL_DEVICE=os.getenv("VISION_LOCAL_DEVICE", "cpu"),
        VISION_LOCAL_DTYPE=os.getenv("VISION_LOCAL_DTYPE", "auto"),
        VISION_EXTERNAL_BASE_URL=os.getenv("VISION_EXTERNAL_BASE_URL") or None,
        VISION_EXTERNAL_MODEL=os.getenv("VISION_EXTERNAL_MODEL") or None,
        VISION_EXTERNAL_API_KEY=os.getenv("VISION_EXTERNAL_API_KEY") or None,
        VISION_EXTERNAL_API_KEY_ENV=os.getenv("VISION_EXTERNAL_API_KEY_ENV") or None,
    )
