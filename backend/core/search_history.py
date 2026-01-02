"""SQLite-based search history tracking for quick search re-runs."""

import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class SearchHistory:
    """Manages search history with persistent SQLite storage."""

    def __init__(self, db_path: str = ".cache/search_history.db", max_history: int = 20):
        """
        Initialize search history tracker.

        Args:
            db_path: Path to SQLite database file
            max_history: Maximum number of searches to keep (default: 20)
        """
        self.db_path = db_path
        self.max_history = max_history
        self._init_db()

    def _init_db(self) -> None:
        """Create database schema if not exists."""
        # Create directory if needed
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create search history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keywords TEXT NOT NULL,
                exclude_keywords TEXT,
                folders TEXT NOT NULL,
                start_date TEXT,
                end_date TEXT,
                case_sensitive INTEGER DEFAULT 0,
                extensions TEXT,
                search_count INTEGER DEFAULT 0,
                created_at INTEGER NOT NULL,
                last_used_at INTEGER NOT NULL
            )
        """)

        # Create index for quick retrieval
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_last_used
            ON searches(last_used_at DESC)
        """)

        conn.commit()
        conn.close()

        logger.info(f"Search history initialized at {self.db_path}")

    def add_search(
        self,
        keywords: List[str],
        folders: List[str],
        exclude_keywords: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        case_sensitive: bool = False,
        extensions: Optional[List[str]] = None
    ) -> None:
        """
        Add or update a search in history.

        Args:
            keywords: List of search keywords
            folders: List of folders searched
            exclude_keywords: Keywords to exclude
            start_date: Start date filter
            end_date: End date filter
            case_sensitive: Whether search was case-sensitive
            extensions: File extensions filter
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Convert lists to comma-separated strings
            keywords_str = ",".join(keywords)
            folders_str = ",".join(folders)
            exclude_str = ",".join(exclude_keywords) if exclude_keywords else ""
            ext_str = ",".join(extensions) if extensions else ""

            current_time = int(datetime.now().timestamp())

            # Check if similar search exists
            cursor.execute("""
                SELECT id, search_count FROM searches
                WHERE keywords = ? AND folders = ?
            """, (keywords_str, folders_str))

            existing = cursor.fetchone()

            if existing:
                # Update existing search
                search_id, count = existing
                cursor.execute("""
                    UPDATE searches
                    SET search_count = ?, last_used_at = ?
                    WHERE id = ?
                """, (count + 1, current_time, search_id))

                logger.debug(f"Updated search history entry: {keywords_str}")
            else:
                # Insert new search
                cursor.execute("""
                    INSERT INTO searches
                    (keywords, exclude_keywords, folders, start_date, end_date,
                     case_sensitive, extensions, search_count, created_at, last_used_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    keywords_str,
                    exclude_str,
                    folders_str,
                    start_date,
                    end_date,
                    1 if case_sensitive else 0,
                    ext_str,
                    1,
                    current_time,
                    current_time
                ))

                logger.debug(f"Added new search history entry: {keywords_str}")

            # Remove oldest entries if exceeding max
            cursor.execute("""
                SELECT COUNT(*) FROM searches
            """)
            count = cursor.fetchone()[0]

            if count > self.max_history:
                cursor.execute("""
                    DELETE FROM searches WHERE id IN (
                        SELECT id FROM searches
                        ORDER BY last_used_at ASC
                        LIMIT ?
                    )
                """, (count - self.max_history,))

                logger.debug(f"Trimmed search history to {self.max_history} entries")

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error adding to search history: {e}")

    def get_history(self, limit: int = 20) -> List[Dict]:
        """
        Get recent search history.

        Args:
            limit: Maximum number of searches to return

        Returns:
            List of search history dictionaries sorted by most recent first
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, keywords, folders, start_date, end_date, case_sensitive,
                       extensions, search_count, created_at, last_used_at
                FROM searches
                ORDER BY last_used_at DESC
                LIMIT ?
            """, (limit,))

            results = []
            for row in cursor.fetchall():
                (search_id, keywords, folders, start_date, end_date, case_sensitive,
                 extensions, search_count, created_at, last_used_at) = row

                # Format created time
                try:
                    created_dt = datetime.fromtimestamp(created_at)
                    created_str = created_dt.strftime('%m/%d %H:%M')
                except (ValueError, OSError):
                    created_str = "Unknown"

                results.append({
                    "id": search_id,
                    "keywords": keywords.split(","),
                    "folders": folders.split(","),
                    "start_date": start_date,
                    "end_date": end_date,
                    "case_sensitive": bool(case_sensitive),
                    "extensions": extensions.split(",") if extensions else [],
                    "search_count": search_count,
                    "created_at": created_str,
                    "last_used": created_str
                })

            conn.close()
            return results

        except Exception as e:
            logger.error(f"Error retrieving search history: {e}")
            return []

    def get_search_by_id(self, search_id: int) -> Optional[Dict]:
        """Get a specific search from history."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, keywords, folders, start_date, end_date, case_sensitive, extensions
                FROM searches
                WHERE id = ?
            """, (search_id,))

            row = cursor.fetchone()
            conn.close()

            if row:
                (search_id, keywords, folders, start_date, end_date, case_sensitive, extensions) = row

                return {
                    "id": search_id,
                    "keywords": keywords.split(","),
                    "folders": folders.split(","),
                    "start_date": start_date,
                    "end_date": end_date,
                    "case_sensitive": bool(case_sensitive),
                    "extensions": extensions.split(",") if extensions else []
                }

            return None

        except Exception as e:
            logger.error(f"Error retrieving search by ID: {e}")
            return None

    def delete_search(self, search_id: int) -> bool:
        """Delete a search from history."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM searches WHERE id = ?", (search_id,))

            conn.commit()
            conn.close()

            logger.debug(f"Deleted search history entry: {search_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting search history: {e}")
            return False

    def clear_history(self) -> bool:
        """Clear all search history."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM searches")

            conn.commit()
            conn.close()

            logger.info("Cleared all search history")
            return True

        except Exception as e:
            logger.error(f"Error clearing search history: {e}")
            return False
