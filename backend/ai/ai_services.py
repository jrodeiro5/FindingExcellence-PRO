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

        Uses improved prompt engineering with examples and stricter requirements.
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": """You are a search query parser that converts natural language to structured search parameters.
You MUST respond with ONLY valid JSON, no other text. No explanations.

IMPORTANT RULES:
1. Extract SPECIFIC, CONCRETE keywords only - NO generic words like "file", "document", "data", "report"
2. Keywords should be 1-4 words max, case-insensitive
3. If user says "Q1", "Q2", "last month", "2025" - set date ranges, don't add to keywords
4. If unsure about dates, leave as null
5. Use exclude_keywords for items to exclude
6. Return empty arrays [] if no keywords found, not null

JSON schema (EXACTLY this format):
{
  "keywords": ["specific", "terms", "to", "find"],
  "exclude_keywords": ["terms", "to", "exclude"],
  "start_date": "YYYY-MM-DD or null",
  "end_date": "YYYY-MM-DD or null"
}

Examples:
- "Find budget spreadsheets" → {"keywords": ["budget"], "exclude_keywords": [], "start_date": null, "end_date": null}
- "Q3 financial reports excluding drafts" → {"keywords": ["financial"], "exclude_keywords": ["draft"], "start_date": "2025-07-01", "end_date": "2025-09-30"}
- "Sales data from last 30 days" → {"keywords": ["sales"], "exclude_keywords": [], "start_date": "2025-10-17", "end_date": null}
- "All PDF files" → {"keywords": [], "exclude_keywords": [], "start_date": null, "end_date": null}
"""
                },
                {"role": "user", "content": f"Parse this search query: {query}"}
            ]

            # Use faster model (DeepSeek R1 1.5B) for parsing - 3-5x faster than LLaMA 8B
            # JSON parsing doesn't require heavy reasoning, so speed is prioritized
            response, usage = self.ai.chat_completion(
                messages,
                model=self.ai.MODELS["general_fast"]  # deepseek-r1:1.5b
            )

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

            # Validate and clean keywords
            params = self._validate_search_params(params)

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

    def _validate_search_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and clean search parameters to prevent overly generic searches
        """
        # Generic/useless keywords to filter out
        generic_keywords = {
            'file', 'files', 'document', 'documents', 'data', 'info', 'information',
            'item', 'items', 'thing', 'things', 'all', 'any', 'find', 'search',
            'get', 'show', 'list', 'report', 'spreadsheet', 'excel', 'pdf'
        }

        # Clean keywords - remove generic terms
        keywords = params.get('keywords', [])
        if isinstance(keywords, list):
            keywords = [kw for kw in keywords if kw and kw.lower() not in generic_keywords]
        else:
            keywords = []

        # Ensure arrays are lists, not null
        exclude_keywords = params.get('exclude_keywords', [])
        if not isinstance(exclude_keywords, list):
            exclude_keywords = []

        return {
            "keywords": keywords,
            "exclude_keywords": exclude_keywords,
            "start_date": params.get('start_date'),
            "end_date": params.get('end_date')
        }

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
                "key_points": "Extract and list the key points from this document",
                "anomalies": "Detect anomalies or unusual data points",
                "insights": "Provide actionable business insights",
                "trends": "Identify key trends and patterns"
            }

            prompt = prompts.get(analysis_type, analysis_type)

            messages = [
                {
                    "role": "system",
                    "content": "You are an expert document analyst. Provide clear, concise analysis."
                },
                {
                    "role": "user",
                    "content": f"{prompt}\n\nDocument:\n{content[:1500]}"
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
