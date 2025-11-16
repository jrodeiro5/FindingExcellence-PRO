"""OpenRouter API client - unified AI model access"""
import json
import logging
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from openai import APIError, OpenAI, RateLimitError

logger = logging.getLogger(__name__)

@dataclass
class UsageStats:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost: float
    model: str
    cached_tokens: int = 0

class OpenRouterClient:
    """OpenRouter client - unified interface to 300+ AI models"""

    MODELS = {
        "general_free": "deepseek/deepseek-r1:free",
        "vision_free": "google/gemini-2.0-flash-exp:free",
        "general": "deepseek/deepseek-chat-v3.1",
        "vision": "qwen/qwen3-vl-8b",
        "fallback_general": "openai/gpt-4o-mini",
    }

    FALLBACK_CHAINS = {
        "general": ["deepseek/deepseek-r1:free", "deepseek/deepseek-chat-v3.1", "google/gemini-2.0-flash-exp:free"],
        "vision": ["google/gemini-2.0-flash-exp:free", "qwen/qwen3-vl-8b"]
    }

    def __init__(self, api_key: Optional[str] = None, app_url: str = "https://findingexcellence.app", app_name: str = "FindingExcellence_PRO"):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")

        self.client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=self.api_key)
        self.extra_headers = {"HTTP-Referer": app_url, "X-Title": app_name}
        self.total_cost = 0.0
        self.total_requests = 0
        self.total_tokens = 0
        logger.info(f"OpenRouterClient initialized: {app_name}")

    def chat_completion(self, messages: List[Dict[str, str]], model: Optional[str] = None, use_fallback: bool = True, max_retries: int = 3, **kwargs) -> tuple:
        if model is None:
            model = self.MODELS["general_free"]

        models_to_try = self.FALLBACK_CHAINS.get("general", [model]) if use_fallback else [model]
        last_error = None

        for model_name in models_to_try:
            try:
                response = self._call_with_retry(model_name, messages, max_retries, **kwargs)
                content = response.choices[0].message.content
                usage = self._extract_usage(response, model_name)
                self.total_requests += 1
                self.total_tokens += usage.total_tokens
                self.total_cost += usage.cost
                logger.info(f"✓ {model_name} | Cost: ${usage.cost:.6f}")
                return content, usage
            except Exception as e:
                last_error = e
                logger.warning(f"✗ {model_name}: {str(e)}")

        raise Exception(f"All models failed: {last_error}")

    def vision_completion(self, messages: List[Dict[str, Any]], model: Optional[str] = None, use_fallback: bool = True, **kwargs) -> tuple:
        if model is None:
            model = self.MODELS["vision_free"]

        models_to_try = self.FALLBACK_CHAINS.get("vision", [model]) if use_fallback else [model]
        last_error = None

        for model_name in models_to_try:
            try:
                response = self._call_with_retry(model_name, messages, 3, **kwargs)
                content = response.choices[0].message.content
                usage = self._extract_usage(response, model_name)
                self.total_requests += 1
                self.total_tokens += usage.total_tokens
                self.total_cost += usage.cost
                logger.info(f"✓ Vision: {model_name}")
                return content, usage
            except Exception as e:
                last_error = e
                logger.warning(f"✗ {model_name}")

        raise Exception(f"Vision models failed: {last_error}")

    def _call_with_retry(self, model: str, messages: List, max_retries: int, **kwargs):
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(model=model, messages=messages, extra_headers=self.extra_headers, extra_body={"usage": {"include": True}}, **kwargs)
                return response
            except RateLimitError as e:
                logger.warning(f"Rate limit hit for {model}, attempt {attempt + 1}/{max_retries}")
                if attempt == max_retries - 1:
                    raise
                wait_time = 2 ** attempt
                time.sleep(wait_time)
            except APIError as e:
                logger.warning(f"API error for {model}: {e}, attempt {attempt + 1}/{max_retries}")
                if attempt == max_retries - 1:
                    raise Exception(f"OpenRouter API error: {e}")
                time.sleep(1)
            except Exception as e:
                logger.warning(f"Unexpected error for {model}: {e}, attempt {attempt + 1}/{max_retries}")
                if attempt == max_retries - 1:
                    raise Exception(f"OpenRouter request failed: {e}")
                time.sleep(1)
        raise Exception("Max retries exceeded")

    def _extract_usage(self, response, model: str) -> UsageStats:
        usage = getattr(response, "usage", None)
        if usage:
            return UsageStats(
                prompt_tokens=getattr(usage, "prompt_tokens", 0),
                completion_tokens=getattr(usage, "completion_tokens", 0),
                total_tokens=getattr(usage, "total_tokens", 0),
                cost=getattr(usage, "cost", 0.0),
                model=model,
                cached_tokens=getattr(usage, "cached_tokens", 0)
            )
        return UsageStats(0, 0, 0, 0.0, model)

    def get_usage_summary(self) -> Dict[str, Any]:
        return {
            "total_requests": self.total_requests,
            "total_tokens": self.total_tokens,
            "total_cost_usd": round(self.total_cost, 6),
            "avg_cost_per_request": round(self.total_cost / self.total_requests if self.total_requests > 0 else 0, 6)
        }
