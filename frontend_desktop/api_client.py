"""
HTTP client for FastAPI backend communication.
Handles all API calls with proper error handling.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests

logger = logging.getLogger(__name__)

# MIME type mapping for file uploads (matches backend ALLOWED_UPLOAD_TYPES)
MIME_TYPES = {
    '.txt': 'text/plain',
    '.csv': 'text/csv',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.xls': 'application/vnd.ms-excel',
    '.xlsm': 'application/vnd.ms-excel',
    '.pdf': 'application/pdf',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.gif': 'image/gif',
}


def get_mime_type(file_path: str) -> str:
    """Get MIME type for a file based on extension."""
    ext = Path(file_path).suffix.lower()
    return MIME_TYPES.get(ext, 'application/octet-stream')


class BackendClient:
    """Client for communicating with FastAPI backend."""

    def __init__(self, host: str = "http://localhost:8000", timeout: int = 180):
        """
        Initialize backend client.

        Args:
            host: Backend URL (default: http://localhost:8000)
            timeout: Request timeout in seconds (default: 180 for Ollama inference)
        """
        self.host = host
        self.timeout = timeout
        self.session = requests.Session()

    def _parse_error_response(self, response: requests.Response) -> str:
        """
        Parse error response and return user-friendly message.

        The backend returns structured errors with error_code for easy mapping.

        Args:
            response: Failed HTTP response

        Returns:
            User-friendly error message
        """
        try:
            data = response.json()
            error = data.get("error", "Unknown error")
            error_code = data.get("error_code", "")

            # Map error codes to user-friendly messages
            friendly_messages = {
                "BAD_REQUEST": f"Invalid request: {error}",
                "FILE_TOO_LARGE": "File is too large (max 50MB). Try a smaller file.",
                "SERVICE_UNAVAILABLE": "AI service is not available. Is Ollama running?",
                "VALIDATION_ERROR": f"Invalid input: {error}",
                "INTERNAL_ERROR": f"Server error: {error}",
                "NOT_FOUND": "The requested resource was not found.",
            }

            return friendly_messages.get(error_code, error)
        except Exception:
            # Fallback for non-JSON responses
            return f"Request failed: HTTP {response.status_code}"

    def health_check(self) -> bool:
        """Check if backend is running."""
        try:
            response = self.session.get(
                urljoin(self.host, "/health"),
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    def search_files_async(
        self,
        keywords: str,
        folders: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Start async file search.

        Args:
            keywords: Search keywords (space-separated)
            folders: List of folder paths to search (optional)

        Returns:
            {"search_id": "uuid", "success": true}
        """
        try:
            payload = {
                "keywords": keywords.split() if isinstance(keywords, str) else keywords,
                "file_types": [".xlsx", ".pdf", ".csv"]
            }
            if folders:
                payload["folders"] = folders

            response = self.session.post(
                urljoin(self.host, "/api/search/filename/async"),
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {"success": False, "error": str(e)}

    def get_search_progress(self, search_id: str) -> Dict[str, Any]:
        """
        Poll search progress.

        Args:
            search_id: Search ID from search_files_async

        Returns:
            {
                "status": "in_progress|completed|failed",
                "directories_scanned": 45,
                "files_found": 12,
                "current_directory": "C:\\Users\\...",
                "elapsed_seconds": 5.2,
                "results": [...] (if completed)
            }
        """
        try:
            response = self.session.get(
                urljoin(self.host, f"/api/search/progress/{search_id}"),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Get progress failed: {e}")
            return {"status": "failed", "error": str(e)}

    def get_search_history(self, limit: int = 20) -> Dict[str, Any]:
        """
        Get recent search history.

        Args:
            limit: Maximum number of searches to return

        Returns:
            {
                "success": bool,
                "history": [
                    {
                        "id": int,
                        "keywords": [list],
                        "folders": [list],
                        "search_count": int,
                        "created_at": str,
                        ...
                    },
                    ...
                ]
            }
        """
        try:
            response = self.session.get(
                urljoin(self.host, f"/api/search/history?limit={limit}"),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Get search history failed: {e}")
            return {"success": False, "history": [], "error": str(e)}

    def rerun_search(self, search_id: int) -> Dict[str, Any]:
        """
        Get a saved search by ID for re-running.

        Args:
            search_id: ID of the search to retrieve

        Returns:
            {
                "success": bool,
                "search": {
                    "id": int,
                    "keywords": [list],
                    "folders": [list],
                    "case_sensitive": bool,
                    "extensions": [list],
                    ...
                }
            }
        """
        try:
            response = self.session.post(
                urljoin(self.host, f"/api/search/history/{search_id}"),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Rerun search failed: {e}")
            return {"success": False, "error": str(e)}

    def delete_search_history(self, search_id: int) -> Dict[str, Any]:
        """Delete a search from history."""
        try:
            response = self.session.delete(
                urljoin(self.host, f"/api/search/history/{search_id}"),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Delete search history failed: {e}")
            return {"success": False, "error": str(e)}

    def add_to_search_history(self, keywords: List[str], folders: List[str],
                              exclude_keywords: Optional[List[str]] = None,
                              start_date: Optional[str] = None,
                              end_date: Optional[str] = None,
                              case_sensitive: bool = False,
                              extensions: Optional[List[str]] = None) -> Dict[str, Any]:
        """Add current search to history after search completes."""
        try:
            from pydantic import BaseModel

            class SearchHistoryRequest(BaseModel):
                keywords: List[str]
                folders: List[str]
                exclude_keywords: Optional[List[str]] = None
                start_date: Optional[str] = None
                end_date: Optional[str] = None
                case_sensitive: bool = False
                supported_extensions: Optional[List[str]] = None

            # Create request object (using dict to avoid needing Pydantic here)
            data = {
                "keywords": keywords,
                "folders": folders,
                "exclude_keywords": exclude_keywords or [],
                "start_date": start_date,
                "end_date": end_date,
                "case_sensitive": case_sensitive,
                "supported_extensions": extensions or []
            }

            response = self.session.post(
                urljoin(self.host, "/api/search/history"),
                json=data,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Add to search history failed: {e}")
            return {"success": False, "error": str(e)}

    def analyze_file(self, file_path: str, analysis_type: str = "summary") -> Dict[str, Any]:
        """
        Upload and analyze a file synchronously.

        The backend processes the file immediately and returns the complete result.
        This may take 30-120 seconds depending on file size and AI model.

        Args:
            file_path: Path to file (PDF/CSV/XLSX/TXT/image)
            analysis_type: Type of analysis (summary, key_points, anomalies, insights, trends)

        Returns:
            {
                "success": bool,
                "file_info": {"name": str, "size": int, "type": str, "pages": int},
                "analysis": str,
                "extracted_text": str (first 1000 chars),
                "latency_ms": float,
                "model": str,
                "timing": {...}
            }
        """
        try:
            # Get proper MIME type for the file
            mime_type = get_mime_type(file_path)
            filename = Path(file_path).name

            with open(file_path, 'rb') as f:
                # Include MIME type as third tuple element for proper content-type
                files = {'file': (filename, f, mime_type)}
                data = {'analysis_type': analysis_type}

                response = self.session.post(
                    urljoin(self.host, "/api/analyze"),
                    files=files,
                    data=data,
                    timeout=self.timeout  # Long timeout for AI inference
                )

            # Check for errors and return user-friendly messages
            if response.status_code != 200:
                error_msg = self._parse_error_response(response)
                return {"success": False, "error": error_msg}

            # Parse JSON response with explicit error handling
            try:
                result = response.json()
            except ValueError:
                logger.error("Invalid JSON response from server")
                return {"success": False, "error": "Invalid response from server"}

            result["success"] = True
            return result

        except requests.exceptions.Timeout:
            logger.error("Analysis timed out")
            return {"success": False, "error": "Analysis timed out. Try a smaller file."}
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to backend")
            return {"success": False, "error": "Cannot connect to backend. Is it running?"}
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {"success": False, "error": str(e)}

    def analyze_batch(self, file_paths: list, analysis_type: str = "summary") -> Dict[str, Any]:
        """
        Upload and analyze multiple files in batch.

        The backend processes files and returns individual analyses plus consolidated summary.

        Args:
            file_paths: List of file paths to analyze (2-100 files)
            analysis_type: Type of analysis (summary, key_points, anomalies, insights, trends, comparative)

        Returns:
            {
                "success": bool,
                "file_count": int,
                "successful": int,
                "failed": int,
                "analysis_type": str,
                "individual_analyses": [{...}, ...],
                "summary": str,
                "error": str (if failed)
            }
        """
        if not file_paths or len(file_paths) < 2:
            return {"success": False, "error": "Batch analysis requires at least 2 files"}

        if len(file_paths) > 100:
            return {"success": False, "error": "Maximum 100 files per batch"}

        try:
            files_to_upload = []

            # Prepare all files
            for file_path in file_paths:
                if not Path(file_path).exists():
                    logger.warning(f"File not found: {file_path}")
                    continue

                mime_type = get_mime_type(file_path)
                filename = Path(file_path).name

                with open(file_path, 'rb') as f:
                    file_content = f.read()
                    files_to_upload.append(
                        ('files', (filename, file_content, mime_type))
                    )

            if not files_to_upload:
                return {"success": False, "error": "No valid files to analyze"}

            # Send batch request
            data = {'analysis_type': analysis_type}

            response = self.session.post(
                urljoin(self.host, "/api/analyze/batch"),
                files=files_to_upload,
                data=data,
                timeout=self.timeout * 2  # Double timeout for batch processing
            )

            # Check for errors
            if response.status_code != 200:
                error_msg = self._parse_error_response(response)
                return {"success": False, "error": error_msg}

            # Parse response
            try:
                result = response.json()
            except ValueError:
                logger.error("Invalid JSON response from server")
                return {"success": False, "error": "Invalid response from server"}

            result["success"] = True
            return result

        except requests.exceptions.Timeout:
            logger.error("Batch analysis timed out")
            return {"success": False, "error": "Batch analysis timed out. Try fewer files or smaller files."}
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to backend")
            return {"success": False, "error": "Cannot connect to backend. Is it running?"}
        except Exception as e:
            logger.error(f"Batch analysis failed: {e}")
            return {"success": False, "error": str(e)}

    # Legacy method for backwards compatibility
    def upload_and_analyze(self, file_path: str) -> Dict[str, Any]:
        """
        Legacy method - redirects to analyze_file.
        Kept for backwards compatibility.
        """
        return self.analyze_file(file_path)

    def close(self):
        """Close HTTP session."""
        self.session.close()
