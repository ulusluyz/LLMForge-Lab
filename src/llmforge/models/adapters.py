import asyncio
import time
import json
import os
import sys
import shlex
import requests
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from llmforge.models.base import ModelInfo, GenerationResponse, CapabilityStatus

class LocalLLMAdapter(ABC):
    """Abstract Base Class for Local LLM Adapters."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.history: List[Dict[str, str]] = []

    @abstractmethod
    async def start(self) -> bool:
        """Initialize process or connection check."""
        pass

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None, reset_session: bool = False) -> GenerationResponse:
        """Generate response for a prompt."""
        pass

    @abstractmethod
    async def inspect_model(self) -> ModelInfo:
        """Audit model parameters and metadata."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Cleanup process or resources."""
        pass

    def reset_history(self) -> None:
        self.history.clear()


class SubprocessCLIAdapter(LocalLLMAdapter):
    """Adapter for interacting with local CLI processes via stdin/stdout."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.command = config.get("command", f"{sys.executable} -u -m tests.fixtures.dummy_model")
        self.process: Optional[asyncio.subprocess.Process] = None

    async def start(self) -> bool:
        try:
            env = dict(os.environ)
            env["PYTHONUNBUFFERED"] = "1"
            cmd_args = shlex.split(self.command)
            self.process = await asyncio.create_subprocess_exec(
                *cmd_args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            return True
        except Exception as e:
            return False

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, reset_session: bool = False) -> GenerationResponse:
        if reset_session:
            self.reset_history()

        start_time = time.time()
        if not self.process or self.process.returncode is not None:
            started = await self.start()
            if not started:
                return GenerationResponse(
                    text="",
                    status="ERROR",
                    error_message="Failed to start subprocess",
                    execution_time_seconds=time.time() - start_time
                )

        payload = {
            "prompt": prompt,
            "system": system_prompt or "",
            "history": self.history if not reset_session else []
        }

        input_str = json.dumps(payload) + "\n"
        try:
            assert self.process is not None and self.process.stdin is not None and self.process.stdout is not None
            self.process.stdin.write(input_str.encode("utf-8"))
            await self.process.stdin.drain()

            line = await asyncio.wait_for(self.process.stdout.readline(), timeout=10.0)
            if not line:
                return GenerationResponse(text="", status="ERROR", error_message="Empty output from process", execution_time_seconds=time.time() - start_time)

            resp_json = json.loads(line.decode("utf-8").strip())
            response_text = resp_json.get("response", "")

            if not reset_session:
                self.history.append({"user": prompt, "assistant": response_text})

            return GenerationResponse(
                text=response_text,
                raw_response=resp_json,
                execution_time_seconds=time.time() - start_time,
                status="SUCCESS"
            )
        except Exception as e:
            return GenerationResponse(
                text="",
                status="ERROR",
                error_message=str(e),
                execution_time_seconds=time.time() - start_time
            )

    async def inspect_model(self) -> ModelInfo:
        return ModelInfo(
            model_name=self.config.get("model_name", "SubprocessModel"),
            model_type="CLI Subprocess",
            context_length=self.config.get("context_length", CapabilityStatus.UNKNOWN.value),
            tokenizer_info=CapabilityStatus.UNKNOWN.value,
            chat_template=CapabilityStatus.UNKNOWN.value,
            generation_parameters=self.config.get("generation_parameters", {})
        )

    async def stop(self) -> None:
        if self.process and self.process.returncode is None:
            try:
                self.process.terminate()
                await self.process.wait()
            except Exception:
                pass


class GenericHTTPAdapter(LocalLLMAdapter):
    """Adapter for generic OpenAI-compatible local HTTP endpoints."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.endpoint = config.get("endpoint", "http://127.0.0.1:11434/v1/chat/completions")
        self.model = config.get("model", "default")

    async def start(self) -> bool:
        return True

    async def generate(self, prompt: str, system_prompt: Optional[str] = None, reset_session: bool = False) -> GenerationResponse:
        if reset_session:
            self.reset_history()

        start_time = time.time()
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        for turn in self.history:
            messages.append({"role": "user", "content": turn["user"]})
            messages.append({"role": "assistant", "content": turn["assistant"]})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.config.get("temperature", 0.7)
        }

        try:
            res = requests.post(self.endpoint, json=payload, timeout=30)
            if res.status_code == 200:
                data = res.json()
                text = data["choices"][0]["message"]["content"]
                if not reset_session:
                    self.history.append({"user": prompt, "assistant": text})
                return GenerationResponse(
                    text=text,
                    raw_response=data,
                    execution_time_seconds=time.time() - start_time,
                    status="SUCCESS"
                )
            else:
                return GenerationResponse(
                    text="",
                    status="ERROR",
                    error_message=f"HTTP {res.status_code}: {res.text}",
                    execution_time_seconds=time.time() - start_time
                )
        except Exception as e:
            return GenerationResponse(
                text="",
                status="ERROR",
                error_message=str(e),
                execution_time_seconds=time.time() - start_time
            )

    async def inspect_model(self) -> ModelInfo:
        return ModelInfo(
            model_name=self.model,
            model_type="Generic HTTP / OpenAI Compatible",
            context_length=CapabilityStatus.UNKNOWN.value,
            tokenizer_info=CapabilityStatus.UNKNOWN.value,
            chat_template=CapabilityStatus.UNKNOWN.value,
            runtime_info={"endpoint": self.endpoint}
        )

    async def stop(self) -> None:
        pass


class OllamaAdapter(GenericHTTPAdapter):
    """Adapter specifically for Ollama local instances."""
    def __init__(self, config: Dict[str, Any]):
        if "endpoint" not in config:
            config["endpoint"] = "http://127.0.0.1:11434/v1/chat/completions"
        super().__init__(config)


class LlamaCppAdapter(GenericHTTPAdapter):
    """Adapter specifically for llama.cpp HTTP server instances."""
    def __init__(self, config: Dict[str, Any]):
        if "endpoint" not in config:
            config["endpoint"] = "http://127.0.0.1:8080/v1/chat/completions"
        super().__init__(config)


class VLLMAdapter(GenericHTTPAdapter):
    """Adapter specifically for vLLM OpenAI-compatible endpoints."""
    def __init__(self, config: Dict[str, Any]):
        if "endpoint" not in config:
            config["endpoint"] = "http://127.0.0.1:8000/v1/chat/completions"
        super().__init__(config)
