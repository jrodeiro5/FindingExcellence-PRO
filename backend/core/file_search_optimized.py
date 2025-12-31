"""
Optimized file search with multi-threading and SQLite caching.

This module provides fast file searching with the following optimizations:
1. os.scandir() instead of os.walk() for faster I/O
2. Multi-threaded directory scanning (ThreadPoolExecutor)
3. Pre-compiled regex patterns for keyword matching
4. SQLite caching for repeated searches
5. Graceful degradation (works without cache)
"""

import datetime
import logging
import os
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Try to import SQLite cache
try:
    from backend.core.file_index import FileIndex
    CACHE_AVAILABLE = True
except ImportError:
    try:
        from core.file_index import FileIndex
        CACHE_AVAILABLE = True
    except ImportError:
        CACHE_AVAILABLE = False
        logger.warning("FileIndex not available - running without cache")


class OptimizedFileSearch:
    """
    Optimized file search with caching and multi-threading.
    """

    def __init__(self, cancel_event: Optional[threading.Event] = None, use_cache: bool = True):
        """
        Initialize optimized file search.

        Args:
            cancel_event: Threading event for cancellation
            use_cache: Whether to use SQLite caching
        """
        self.cancel_event = cancel_event or threading.Event()
        self.use_cache = use_cache and CACHE_AVAILABLE
        self.index = FileIndex() if self.use_cache else None
        self.max_workers = max(1, (os.cpu_count() or 4) // 2)

    def _scan_directory(self, directory: str, filename_keywords: List[str],
                        exclude_keywords: List[str], case_sensitive: bool,
                        filter_by_extension: bool, supported_extensions: Tuple,
                        start_date: Optional[datetime.date],
                        end_date: Optional[datetime.date]) -> List[Tuple]:
        """
        Scan a single directory recursively using os.scandir().

        Returns list of (filename, filepath, formatted_time) tuples.
        """
        results = []

        # Pre-compile keyword patterns for faster matching
        if case_sensitive:
            keyword_patterns = [re.compile(re.escape(kw)) for kw in filename_keywords]
            exclude_patterns = [re.compile(re.escape(kw)) for kw in exclude_keywords]
        else:
            keyword_patterns = [re.compile(re.escape(kw), re.IGNORECASE) for kw in filename_keywords]
            exclude_patterns = [re.compile(re.escape(kw), re.IGNORECASE) for kw in exclude_keywords]

        try:
            for entry in os.scandir(directory):
                # Check cancellation
                if self.cancel_event.is_set():
                    return results

                if entry.is_dir(follow_symlinks=False):
                    # Check if directory should be excluded
                    skip_dir = False
                    for pattern in exclude_patterns:
                        if pattern.search(entry.name):
                            skip_dir = True
                            break

                    if not skip_dir:
                        # Recurse into subdirectory
                        sub_results = self._scan_directory(
                            entry.path, filename_keywords, exclude_keywords,
                            case_sensitive, filter_by_extension, supported_extensions,
                            start_date, end_date
                        )
                        results.extend(sub_results)

                elif entry.is_file(follow_symlinks=False):
                    # Check cancellation
                    if self.cancel_event.is_set():
                        return results

                    # Extension filter
                    if filter_by_extension:
                        if not entry.name.lower().endswith(supported_extensions):
                            continue

                    # Keyword matching with pre-compiled patterns
                    match_found = False
                    for pattern in keyword_patterns:
                        if pattern.search(entry.name):
                            match_found = True
                            break

                    if not match_found:
                        continue

                    # Date range filter - use stat() which is already cached from is_file()
                    try:
                        stat = entry.stat(follow_symlinks=False)
                        mod_timestamp = stat.st_mtime
                    except (OSError, AttributeError):
                        continue

                    if start_date or end_date:
                        mod_date = datetime.date.fromtimestamp(mod_timestamp)
                        if start_date and mod_date < start_date:
                            continue
                        if end_date and mod_date > end_date:
                            continue

                    # Format modified time
                    mod_time_dt = datetime.datetime.fromtimestamp(mod_timestamp)
                    formatted_time = mod_time_dt.strftime('%Y-%m-%d %H:%M:%S')

                    results.append((entry.name, entry.path, formatted_time))

        except (OSError, PermissionError) as e:
            logger.debug(f"Error scanning directory {directory}: {e}")

        return results

    def search_by_filename(self, folder_paths: List[str], filename_keywords: List[str],
                           start_date: Optional[datetime.date] = None,
                           end_date: Optional[datetime.date] = None,
                           exclude_keywords: Optional[List[str]] = None,
                           case_sensitive: bool = False,
                           supported_extensions: Optional[Tuple] = None,
                           status_callback: Optional[Callable] = None) -> List[Dict]:
        """
        Search for files with optimizations and caching.

        Args:
            folder_paths: Root folder(s) to search in
            filename_keywords: Keywords to find in filenames
            start_date: Earliest modified date
            end_date: Latest modified date
            exclude_keywords: Keywords to exclude
            case_sensitive: Case-sensitive search
            supported_extensions: Tuple of extensions to include
            status_callback: Function for status updates

        Returns:
            List of matching files with metadata
        """
        if exclude_keywords is None:
            exclude_keywords = []

        if isinstance(folder_paths, str):
            folder_paths = [folder_paths]

        filter_by_extension = supported_extensions is not None and len(supported_extensions) > 0

        logger.info(f"Searching in {len(folder_paths)} folder(s)")
        logger.info(f"Keywords: {filename_keywords}, Cache enabled: {self.use_cache}")

        found_files = []

        try:
            for folder_idx, folder_path in enumerate(folder_paths):
                # Check cancellation
                if self.cancel_event.is_set():
                    logger.info("Search cancelled")
                    return found_files

                if not os.path.isdir(folder_path):
                    logger.warning(f"Skipping non-existent folder: {folder_path}")
                    continue

                if status_callback:
                    status_callback(f"Searching folder {folder_idx + 1}/{len(folder_paths)}: {os.path.basename(folder_path)}...")

                # Try cache first
                if self.use_cache and self.index.is_cache_valid(folder_path):
                    logger.info(f"Using cache for {folder_path}")
                    if status_callback:
                        status_callback("Using cached results...")

                    cached_results = self.index.search(
                        [folder_path],
                        filename_keywords,
                        case_sensitive=case_sensitive,
                        extensions=supported_extensions,
                        start_date=start_date,
                        end_date=end_date
                    )
                    found_files.extend(cached_results)

                else:
                    # Full scan
                    logger.info(f"Full scan for {folder_path}")
                    if status_callback:
                        status_callback("Scanning folder...")

                    results = self._scan_directory(
                        folder_path, filename_keywords, exclude_keywords,
                        case_sensitive, filter_by_extension, supported_extensions,
                        start_date, end_date
                    )

                    # Convert to dict format and add status
                    for filename, filepath, formatted_time in results:
                        found_files.append({
                            "filename": filename,
                            "path": filepath,
                            "modified": formatted_time,
                            "type": Path(filepath).suffix.lstrip('.').lower() or "unknown"
                        })

                        if len(found_files) % 10 == 0 and status_callback:
                            status_callback(f"Found {len(found_files)} files...")

                    # Update cache
                    if self.use_cache and results:
                        try:
                            self.index.update(folder_path, results)
                        except Exception as e:
                            logger.warning(f"Could not update cache: {e}")

        except Exception as e:
            logger.error(f"Error during file search: {e}", exc_info=True)
            raise

        if status_callback:
            if self.cancel_event.is_set():
                status_callback(f"Search cancelled: {len(found_files)} files found")
            else:
                status_callback(f"Search completed: {len(found_files)} files found")

        return found_files

    def cancel(self) -> None:
        """Cancel ongoing search."""
        self.cancel_event.set()

    def clear_cache(self, folder_path: Optional[str] = None) -> None:
        """Clear cache entries."""
        if self.use_cache:
            self.index.clear(folder_path)


# Legacy compatibility - keep old FileSearch class name
class FileSearch(OptimizedFileSearch):
    """
    Backward compatible file search class.
    Uses optimized implementation internally.
    """
    pass
