"""Tests for the lazy local transformers vision backend scaffold."""

from __future__ import annotations

import asyncio
import importlib

import pytest

from server.adapters.mcp.vision import (
    MLXLocalVisionBackend,
    TransformersLocalVisionBackend,
    VisionBackendUnavailableError,
    VisionImageInput,
    VisionRequest,
    build_vision_runtime_config,
)
from server.infrastructure.config import Config


def _config(**overrides) -> Config:
    payload = {
        "BLENDER_RPC_HOST": "127.0.0.1",
        "BLENDER_RPC_PORT": 8765,
        "ROUTER_ENABLED": True,
        "ROUTER_LOG_DECISIONS": True,
        "OTEL_ENABLED": False,
        "OTEL_EXPORTER": "none",
        "OTEL_SERVICE_NAME": "blender-ai-mcp",
        "MCP_SURFACE_PROFILE": "llm-guided",
        "MCP_DEFAULT_CONTRACT_LINE": None,
        "MCP_LIST_PAGE_SIZE": 100,
        "MCP_TOOL_TIMEOUT_SECONDS": 30.0,
        "MCP_TASK_TIMEOUT_SECONDS": 300.0,
        "RPC_TIMEOUT_SECONDS": 30.0,
        "ADDON_EXECUTION_TIMEOUT_SECONDS": 30.0,
        "VISION_ENABLED": True,
        "VISION_PROVIDER": "transformers_local",
        "VISION_ALLOW_ON_GUIDED": True,
        "VISION_MAX_IMAGES": 6,
        "VISION_MAX_TOKENS": 400,
        "VISION_TIMEOUT_SECONDS": 20.0,
        "VISION_LOCAL_MODEL_ID": "Qwen/Qwen3-VL-4B-Instruct",
        "VISION_LOCAL_MODEL_PATH": None,
        "VISION_LOCAL_DEVICE": "cpu",
        "VISION_LOCAL_DTYPE": "auto",
        "VISION_MLX_MODEL_ID": None,
        "VISION_MLX_MODEL_PATH": None,
        "VISION_EXTERNAL_BASE_URL": None,
        "VISION_EXTERNAL_MODEL": None,
        "VISION_EXTERNAL_API_KEY": None,
        "VISION_EXTERNAL_API_KEY_ENV": None,
    }
    payload.update(overrides)
    return Config(**payload)


def test_local_backend_init_does_not_import_heavy_runtime(monkeypatch):
    calls: list[str] = []

    def _fake_import(name: str):
        calls.append(name)
        raise AssertionError("init should not import runtime modules")

    monkeypatch.setattr(importlib, "import_module", _fake_import)

    runtime = build_vision_runtime_config(_config())
    backend = TransformersLocalVisionBackend(runtime)

    assert backend.model_name == "Qwen/Qwen3-VL-4B-Instruct"
    assert calls == []


def test_local_backend_analyze_imports_runtime_lazily_and_fails_cleanly(monkeypatch, tmp_path):
    image_path = tmp_path / "before.png"
    image_path.write_bytes(b"fake-png")
    request = VisionRequest(goal="goal", images=(VisionImageInput(path=str(image_path), role="before"),))

    calls: list[str] = []

    def _fake_import(name: str):
        calls.append(name)
        if name == "transformers":
            return object()
        if name == "torch":
            return object()
        raise ModuleNotFoundError(name)

    monkeypatch.setattr(importlib, "import_module", _fake_import)

    backend = TransformersLocalVisionBackend(build_vision_runtime_config(_config()))

    with pytest.raises(VisionBackendUnavailableError, match="AutoProcessor and AutoModelForImageTextToText"):
        asyncio.run(backend.analyze(request))

    assert calls == ["transformers", "torch"]


def test_local_backend_reports_missing_optional_dependencies(monkeypatch, tmp_path):
    image_path = tmp_path / "after.png"
    image_path.write_bytes(b"fake-png")
    request = VisionRequest(goal="goal", images=(VisionImageInput(path=str(image_path), role="after"),))

    def _missing_import(name: str):
        raise ModuleNotFoundError(name)

    monkeypatch.setattr(importlib, "import_module", _missing_import)

    backend = TransformersLocalVisionBackend(build_vision_runtime_config(_config()))

    with pytest.raises(VisionBackendUnavailableError, match="optional runtime dependencies"):
        asyncio.run(backend.analyze(request))


def test_local_backend_analyze_runs_generic_transformers_flow(monkeypatch, tmp_path):
    image_path = tmp_path / "before.png"
    image_path.write_bytes(b"fake-png")
    request = VisionRequest(goal="goal", images=(VisionImageInput(path=str(image_path), role="before"),))

    class FakeTensor(list):
        def to(self, device):
            return self

    class FakeInputs(dict):
        def __init__(self):
            super().__init__({"input_ids": FakeTensor([[1, 2, 3]])})
            self.input_ids = self["input_ids"]

        def to(self, device):
            return self

    class FakeProcessor:
        def __init__(self):
            self.messages = None

        @classmethod
        def from_pretrained(cls, model_source):
            instance = cls()
            instance.model_source = model_source
            return instance

        def apply_chat_template(self, messages, **kwargs):
            self.messages = messages
            return FakeInputs()

        def batch_decode(self, generated_ids, **kwargs):
            return [
                '{"goal_summary":"Closer to the goal.","reference_match_summary":null,"visible_changes":["Front changed."],"likely_issues":[],"recommended_checks":[],"confidence":0.5,"captures_used":["before_1"]}'
            ]

    class FakeModel:
        device = "cpu"

        @classmethod
        def from_pretrained(cls, model_source, **kwargs):
            instance = cls()
            instance.model_source = model_source
            instance.kwargs = kwargs
            return instance

        def to(self, device):
            self.device = device
            return self

        def generate(self, **kwargs):
            return [[1, 2, 3, 4, 5]]

    class FakeTransformers:
        AutoProcessor = FakeProcessor
        AutoModelForImageTextToText = FakeModel

    class FakeTorch:
        float32 = "float32"
        float16 = "float16"
        bfloat16 = "bfloat16"

    def _fake_import(name: str):
        if name == "transformers":
            return FakeTransformers
        if name == "torch":
            return FakeTorch
        raise ModuleNotFoundError(name)

    monkeypatch.setattr(importlib, "import_module", _fake_import)

    backend = TransformersLocalVisionBackend(
        build_vision_runtime_config(_config(VISION_LOCAL_DEVICE="cpu", VISION_LOCAL_DTYPE="float16"))
    )

    result = asyncio.run(backend.analyze(request))

    assert result["backend_kind"] == "transformers_local"
    assert result["model_name"] == "Qwen/Qwen3-VL-4B-Instruct"
    assert result["goal_summary"] == "Closer to the goal."
    assert result["input_summary"]["before_image_count"] == 1
    assert backend._processor is not None
    assert backend._processor.messages is not None
    assert backend.last_output_diagnostics is not None
    assert backend.last_output_diagnostics["payload_shape"] == "contract"


def test_local_backend_rejects_invalid_json_output(monkeypatch, tmp_path):
    image_path = tmp_path / "after.png"
    image_path.write_bytes(b"fake-png")
    request = VisionRequest(goal="goal", images=(VisionImageInput(path=str(image_path), role="after"),))

    class FakeInputs(dict):
        def __init__(self):
            super().__init__({"input_ids": [[1, 2, 3]]})
            self.input_ids = self["input_ids"]

        def to(self, device):
            return self

    class FakeProcessor:
        @classmethod
        def from_pretrained(cls, model_source):
            return cls()

        def apply_chat_template(self, messages, **kwargs):
            return FakeInputs()

        def batch_decode(self, generated_ids, **kwargs):
            return ["not-json"]

    class FakeModel:
        device = "cpu"

        @classmethod
        def from_pretrained(cls, model_source, **kwargs):
            return cls()

        def to(self, device):
            return self

        def generate(self, **kwargs):
            return [[1, 2, 3, 4]]

    class FakeTransformers:
        AutoProcessor = FakeProcessor
        AutoModelForImageTextToText = FakeModel

    class FakeTorch:
        float32 = "float32"
        float16 = "float16"
        bfloat16 = "bfloat16"

    def _fake_import(name: str):
        if name == "transformers":
            return FakeTransformers
        if name == "torch":
            return FakeTorch
        raise ModuleNotFoundError(name)

    monkeypatch.setattr(importlib, "import_module", _fake_import)

    backend = TransformersLocalVisionBackend(build_vision_runtime_config(_config()))

    with pytest.raises(VisionBackendUnavailableError, match="valid JSON"):
        asyncio.run(backend.analyze(request))


def test_mlx_local_backend_reports_missing_optional_dependency(monkeypatch, tmp_path):
    image_path = tmp_path / "mlx.png"
    image_path.write_bytes(b"fake-png")
    request = VisionRequest(goal="goal", images=(VisionImageInput(path=str(image_path), role="before"),))

    def _fake_import(name: str):
        raise ModuleNotFoundError(name)

    monkeypatch.setattr(importlib, "import_module", _fake_import)

    backend = MLXLocalVisionBackend(
        build_vision_runtime_config(
            _config(
                VISION_PROVIDER="mlx_local",
                VISION_MLX_MODEL_ID="mlx-community/Qwen3-VL-4B-Instruct-4bit",
                VISION_LOCAL_MODEL_ID=None,
            )
        )
    )

    with pytest.raises(VisionBackendUnavailableError, match="mlx-vlm"):
        asyncio.run(backend.analyze(request))


def test_mlx_local_backend_runs_generic_mlx_vlm_flow(monkeypatch, tmp_path):
    image_path = tmp_path / "mlx2.png"
    image_path.write_bytes(b"fake-png")
    request = VisionRequest(goal="goal", images=(VisionImageInput(path=str(image_path), role="before"),))

    class FakeGenerationResult:
        def __init__(self, text: str) -> None:
            self.text = text

    class FakeMLXVLM:
        @staticmethod
        def load(model_source):
            return "model", "processor"

        @staticmethod
        def generate(model, processor, *args, **kwargs):
            return FakeGenerationResult(
                '{"goal_summary":"Closer to the goal.","reference_match_summary":null,"visible_changes":["Front changed."],"likely_issues":[],"recommended_checks":[],"confidence":0.5,"captures_used":["before_1"]}'
            )

    class FakePromptUtils:
        @staticmethod
        def apply_chat_template(processor, config, prompt_payload, num_images=0):
            return f"PROMPT::{num_images}"

    class FakeUtils:
        @staticmethod
        def load_config(model_source):
            return {"model_source": model_source}

    def _fake_import(name: str):
        if name == "mlx_vlm":
            return FakeMLXVLM
        if name == "mlx_vlm.prompt_utils":
            return FakePromptUtils
        if name == "mlx_vlm.utils":
            return FakeUtils
        raise ModuleNotFoundError(name)

    monkeypatch.setattr(importlib, "import_module", _fake_import)

    backend = MLXLocalVisionBackend(
        build_vision_runtime_config(
            _config(
                VISION_PROVIDER="mlx_local",
                VISION_MLX_MODEL_ID="mlx-community/Qwen3-VL-4B-Instruct-4bit",
                VISION_LOCAL_MODEL_ID=None,
            )
        )
    )

    result = asyncio.run(backend.analyze(request))

    assert result["backend_kind"] == "mlx_local"
    assert result["model_name"] == "mlx-community/Qwen3-VL-4B-Instruct-4bit"
    assert result["goal_summary"] == "Closer to the goal."
    assert backend.last_output_diagnostics is not None
    assert backend.last_output_diagnostics["payload_shape"] == "contract"


def test_mlx_local_backend_repairs_comparison_only_json(monkeypatch, tmp_path):
    image_path = tmp_path / "mlx_comparison.png"
    image_path.write_bytes(b"fake-png")
    request = VisionRequest(goal="goal", images=(VisionImageInput(path=str(image_path), role="before"),))

    class FakeGenerationResult:
        def __init__(self, text: str) -> None:
            self.text = text

    class FakeMLXVLM:
        @staticmethod
        def load(model_source):
            return "model", "processor"

        @staticmethod
        def generate(model, processor, *args, **kwargs):
            return FakeGenerationResult('{"comparison":"The after state is closer to the rounded target."}')

    class FakePromptUtils:
        @staticmethod
        def apply_chat_template(processor, config, prompt_payload, num_images=0):
            return f"PROMPT::{num_images}"

    class FakeUtils:
        @staticmethod
        def load_config(model_source):
            return {"model_source": model_source}

    def _fake_import(name: str):
        if name == "mlx_vlm":
            return FakeMLXVLM
        if name == "mlx_vlm.prompt_utils":
            return FakePromptUtils
        if name == "mlx_vlm.utils":
            return FakeUtils
        raise ModuleNotFoundError(name)

    monkeypatch.setattr(importlib, "import_module", _fake_import)

    backend = MLXLocalVisionBackend(
        build_vision_runtime_config(
            _config(
                VISION_PROVIDER="mlx_local",
                VISION_MLX_MODEL_ID="mlx-community/Qwen3-VL-4B-Instruct-4bit",
                VISION_LOCAL_MODEL_ID=None,
            )
        )
    )

    result = asyncio.run(backend.analyze(request))

    assert result["goal_summary"] == "The after state is closer to the rounded target."
    assert result["likely_issues"] == []


def test_mlx_local_backend_rejects_invalid_json_output(monkeypatch, tmp_path):
    image_path = tmp_path / "mlx3.png"
    image_path.write_bytes(b"fake-png")
    request = VisionRequest(goal="goal", images=(VisionImageInput(path=str(image_path), role="before"),))

    class FakeMLXVLM:
        @staticmethod
        def load(model_source):
            return "model", "processor"

        @staticmethod
        def generate(model, processor, *args, **kwargs):
            return "not-json"

    class FakePromptUtils:
        @staticmethod
        def apply_chat_template(processor, config, prompt_payload, num_images=0):
            return "PROMPT"

    class FakeUtils:
        @staticmethod
        def load_config(model_source):
            return {"model_source": model_source}

    def _fake_import(name: str):
        if name == "mlx_vlm":
            return FakeMLXVLM
        if name == "mlx_vlm.prompt_utils":
            return FakePromptUtils
        if name == "mlx_vlm.utils":
            return FakeUtils
        raise ModuleNotFoundError(name)

    monkeypatch.setattr(importlib, "import_module", _fake_import)

    backend = MLXLocalVisionBackend(
        build_vision_runtime_config(
            _config(
                VISION_PROVIDER="mlx_local",
                VISION_MLX_MODEL_ID="mlx-community/Qwen3-VL-4B-Instruct-4bit",
                VISION_LOCAL_MODEL_ID=None,
            )
        )
    )

    with pytest.raises(VisionBackendUnavailableError, match="valid JSON"):
        asyncio.run(backend.analyze(request))
