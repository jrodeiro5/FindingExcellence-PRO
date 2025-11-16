"""AI services layer - high-level AI features using local Ollama models"""
import json
import logging
from typing import Any, Dict, List, Optional

from .ollama_client import OllamaClient

logger = logging.getLogger(__name__)


class AISearchService:
    """AI-powered search and analysis services"""

    def __init__(self, ollama_host: Optional[str] = None):
        """Initialize with Ollama client

        Args:
            ollama_host: Ollama API host (default: http://localhost:11434)
        """
        try:
            self.ai = OllamaClient(host=ollama_host)
        except ConnectionError as e:
            logger.warning(f"Ollama initialization failed: {e}")
            raise

    def natural_language_search(self, query: str) -> Dict[str, Any]:
        """
        Convert natural language query to search parameters

        Example: "Find budget files from last month"
        → {"keywords": ["budget"], "start_date": "2025-10-01"}
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": """You are a search query parser. Convert natural language search queries to JSON.
You MUST respond with ONLY valid JSON, no other text.
JSON schema: {
  "keywords": ["list", "of", "search", "terms"],
  "exclude_keywords": ["optional", "exclusions"],
  "start_date": "YYYY-MM-DD or null",
  "end_date": "YYYY-MM-DD or null"
}"""
                },
                {"role": "user", "content": f"Parse this search query: {query}"}
            ]

            response, usage = self.ai.chat_completion(messages)

            # Parse JSON from response (may have extra whitespace)
            json_str = response.strip()
            # Try to extract JSON if model added extra text
            if not json_str.startswith('{'):
                start_idx = json_str.find('{')
                if start_idx != -1:
                    json_str = json_str[start_idx:]
            if not json_str.endswith('}'):
                end_idx = json_str.rfind('}')
                if end_idx != -1:
                    json_str = json_str[:end_idx+1]

            params = json.loads(json_str)
            logger.info(f"NL search parsed: {params} | Latency: {usage.latency_ms:.0f}ms")

            return {
                "success": True,
                "search_params": params,
                "latency_ms": usage.latency_ms,
                "model": usage.model
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from response: {e}")
            return {"success": False, "error": f"Invalid JSON response: {str(e)}"}
        except Exception as e:
            logger.error(f"Natural language search failed: {e}")
            return {"success": False, "error": str(e)}

    def analyze_document(
        self,
        content: str,
        analysis_type: str = "summary"
    ) -> Dict[str, Any]:
        """
        AI-powered document analysis

        Args:
            content: Document content (text or truncated for large files)
            analysis_type: summary, trends, anomalies, insights

        Returns:
            Analysis result from AI
        """
        try:
            prompts = {
                "summary": "Provide a concise summary of this document",
                "trends": "Identify key trends and patterns",
                "anomalies": "Detect anomalies or unusual data points",
                "insights": "Provide actionable business insights"
            }

            prompt = prompts.get(analysis_type, analysis_type)

            messages = [
                {
                    "role": "system",
                    "content": "You are an expert document analyst. Provide clear, structured analysis."
                },
                {
                    "role": "user",
                    "content": f"{prompt}\n\nDocument:\n{content[:3000]}"
                }
            ]

            response, usage = self.ai.chat_completion(messages)

            logger.info(f"Document analysis ({analysis_type}): Latency {usage.latency_ms:.0f}ms")

            return {
                "success": True,
                "analysis": response,
                "analysis_type": analysis_type,
                "latency_ms": usage.latency_ms,
                "model": usage.model
            }

        except Exception as e:
            logger.error(f"Document analysis failed: {e}")
            return {"success": False, "error": str(e)}

    def ocr_from_image(
        self,
        image_url: str,
        extract_tables: bool = False
    ) -> Dict[str, Any]:
        """
        Extract text/tables from image using vision models

        Args:
            image_url: URL or base64 of image
            extract_tables: Whether to extract as structured tables

        Returns:
            Extracted text or table data
        """
        try:
            prompt = (
                "Extract all text and tables as structured markdown. "
                "For tables, use pipe-separated format."
                if extract_tables
                else "Extract all text from this image."
            )

            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ]

            response, usage = self.ai.vision_completion(messages)

            logger.info(f"OCR from image: Latency {usage.latency_ms:.0f}ms")

            return {
                "success": True,
                "text": response,
                "extract_tables": extract_tables,
                "latency_ms": usage.latency_ms,
                "model": usage.model
            }

        except Exception as e:
            logger.error(f"Image OCR failed: {e}")
            return {"success": False, "error": str(e)}

    def semantic_search(
        self,
        content: str,
        query: str
    ) -> Dict[str, Any]:
        """
        Semantic search - find relevant content by meaning, not just keywords
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": "Find relevant sections from the document that answer the user's query. Focus on semantic meaning, not just keyword matching."
                },
                {
                    "role": "user",
                    "content": f"Document:\n{content[:2000]}\n\nFind relevant sections for: {query}"
                }
            ]

            response, usage = self.ai.chat_completion(messages)

            logger.info(f"Semantic search: Latency {usage.latency_ms:.0f}ms")

            return {
                "success": True,
                "results": response,
                "latency_ms": usage.latency_ms,
                "model": usage.model
            }

        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return {"success": False, "error": str(e)}

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get AI usage statistics"""
        return self.ai.get_usage_summary()
