"""Ollama local LLM client - 100% privacy, no external API calls

December 2025 Optimizations:
- Model warmup on startup (eliminates cold-start delay)
- OLLAMA_KEEP_ALIVE support (keeps model in memory)
- Smaller, faster models (qwen3:4b, deepseek-r1:1.5b)
- Reduced context window for speed
"""
import base64
import logging
import os
import threading
import time
from dataclasses import dataclass
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
    """Ollama client - local LLM inference with zero external dependencies

    December 2025 Optimizations:
    - Warmup models on init (background thread)
    - Keep models loaded with OLLAMA_KEEP_ALIVE
    - Use smaller, faster models
    - Configurable context window
    """

    # Model configuration for different tasks
    # December 2025 OPTIMIZED: phi4-mini (fast CPU inference) + deepseek-ocr (3B)
    # phi4-mini: Microsoft's latest small model, optimized for CPU speed
    # Performance: Very fast on CPU, good reasoning capabilities
    # Storage: ~2.5GB
    MODELS = {
        "general": "phi4-mini",  # phi4-mini: Fast CPU inference, good reasoning
        "general_fast": "phi4-mini",  # Same model for consistency
        "vision": "deepseek-ocr",  # DeepSeek-OCR (3B) - 97% accuracy, specialized for OCR
        "fallback_general": "qwen3:4b-instruct",  # Fallback to qwen3 if needed
    }

    FALLBACK_CHAINS = {
        "general": ["phi4-mini", "qwen3:4b-instruct", "qwen3:4b"],  # phi4-mini first, then qwen3
        "vision": ["deepseek-ocr"],  # Primary only - no fallback needed
    }

    # Default configuration (can be overridden via environment variables)
    # CPU optimization: smaller context and fewer tokens = faster inference
    DEFAULT_CONTEXT_SIZE = int(os.getenv("OLLAMA_CONTEXT_SIZE", "1024"))  # Smaller = faster
    DEFAULT_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.3"))
    DEFAULT_MAX_TOKENS = int(os.getenv("OLLAMA_MAX_TOKENS", "500"))  # Reduced for CPU speed

    # Keep models loaded in memory (December 2025 optimization)
    # Values: -1 (forever), 0 (unload immediately), "5m" (5 minutes), "1h" (1 hour)
    KEEP_ALIVE = os.getenv("OLLAMA_KEEP_ALIVE", "5m")  # Keep model in memory for 5 minutes

    def __init__(
        self,
        host: Optional[str] = None,
        app_url: str = "https://findingexcellence.app",
        app_name: str = "FindingExcellence_PRO",
        warmup: bool = True,
        warmup_async: bool = True,
    ):
        """Initialize Ollama client

        Args:
            host: Ollama API host (default: http://localhost:11434)
            app_url: Application URL for metadata
            app_name: Application name for metadata
            warmup: Whether to warmup models on init
            warmup_async: Run warmup in background thread
        """
        self.host = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.app_url = app_url
        self.app_name = app_name
        self.session = requests.Session()

        # Warmup state
        self._warmup_complete = threading.Event()
        self._warmed_models: set = set()

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

        # Warmup models (loads them into memory for faster first request)
        if warmup:
            if warmup_async:
                # Background warmup - doesn't block startup
                thread = threading.Thread(target=self._warmup_models, daemon=True)
                thread.start()
            else:
                # Blocking warmup - ensures models ready before first use
                self._warmup_models()

    def _check_ollama_health(self) -> bool:
        """Check if Ollama service is available"""
        try:
            response = self.session.get(f"{self.host}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama health check failed: {e}")
            return False

    def _warmup_models(self):
        """Warmup models by sending a minimal request

        This loads the model into memory, eliminating cold-start latency.
        Called automatically on init if warmup=True.
        """
        # Warmup the instruct model (phi4-mini - fast CPU inference)
        models_to_warmup = [
            self.MODELS["general"],  # phi4-mini
        ]

        for model in models_to_warmup:
            if model in self._warmed_models:
                continue

            try:
                logger.info(f"Warming up model: {model}...")
                start = time.time()

                # Send minimal request to load model
                response = self.session.post(
                    f"{self.host}/api/generate",
                    json={
                        "model": model,
                        "prompt": "Hi",
                        "stream": False,
                        "options": {
                            "num_predict": 1,  # Generate just 1 token
                            "num_ctx": 512,    # Minimal context
                        }
                    },
                    timeout=120,
                )

                if response.status_code == 200:
                    elapsed = time.time() - start
                    self._warmed_models.add(model)
                    logger.info(f"✓ Model {model} warmed up in {elapsed:.1f}s")
                else:
                    logger.warning(f"Warmup failed for {model}: {response.status_code}")

            except Exception as e:
                logger.warning(f"Warmup error for {model}: {e}")

        self._warmup_complete.set()
        logger.info(f"Model warmup complete. Warmed models: {list(self._warmed_models)}")

    def wait_for_warmup(self, timeout: float = 60.0) -> bool:
        """Wait for model warmup to complete

        Args:
            timeout: Maximum seconds to wait

        Returns:
            True if warmup completed, False if timeout
        """
        return self._warmup_complete.wait(timeout=timeout)

    def is_warmed_up(self, model: Optional[str] = None) -> bool:
        """Check if models are warmed up

        Args:
            model: Specific model to check, or None for any

        Returns:
            True if warmed up
        """
        if model:
            return model in self._warmed_models
        return self._warmup_complete.is_set()

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        use_fallback: bool = True,
        max_retries: int = 1,
        context_size: Optional[int] = None,
        **kwargs,
    ) -> tuple:
        """Call Ollama chat completion API

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (default: qwen3:4b)
            use_fallback: Try fallback models if primary fails
            max_retries: Number of retries
            context_size: Context window size (smaller = faster)
            **kwargs: Additional parameters (temperature, top_p, etc.)

        Returns:
            Tuple of (content, UsageStats)
        """
        if model is None:
            model = self.MODELS["general"]

        if context_size is None:
            context_size = self.DEFAULT_CONTEXT_SIZE

        models_to_try = (
            self.FALLBACK_CHAINS.get("general", [model])
            if use_fallback
            else [model]
        )
        last_error = None

        for model_name in models_to_try:
            try:
                start_time = time.time()

                # Call Ollama API with optimized settings
                # Disable thinking mode for faster inference (Qwen3, DeepSeek-R1)
                response = self.session.post(
                    f"{self.host}/api/chat",
                    json={
                        "model": model_name,
                        "messages": messages,
                        "stream": False,
                        "think": False,  # Disable thinking mode - 10x faster
                        "keep_alive": self.KEEP_ALIVE,  # Keep model in memory
                        "options": {
                            "temperature": kwargs.get("temperature", self.DEFAULT_TEMPERATURE),
                            "top_p": kwargs.get("top_p", 0.9),
                            "num_predict": kwargs.get("max_tokens", self.DEFAULT_MAX_TOKENS),
                            "num_ctx": context_size,  # Smaller context = faster
                        }
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

                # Mark model as warmed if not already
                if model_name not in self._warmed_models:
                    self._warmed_models.add(model_name)

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
        context_size: Optional[int] = None,
        **kwargs,
    ) -> tuple:
        """Call Ollama vision/multimodal completion

        Args:
            messages: List of message dicts with 'role' and 'content' (can include images)
            model: Vision model name (default: deepseek-ocr)
            use_fallback: Try fallback models if primary fails
            context_size: Context window size
            **kwargs: Additional parameters

        Returns:
            Tuple of (content, UsageStats)
        """
        if model is None:
            model = self.MODELS["vision"]

        if context_size is None:
            context_size = self.DEFAULT_CONTEXT_SIZE

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
                        "keep_alive": self.KEEP_ALIVE,  # Keep model in memory
                        "options": {
                            "temperature": kwargs.get("temperature", self.DEFAULT_TEMPERATURE),
                            "top_p": kwargs.get("top_p", 0.9),
                            "num_predict": kwargs.get("max_tokens", self.DEFAULT_MAX_TOKENS),
                            "num_ctx": context_size,
                        }
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

                # Mark model as warmed
                if model_name not in self._warmed_models:
                    self._warmed_models.add(model_name)

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
            "warmed_models": list(self._warmed_models),
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
