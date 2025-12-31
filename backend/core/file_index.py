"""
SQLite-based file indexing for fast cached searches.

This module provides persistent caching of file metadata to enable
instant keyword searches without full filesystem scans.
"""

import logging
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class FileIndex:
    """SQLite-based file index for caching and fast searches."""

    def __init__(self, db_path: str = ".cache/file_index.db", cache_ttl: int = 3600):
        """
        Initialize file index.

        Args:
            db_path: Path to SQLite database file
            cache_ttl: Cache time-to-live in seconds (default: 1 hour)
        """
        self.db_path = db_path
        self.cache_ttl = cache_ttl
        self._init_db()

    def _init_db(self) -> None:
        """Create database schema if not exists."""
        # Create directory if needed
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create files table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                folder TEXT NOT NULL,
                filename TEXT NOT NULL,
                path TEXT UNIQUE NOT NULL,
                modified_time INTEGER,
                extension TEXT,
                indexed_at INTEGER NOT NULL
            )
        """)

        # Create indexes for fast searches
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_folder
            ON files(folder)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_filename
            ON files(filename COLLATE NOCASE)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_extension
            ON files(extension)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_indexed_at
            ON files(indexed_at)
        """)

        conn.commit()
        conn.close()

        logger.info(f"File index initialized at {self.db_path}")

    def is_cache_valid(self, folder_path: str) -> bool:
        """
        Check if cache for a folder is still valid (not expired).

        Args:
            folder_path: Path to check

        Returns:
            True if cache exists and is fresh, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT indexed_at FROM files
                WHERE folder = ?
                LIMIT 1
            """, (folder_path,))

            result = cursor.fetchone()
            conn.close()

            if result:
                indexed_at = result[0]
                current_time = int(datetime.now().timestamp())
                age = current_time - indexed_at

                is_valid = age < self.cache_ttl
                if is_valid:
                    logger.debug(f"Cache valid for {folder_path} (age: {age}s)")
                else:
                    logger.debug(f"Cache expired for {folder_path} (age: {age}s > {self.cache_ttl}s)")
                return is_valid

            logger.debug(f"No cache found for {folder_path}")
            return False

        except Exception as e:
            logger.error(f"Error checking cache validity: {e}")
            return False

    def search(self, folder_paths: List[str], keywords: List[str],
               case_sensitive: bool = False,
               extensions: Optional[Tuple] = None,
               start_date: Optional[datetime] = None,
               end_date: Optional[datetime] = None) -> List[Dict]:
        """
        Search indexed files by keywords.

        Args:
            folder_paths: List of folders to search in cache
            keywords: List of keywords to match
            case_sensitive: Whether search is case-sensitive
            extensions: Tuple of extensions to filter by
            start_date: Earliest modified date
            end_date: Latest modified date

        Returns:
            List of matching files with metadata
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            results = []

            for folder_path in folder_paths:
                # Build base query
                query = "SELECT filename, path, modified_time FROM files WHERE folder = ?"
                params = [folder_path]

                # Add keyword filters (AND logic - all keywords must match)
                for keyword in keywords:
                    if case_sensitive:
                        query += " AND filename LIKE ?"
                        params.append(f"%{keyword}%")
                    else:
                        query += " AND filename LIKE ? COLLATE NOCASE"
                        params.append(f"%{keyword}%")

                # Add extension filter
                if extensions:
                    placeholders = ",".join("?" * len(extensions))
                    query += f" AND extension IN ({placeholders})"
                    params.extend(extensions)

                # Add date range filters
                if start_date:
                    start_timestamp = int(start_date.timestamp())
                    query += " AND modified_time >= ?"
                    params.append(start_timestamp)

                if end_date:
                    # Include entire end date
                    end_of_day = end_date.replace(hour=23, minute=59, second=59)
                    end_timestamp = int(end_of_day.timestamp())
                    query += " AND modified_time <= ?"
                    params.append(end_timestamp)

                query += " ORDER BY filename"

                cursor.execute(query, params)
                rows = cursor.fetchall()

                for filename, path, mod_time in rows:
                    # Format modified time
                    try:
                        mod_dt = datetime.fromtimestamp(mod_time)
                        formatted_time = mod_dt.strftime('%Y-%m-%d %H:%M:%S')
                    except (ValueError, OSError):
                        formatted_time = "Unknown"

                    results.append({
                        "filename": filename,
                        "path": path,
                        "modified": formatted_time,
                        "type": Path(path).suffix.lstrip('.').lower() or "unknown"
                    })

            conn.close()
            logger.debug(f"Found {len(results)} files in cache")
            return results

        except Exception as e:
            logger.error(f"Error searching cache: {e}")
            return []

    def update(self, folder_path: str, files: List[Tuple]) -> None:
        """
        Update cache with new files from a folder.

        Args:
            folder_path: Path to the folder being indexed
            files: List of (filename, path, formatted_time) tuples
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Clear old entries for this folder
            cursor.execute("DELETE FROM files WHERE folder = ?", (folder_path,))

            # Insert new files
            current_time = int(datetime.now().timestamp())
            for filename, filepath, formatted_time in files:
                extension = Path(filepath).suffix.lstrip('.').lower() or None

                # Try to get actual modification time from file
                try:
                    mod_timestamp = int(os.path.getmtime(filepath))
                except (OSError, ValueError):
                    mod_timestamp = current_time

                cursor.execute("""
                    INSERT INTO files
                    (folder, filename, path, modified_time, extension, indexed_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (folder_path, filename, filepath, mod_timestamp, extension, current_time))

            conn.commit()
            conn.close()

            logger.info(f"Indexed {len(files)} files from {folder_path}")

        except Exception as e:
            logger.error(f"Error updating cache: {e}")

    def clear_expired(self) -> None:
        """Remove expired cache entries."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            current_time = int(datetime.now().timestamp())
            cutoff_time = current_time - self.cache_ttl

            cursor.execute(
                "DELETE FROM files WHERE indexed_at < ?",
                (cutoff_time,)
            )

            deleted = cursor.rowcount
            conn.commit()
            conn.close()

            if deleted > 0:
                logger.info(f"Cleared {deleted} expired cache entries")

        except Exception as e:
            logger.error(f"Error clearing expired cache: {e}")

    def clear(self, folder_path: Optional[str] = None) -> None:
        """
        Clear cache entries.

        Args:
            folder_path: Specific folder to clear, or None to clear all
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            if folder_path:
                cursor.execute("DELETE FROM files WHERE folder = ?", (folder_path,))
                logger.info(f"Cleared cache for {folder_path}")
            else:
                cursor.execute("DELETE FROM files")
                logger.info("Cleared all cache entries")

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error clearing cache: {e}")

    def get_stats(self) -> Dict:
        """Get cache statistics."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM files")
            total_files = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(DISTINCT folder) FROM files")
            total_folders = cursor.fetchone()[0]

            cursor.execute("SELECT MIN(indexed_at), MAX(indexed_at) FROM files")
            oldest, newest = cursor.fetchone()

            conn.close()

            return {
                "total_files": total_files,
                "total_folders": total_folders,
                "oldest_index": datetime.fromtimestamp(oldest).isoformat() if oldest else None,
                "newest_index": datetime.fromtimestamp(newest).isoformat() if newest else None,
            }

        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}
