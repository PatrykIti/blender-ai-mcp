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
    MCP_TRANSPORT_MODE: str = Field(default="stdio", description="MCP transport mode: stdio|streamable")
    MCP_DEFAULT_CONTRACT_LINE: str | None = Field(default=None, description="Optional default public contract line")
    MCP_LIST_PAGE_SIZE: int = Field(default=100, description="Default MCP list page size")
    MCP_TOOL_TIMEOUT_SECONDS: float = Field(default=30.0, gt=0, description="Foreground MCP tool timeout")
    MCP_TASK_TIMEOUT_SECONDS: float = Field(default=300.0, gt=0, description="Background MCP task timeout")
    RPC_TIMEOUT_SECONDS: float = Field(default=30.0, gt=0, description="RPC socket timeout")
    ADDON_EXECUTION_TIMEOUT_SECONDS: float = Field(default=30.0, gt=0, description="Blender addon execution timeout")
    MCP_HTTP_HOST: str = Field(default="127.0.0.1", description="Host for streamable HTTP MCP mode")
    MCP_HTTP_PORT: int = Field(default=8000, gt=0, description="Port for streamable HTTP MCP mode")
    MCP_STREAMABLE_HTTP_PATH: str = Field(default="/mcp", description="HTTP path for streamable MCP mode")

    # Vision runtime scaffold
    VISION_ENABLED: bool = Field(default=False, description="Enable bounded vision-assist runtime")
    VISION_PROVIDER: str = Field(
        default="transformers_local",
        description="Vision backend provider: transformers_local|mlx_local|openai_compatible_external",
    )
    VISION_ALLOW_ON_GUIDED: bool = Field(default=True, description="Allow vision assistance on llm-guided")
    VISION_MAX_IMAGES: int = Field(default=8, gt=0, description="Maximum images per bounded vision request")
    VISION_MAX_TOKENS: int = Field(default=400, gt=0, description="Maximum output tokens for vision assistance")
    VISION_TIMEOUT_SECONDS: float = Field(default=20.0, gt=0, description="Timeout for one bounded vision request")
    VISION_LOCAL_MODEL_ID: str | None = Field(default=None, description="Local HF vision model id")
    VISION_LOCAL_MODEL_PATH: str | None = Field(default=None, description="Local HF vision model path")
    VISION_LOCAL_DEVICE: str = Field(default="cpu", description="Device for local vision backend")
    VISION_LOCAL_DTYPE: str = Field(default="auto", description="Dtype for local vision backend")
    VISION_MLX_MODEL_ID: str | None = Field(default=None, description="Local MLX vision model id")
    VISION_MLX_MODEL_PATH: str | None = Field(default=None, description="Local MLX vision model path")
    VISION_EXTERNAL_BASE_URL: str | None = Field(
        default=None, description="Base URL for external OpenAI-compatible vision"
    )
    VISION_EXTERNAL_MODEL: str | None = Field(
        default=None, description="Model name for external OpenAI-compatible vision"
    )
    VISION_EXTERNAL_API_KEY: str | None = Field(default=None, description="Inline API key for external vision endpoint")
    VISION_EXTERNAL_API_KEY_ENV: str | None = Field(
        default=None,
        description="Environment variable name containing the API key for external vision endpoint",
    )
    VISION_EXTERNAL_PROVIDER: str = Field(
        default="generic",
        description="Named external vision provider profile: generic|openrouter|google_ai_studio",
    )
    VISION_EXTERNAL_CONTRACT_PROFILE: str | None = Field(
        default=None,
        description="Optional external vision contract profile override: generic_full|google_family_compare",
    )
    VISION_OPENROUTER_BASE_URL: str | None = Field(
        default=None,
        description="Optional OpenRouter base URL override for vision; defaults to https://openrouter.ai/api/v1",
    )
    VISION_OPENROUTER_MODEL: str | None = Field(default=None, description="OpenRouter multimodal model id for vision")
    VISION_OPENROUTER_API_KEY: str | None = Field(default=None, description="Inline OpenRouter API key for vision")
    VISION_OPENROUTER_API_KEY_ENV: str | None = Field(
        default=None,
        description="Environment variable containing the OpenRouter API key for vision",
    )
    VISION_OPENROUTER_SITE_URL: str | None = Field(
        default=None,
        description="Optional HTTP-Referer / site URL sent to OpenRouter for ranking/analytics",
    )
    VISION_OPENROUTER_SITE_NAME: str | None = Field(
        default=None,
        description="Optional X-Title / site name sent to OpenRouter for ranking/analytics",
    )
    VISION_OPENROUTER_REQUIRE_PARAMETERS: bool = Field(
        default=True,
        description="Require OpenRouter to route only through providers that support the requested parameters",
    )
    VISION_OPENROUTER_ENABLE_RESPONSE_HEALING: bool = Field(
        default=True,
        description="Enable OpenRouter response-healing plugin for bounded JSON compare paths",
    )
    VISION_OPENROUTER_PREFER_JSON_OBJECT_FOR_QWEN: bool = Field(
        default=True,
        description="Use response_format=json_object for Qwen-family OpenRouter models instead of json_schema",
    )
    VISION_GEMINI_BASE_URL: str | None = Field(
        default=None,
        description="Optional Google AI Studio base URL override for vision; defaults to https://generativelanguage.googleapis.com/v1beta",
    )
    VISION_GEMINI_MODEL: str | None = Field(default=None, description="Google AI Studio Gemini model id for vision")
    VISION_GEMINI_API_KEY: str | None = Field(default=None, description="Inline Google AI Studio API key for vision")
    VISION_GEMINI_API_KEY_ENV: str | None = Field(
        default=None,
        description="Environment variable containing the Google AI Studio API key for vision",
    )
    VISION_SEGMENTATION_ENABLED: bool = Field(
        default=False,
        description="Enable optional part-segmentation sidecar for creature perception",
    )
    VISION_SEGMENTATION_PROVIDER: str = Field(
        default="generic_sidecar",
        description="Optional segmentation sidecar provider: generic_sidecar",
    )
    VISION_SEGMENTATION_ENDPOINT: str | None = Field(
        default=None,
        description="Endpoint/base URL for the optional segmentation sidecar",
    )
    VISION_SEGMENTATION_MODEL: str | None = Field(
        default=None,
        description="Optional model identifier for the segmentation sidecar",
    )
    VISION_SEGMENTATION_API_KEY: str | None = Field(
        default=None,
        description="Inline API key for the segmentation sidecar",
    )
    VISION_SEGMENTATION_API_KEY_ENV: str | None = Field(
        default=None,
        description="Environment variable containing the segmentation sidecar API key",
    )
    VISION_SEGMENTATION_TIMEOUT_SECONDS: float = Field(
        default=15.0,
        gt=0,
        description="Timeout for one optional segmentation sidecar request",
    )
    VISION_SEGMENTATION_MAX_PARTS: int = Field(
        default=16,
        gt=0,
        description="Maximum part outputs accepted from the optional segmentation sidecar",
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
    def validate_mcp_transport_mode(self):
        """Keep the MCP transport vocabulary explicit and bootstrap-safe."""

        if self.MCP_TRANSPORT_MODE not in {"stdio", "streamable"}:
            raise ValueError("MCP_TRANSPORT_MODE must be one of: stdio, streamable")
        if not self.MCP_STREAMABLE_HTTP_PATH.startswith("/"):
            raise ValueError("MCP_STREAMABLE_HTTP_PATH must start with '/'")
        return self

    @model_validator(mode="after")
    def validate_vision_provider(self):
        """Keep the vision provider vocabulary explicit."""

        if self.VISION_PROVIDER not in {"transformers_local", "mlx_local", "openai_compatible_external"}:
            raise ValueError(
                "VISION_PROVIDER must be one of: transformers_local, mlx_local, openai_compatible_external"
            )
        if self.VISION_EXTERNAL_PROVIDER not in {"generic", "openrouter", "google_ai_studio"}:
            raise ValueError("VISION_EXTERNAL_PROVIDER must be one of: generic, openrouter, google_ai_studio")
        if self.VISION_EXTERNAL_CONTRACT_PROFILE not in {None, "generic_full", "google_family_compare"}:
            raise ValueError("VISION_EXTERNAL_CONTRACT_PROFILE must be one of: generic_full, google_family_compare")
        if self.VISION_SEGMENTATION_PROVIDER not in {"generic_sidecar"}:
            raise ValueError("VISION_SEGMENTATION_PROVIDER must be one of: generic_sidecar")
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
        MCP_TRANSPORT_MODE=os.getenv("MCP_TRANSPORT_MODE", "stdio"),
        MCP_DEFAULT_CONTRACT_LINE=os.getenv("MCP_DEFAULT_CONTRACT_LINE") or None,
        MCP_LIST_PAGE_SIZE=int(os.getenv("MCP_LIST_PAGE_SIZE", 100)),
        MCP_TOOL_TIMEOUT_SECONDS=float(os.getenv("MCP_TOOL_TIMEOUT_SECONDS", 30.0)),
        MCP_TASK_TIMEOUT_SECONDS=float(os.getenv("MCP_TASK_TIMEOUT_SECONDS", 300.0)),
        RPC_TIMEOUT_SECONDS=float(os.getenv("RPC_TIMEOUT_SECONDS", 30.0)),
        ADDON_EXECUTION_TIMEOUT_SECONDS=float(os.getenv("ADDON_EXECUTION_TIMEOUT_SECONDS", 30.0)),
        MCP_HTTP_HOST=os.getenv("MCP_HTTP_HOST", "127.0.0.1"),
        MCP_HTTP_PORT=int(os.getenv("MCP_HTTP_PORT", 8000)),
        MCP_STREAMABLE_HTTP_PATH=os.getenv("MCP_STREAMABLE_HTTP_PATH", "/mcp"),
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
        VISION_MLX_MODEL_ID=os.getenv("VISION_MLX_MODEL_ID") or None,
        VISION_MLX_MODEL_PATH=os.getenv("VISION_MLX_MODEL_PATH") or None,
        VISION_EXTERNAL_BASE_URL=os.getenv("VISION_EXTERNAL_BASE_URL") or None,
        VISION_EXTERNAL_MODEL=os.getenv("VISION_EXTERNAL_MODEL") or None,
        VISION_EXTERNAL_API_KEY=os.getenv("VISION_EXTERNAL_API_KEY") or None,
        VISION_EXTERNAL_API_KEY_ENV=os.getenv("VISION_EXTERNAL_API_KEY_ENV") or None,
        VISION_EXTERNAL_PROVIDER=os.getenv("VISION_EXTERNAL_PROVIDER", "generic"),
        VISION_EXTERNAL_CONTRACT_PROFILE=os.getenv("VISION_EXTERNAL_CONTRACT_PROFILE") or None,
        VISION_OPENROUTER_BASE_URL=os.getenv("VISION_OPENROUTER_BASE_URL") or None,
        VISION_OPENROUTER_MODEL=os.getenv("VISION_OPENROUTER_MODEL") or None,
        VISION_OPENROUTER_API_KEY=os.getenv("VISION_OPENROUTER_API_KEY") or None,
        VISION_OPENROUTER_API_KEY_ENV=os.getenv("VISION_OPENROUTER_API_KEY_ENV") or None,
        VISION_OPENROUTER_SITE_URL=os.getenv("VISION_OPENROUTER_SITE_URL") or None,
        VISION_OPENROUTER_SITE_NAME=os.getenv("VISION_OPENROUTER_SITE_NAME") or None,
        VISION_OPENROUTER_REQUIRE_PARAMETERS=(
            os.getenv("VISION_OPENROUTER_REQUIRE_PARAMETERS", "true").lower() not in {"0", "false", "no"}
        ),
        VISION_OPENROUTER_ENABLE_RESPONSE_HEALING=(
            os.getenv("VISION_OPENROUTER_ENABLE_RESPONSE_HEALING", "true").lower() not in {"0", "false", "no"}
        ),
        VISION_OPENROUTER_PREFER_JSON_OBJECT_FOR_QWEN=(
            os.getenv("VISION_OPENROUTER_PREFER_JSON_OBJECT_FOR_QWEN", "true").lower() not in {"0", "false", "no"}
        ),
        VISION_GEMINI_BASE_URL=os.getenv("VISION_GEMINI_BASE_URL") or None,
        VISION_GEMINI_MODEL=os.getenv("VISION_GEMINI_MODEL") or None,
        VISION_GEMINI_API_KEY=os.getenv("VISION_GEMINI_API_KEY") or None,
        VISION_GEMINI_API_KEY_ENV=os.getenv("VISION_GEMINI_API_KEY_ENV") or None,
        VISION_SEGMENTATION_ENABLED=os.getenv("VISION_SEGMENTATION_ENABLED", "false").lower() in ("true", "1", "yes"),
        VISION_SEGMENTATION_PROVIDER=os.getenv("VISION_SEGMENTATION_PROVIDER", "generic_sidecar"),
        VISION_SEGMENTATION_ENDPOINT=os.getenv("VISION_SEGMENTATION_ENDPOINT") or None,
        VISION_SEGMENTATION_MODEL=os.getenv("VISION_SEGMENTATION_MODEL") or None,
        VISION_SEGMENTATION_API_KEY=os.getenv("VISION_SEGMENTATION_API_KEY") or None,
        VISION_SEGMENTATION_API_KEY_ENV=os.getenv("VISION_SEGMENTATION_API_KEY_ENV") or None,
        VISION_SEGMENTATION_TIMEOUT_SECONDS=float(os.getenv("VISION_SEGMENTATION_TIMEOUT_SECONDS", 15.0)),
        VISION_SEGMENTATION_MAX_PARTS=int(os.getenv("VISION_SEGMENTATION_MAX_PARTS", 16)),
    )
