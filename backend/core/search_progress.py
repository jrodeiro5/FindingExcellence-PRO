"""
Search progress tracking module for long-running file searches.
Allows frontend to poll progress without blocking on full results.
"""

import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class SearchProgress:
    """Track progress of an ongoing search operation"""
    search_id: str
    status: str = "starting"  # starting, scanning, completed, cancelled, error
    directories_scanned: int = 0
    files_checked: int = 0
    files_found: int = 0
    current_directory: str = ""
    results: List[tuple] = field(default_factory=list)
    error: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.now)
    elapsed_seconds: float = 0.0
    estimated_remaining: float = 0.0

    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dictionary"""
        return {
            "search_id": self.search_id,
            "status": self.status,
            "directories_scanned": self.directories_scanned,
            "files_checked": self.files_checked,
            "files_found": self.files_found,
            "current_directory": self.current_directory,
            "results_count": len(self.results),
            "error": self.error,
            "elapsed_seconds": self.elapsed_seconds,
            "estimated_remaining": self.estimated_remaining,
        }


class SearchProgressTracker:
    """Manages progress tracking for multiple concurrent searches"""

    def __init__(self):
        self._searches: Dict[str, SearchProgress] = {}
        self._lock = threading.Lock()

    def create_search(self, search_id: str) -> SearchProgress:
        """Create a new search progress tracker"""
        with self._lock:
            progress = SearchProgress(search_id=search_id)
            self._searches[search_id] = progress
            return progress

    def get_progress(self, search_id: str) -> Optional[SearchProgress]:
        """Get current progress of a search"""
        with self._lock:
            return self._searches.get(search_id)

    def update_progress(self, search_id: str, **kwargs) -> bool:
        """Update progress fields for a search"""
        with self._lock:
            progress = self._searches.get(search_id)
            if progress:
                for key, value in kwargs.items():
                    if hasattr(progress, key):
                        setattr(progress, key, value)
                # Update elapsed time
                progress.elapsed_seconds = (datetime.now() - progress.start_time).total_seconds()
                return True
            return False

    def add_result(self, search_id: str, result: tuple) -> bool:
        """Add a result to the search"""
        with self._lock:
            progress = self._searches.get(search_id)
            if progress:
                progress.results.append(result)
                progress.files_found += 1
                return True
            return False

    def complete_search(self, search_id: str, results: Optional[List[tuple]] = None) -> bool:
        """Mark search as completed"""
        with self._lock:
            progress = self._searches.get(search_id)
            if progress:
                progress.status = "completed"
                if results:
                    progress.results = results
                progress.elapsed_seconds = (datetime.now() - progress.start_time).total_seconds()
                return True
            return False

    def cancel_search(self, search_id: str) -> bool:
        """Mark search as cancelled"""
        with self._lock:
            progress = self._searches.get(search_id)
            if progress:
                progress.status = "cancelled"
                progress.elapsed_seconds = (datetime.now() - progress.start_time).total_seconds()
                return True
            return False

    def error_search(self, search_id: str, error: str) -> bool:
        """Mark search as errored"""
        with self._lock:
            progress = self._searches.get(search_id)
            if progress:
                progress.status = "error"
                progress.error = error
                progress.elapsed_seconds = (datetime.now() - progress.start_time).total_seconds()
                return True
            return False

    def cleanup_search(self, search_id: str) -> bool:
        """Remove completed/cancelled search from memory"""
        with self._lock:
            if search_id in self._searches:
                del self._searches[search_id]
                return True
            return False
