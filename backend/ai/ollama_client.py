"""Ollama local LLM client - 100% privacy, no external API calls"""
import base64
import json
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


@dataclass
class UsageStats:
    """Track usage statistics for local LLM inference"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float  # Local inference latency instead of cost
    model: str
    cached_tokens: int = 0


class OllamaClient:
    """Ollama client - local LLM inference with zero external dependencies"""

    # Model configuration for different tasks
    MODELS = {
        "general": "llama3.1:8b",  # Primary: best reasoning
        "general_fast": "deepseek-r1:1.5b",  # Fast ranking/secondary tasks
        "vision": "qwen2.5-vl:7b",  # OCR and image understanding
        "fallback_general": "llama3.1:8b",
    }

    FALLBACK_CHAINS = {
        "general": ["llama3.1:8b", "deepseek-r1:1.5b"],
        "vision": ["qwen2.5-vl:7b", "llava:7b"],
    }

    def __init__(
        self,
        host: Optional[str] = None,
        app_url: str = "https://findingexcellence.app",
        app_name: str = "FindingExcellence_PRO",
    ):
        """Initialize Ollama client

        Args:
            host: Ollama API host (default: http://localhost:11434)
            app_url: Application URL for metadata
            app_name: Application name for metadata
        """
        self.host = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.app_url = app_url
        self.app_name = app_name
        self.session = requests.Session()

        # Usage tracking
        self.total_cost = 0.0  # Kept for backward compatibility, always 0 for local
        self.total_requests = 0
        self.total_tokens = 0
        self.total_latency_ms = 0

        # Verify Ollama is running
        if not self._check_ollama_health():
            raise ConnectionError(
                f"Ollama service not running at {self.host}. "
                "Please install Ollama from https://ollama.com and run it."
            )

        logger.info(f"OllamaClient initialized: {app_name}")

    def _check_ollama_health(self) -> bool:
        """Check if Ollama service is available"""
        try:
            response = self.session.get(f"{self.host}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama health check failed: {e}")
            return False

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        use_fallback: bool = True,
        max_retries: int = 1,
        **kwargs,
    ) -> tuple:
        """Call Ollama chat completion API

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (default: llama3.1:8b)
            use_fallback: Try fallback models if primary fails
            max_retries: Number of retries
            **kwargs: Additional parameters (temperature, top_p, etc.)

        Returns:
            Tuple of (content, UsageStats)
        """
        if model is None:
            model = self.MODELS["general"]

        models_to_try = (
            self.FALLBACK_CHAINS.get("general", [model])
            if use_fallback
            else [model]
        )
        last_error = None

        for model_name in models_to_try:
            try:
                start_time = time.time()

                # Call Ollama API
                response = self.session.post(
                    f"{self.host}/api/chat",
                    json={
                        "model": model_name,
                        "messages": messages,
                        "stream": False,
                        "temperature": kwargs.get("temperature", 0.3),
                        "top_p": kwargs.get("top_p", 0.9),
                        "num_predict": kwargs.get("max_tokens", 2000),
                    },
                    timeout=120,
                )

                if response.status_code != 200:
                    raise Exception(
                        f"Ollama API error: {response.status_code} - {response.text}"
                    )

                data = response.json()
                content = data.get("message", {}).get("content", "")
                latency_ms = (time.time() - start_time) * 1000

                # Parse token counts from response
                prompt_tokens = data.get("prompt_eval_count", 0)
                completion_tokens = data.get("eval_count", 0)
                total_tokens = prompt_tokens + completion_tokens

                usage = UsageStats(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    latency_ms=latency_ms,
                    model=model_name,
                    cached_tokens=0,
                )

                self.total_requests += 1
                self.total_tokens += total_tokens
                self.total_latency_ms += latency_ms

                logger.info(
                    f"✓ {model_name} | Latency: {latency_ms:.0f}ms | Tokens: {total_tokens}"
                )
                return content, usage

            except Exception as e:
                last_error = e
                logger.warning(f"✗ {model_name}: {str(e)}")

        raise Exception(f"All models failed: {last_error}")

    def vision_completion(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        use_fallback: bool = True,
        **kwargs,
    ) -> tuple:
        """Call Ollama vision/multimodal completion

        Args:
            messages: List of message dicts with 'role' and 'content' (can include images)
            model: Vision model name (default: qwen2.5-vl:7b)
            use_fallback: Try fallback models if primary fails
            **kwargs: Additional parameters

        Returns:
            Tuple of (content, UsageStats)
        """
        if model is None:
            model = self.MODELS["vision"]

        models_to_try = (
            self.FALLBACK_CHAINS.get("vision", [model])
            if use_fallback
            else [model]
        )
        last_error = None

        for model_name in models_to_try:
            try:
                start_time = time.time()

                # Process messages to handle image URLs
                processed_messages = self._process_vision_messages(messages)

                response = self.session.post(
                    f"{self.host}/api/chat",
                    json={
                        "model": model_name,
                        "messages": processed_messages,
                        "stream": False,
                        "temperature": kwargs.get("temperature", 0.3),
                        "top_p": kwargs.get("top_p", 0.9),
                        "num_predict": kwargs.get("max_tokens", 2000),
                    },
                    timeout=120,
                )

                if response.status_code != 200:
                    raise Exception(
                        f"Ollama API error: {response.status_code} - {response.text}"
                    )

                data = response.json()
                content = data.get("message", {}).get("content", "")
                latency_ms = (time.time() - start_time) * 1000

                prompt_tokens = data.get("prompt_eval_count", 0)
                completion_tokens = data.get("eval_count", 0)
                total_tokens = prompt_tokens + completion_tokens

                usage = UsageStats(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    latency_ms=latency_ms,
                    model=model_name,
                    cached_tokens=0,
                )

                self.total_requests += 1
                self.total_tokens += total_tokens
                self.total_latency_ms += latency_ms

                logger.info(
                    f"✓ Vision: {model_name} | Latency: {latency_ms:.0f}ms"
                )
                return content, usage

            except Exception as e:
                last_error = e
                logger.warning(f"✗ {model_name}: {str(e)}")

        raise Exception(f"Vision models failed: {last_error}")

    def _process_vision_messages(
        self, messages: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Convert image URLs to base64 for Ollama

        Ollama expects images as base64 encoded data
        """
        processed = []
        for msg in messages:
            processed_msg = msg.copy()

            if "content" in msg and isinstance(msg["content"], list):
                # Handle multi-part content (text + images)
                processed_content = []
                for item in msg["content"]:
                    if isinstance(item, dict):
                        if item.get("type") == "image_url":
                            # Convert image URL to base64
                            image_url = item["image_url"]["url"]
                            image_data = self._load_image_as_base64(image_url)
                            processed_content.append(
                                {
                                    "type": "image",
                                    "image": image_data,
                                }
                            )
                        elif item.get("type") == "text":
                            processed_content.append(
                                {
                                    "type": "text",
                                    "text": item["text"],
                                }
                            )
                processed_msg["content"] = processed_content

            processed.append(processed_msg)

        return processed

    def _load_image_as_base64(self, image_source: str) -> str:
        """Load image from URL or file path and convert to base64"""
        try:
            if image_source.startswith("http://") or image_source.startswith(
                "https://"
            ):
                # Download from URL
                response = self.session.get(image_source, timeout=10)
                image_data = response.content
            else:
                # Load from file path
                with open(image_source, "rb") as f:
                    image_data = f.read()

            return base64.b64encode(image_data).decode("utf-8")
        except Exception as e:
            logger.error(f"Failed to load image from {image_source}: {e}")
            raise

    def get_usage_summary(self) -> Dict[str, Any]:
        """Get aggregated usage statistics

        Returns:
            Dict with total_requests, total_tokens, total_latency_ms, avg_latency_per_request
        """
        avg_latency = (
            self.total_latency_ms / self.total_requests
            if self.total_requests > 0
            else 0
        )

        return {
            "total_requests": self.total_requests,
            "total_tokens": self.total_tokens,
            "total_latency_ms": round(self.total_latency_ms, 0),
            "avg_latency_per_request": round(avg_latency, 0),
            "total_cost_usd": 0.0,  # Always zero for local LLM
        }

    def list_available_models(self) -> List[str]:
        """List all available models in Ollama"""
        try:
            response = self.session.get(f"{self.host}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
            return []
        except Exception as e:
            logger.warning(f"Failed to list models: {e}")
            return []

    def check_model_exists(self, model: str) -> bool:
        """Check if a specific model is available"""
        try:
            models = self.list_available_models()
            return any(m.startswith(model) for m in models)
        except Exception:
            return False

    def pull_model(self, model: str) -> bool:
        """Download a model from Ollama library

        This is a blocking operation - model download happens synchronously
        """
        try:
            logger.info(f"Pulling model {model}...")
            response = self.session.post(
                f"{self.host}/api/pull",
                json={"name": model, "stream": False},
                timeout=600,  # 10 minute timeout for large models
            )
            if response.status_code == 200:
                logger.info(f"✓ Model {model} pulled successfully")
                return True
            else:
                logger.error(f"Failed to pull model: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error pulling model {model}: {e}")
            return False
