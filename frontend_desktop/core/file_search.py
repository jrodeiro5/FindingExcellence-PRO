"""
File search module - optimized with caching.

Pure Python implementation - no API dependencies.
Uses optimized scanner with os.scandir(), regex patterns, and SQLite caching.

For optimized implementation, see ../../backend/core/file_search_optimized.py
"""

import sys
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import optimized implementation
try:
    from backend.core.file_search_optimized import FileSearch, OptimizedFileSearch
except ImportError:
    # Fallback if imports don't work
    import logging
    logging.warning("Could not import optimized file search, using basic implementation")
    from core.file_search_optimized import FileSearch, OptimizedFileSearch

__all__ = ['FileSearch', 'OptimizedFileSearch']
