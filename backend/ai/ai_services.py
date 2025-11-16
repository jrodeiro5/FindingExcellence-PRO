"""AI services layer - high-level AI features using OpenRouter"""
import logging
import json
from typing import Dict, List, Any, Optional
from .openrouter_client import OpenRouterClient

logger = logging.getLogger(__name__)


class AISearchService:
    """AI-powered search and analysis services"""
    
    def __init__(self, api_key: str):
        """Initialize with OpenRouter client"""
        self.ai = OpenRouterClient(api_key=api_key)
    
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
                    "content": "Convert natural language search queries to JSON with: keywords (list), exclude_keywords (list), start_date (YYYY-MM-DD or null), end_date (YYYY-MM-DD or null)"
                },
                {"role": "user", "content": query}
            ]
            
            response, usage = self.ai.chat_completion(
                messages,
                response_format={"type": "json_object"}
            )
            
            params = json.loads(response)
            logger.info(f"NL search parsed: {params} | Cost: ${usage.cost:.6f}")
            
            return {
                "success": True,
                "search_params": params,
                "cost": usage.cost,
                "model": usage.model
            }
        
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
            
            logger.info(f"Document analysis ({analysis_type}): Cost ${usage.cost:.6f}")
            
            return {
                "success": True,
                "analysis": response,
                "analysis_type": analysis_type,
                "cost": usage.cost,
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
            
            logger.info(f"OCR from image: Cost ${usage.cost:.6f}")
            
            return {
                "success": True,
                "text": response,
                "extract_tables": extract_tables,
                "cost": usage.cost,
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
            
            logger.info(f"Semantic search: Cost ${usage.cost:.6f}")
            
            return {
                "success": True,
                "results": response,
                "cost": usage.cost,
                "model": usage.model
            }
        
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return {"success": False, "error": str(e)}
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get AI usage statistics"""
        return self.ai.get_usage_summary()
