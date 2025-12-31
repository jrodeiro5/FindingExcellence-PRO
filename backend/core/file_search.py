"""
File search module - optimized with caching.

This module provides fast file searching with the following optimizations:
- os.scandir() instead of os.walk() for faster I/O
- Pre-compiled regex patterns for keyword matching
- SQLite caching for repeated searches
- Graceful degradation (works without cache)

For optimized implementation, see file_search_optimized.py
"""

# Import optimized implementation
from backend.core.file_search_optimized import FileSearch, OptimizedFileSearch

__all__ = ['FileSearch', 'OptimizedFileSearch']
