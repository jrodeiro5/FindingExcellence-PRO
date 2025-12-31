"""Polars handler for heavy data processing - faster than pandas for large datasets"""
import logging
from pathlib import Path
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)


class PolarsHandler:
    """Handle large CSV/Excel files with Polars (faster than pandas)"""

    SUPPORTED_EXTENSIONS = ('.csv', '.xlsx', '.xls', '.parquet')
    HEAVY_FILE_THRESHOLD = 50 * 1024 * 1024  # 50MB - switch to Polars

    @staticmethod
    def is_available() -> bool:
        """Check if Polars is installed"""
        try:
            import polars as pl
            return True
        except ImportError:
            return False

    @staticmethod
    def should_use_polars(file_path: str) -> bool:
        """Determine if Polars should be used based on file size"""
        if not PolarsHandler.is_available():
            return False

        try:
            file_size = Path(file_path).stat().st_size
            return file_size > PolarsHandler.HEAVY_FILE_THRESHOLD
        except Exception:
            return False

    @staticmethod
    def read_csv(file_path: str) -> Tuple[str, Optional[str]]:
        """
        Read large CSV with Polars (faster than pandas)

        Args:
            file_path: Path to CSV file

        Returns:
            (formatted_text, error_message)
        """
        try:
            import polars as pl

            file_path = Path(file_path)

            # Read with Polars
            df = pl.read_csv(file_path)

            # Format output
            lines = []
            lines.append(f"# CSV Summary (Polars - Fast Processing)")
            lines.append(f"- Rows: {df.height:,}")
            lines.append(f"- Columns: {df.width}")
            lines.append(f"- Column Names: {', '.join(df.columns)}")
            lines.append("")

            # Data types
            lines.append("## Schema")
            for col, dtype in zip(df.columns, df.dtypes):
                lines.append(f"- {col}: {dtype}")
            lines.append("")

            # Statistics
            lines.append("## Statistics")
            try:
                stats = df.describe()
                lines.append(stats.to_pandas().to_markdown())
            except Exception as e:
                lines.append(f"(Could not generate statistics: {e})")
            lines.append("")

            # Preview
            lines.append("## Data Preview")
            preview = df.head(10)
            lines.append(preview.to_pandas().to_markdown(index=False))

            if df.height > 10:
                lines.append(f"\n... and {df.height - 10:,} more rows")

            text_output = "\n".join(lines)
            logger.info(f"Polars read CSV: {df.height:,} rows, {df.width} cols from {file_path.name}")

            return text_output, None

        except ImportError:
            return "", "Polars not installed. Install with: pip install polars"
        except Exception as e:
            logger.error(f"Polars CSV read failed: {e}")
            return "", f"Error reading CSV with Polars: {str(e)}"

    @staticmethod
    def search_content(
        file_path: str,
        keywords: List[str],
        case_sensitive: bool = False
    ) -> List[dict]:
        """
        Fast content search in large CSV using Polars

        Args:
            file_path: Path to CSV
            keywords: Keywords to search
            case_sensitive: Case-sensitive search

        Returns:
            List of matches
        """
        try:
            import polars as pl

            df = pl.read_csv(file_path)
            results = []

            for keyword in keywords:
                # Search across all string columns
                for col in df.columns:
                    if df[col].dtype == pl.Utf8:
                        # Use Polars string methods (much faster than pandas)
                        if case_sensitive:
                            mask = df[col].str.contains(keyword)
                        else:
                            mask = df[col].str.to_lowercase().str.contains(keyword.lower())

                        # Get matching rows
                        matches = df.filter(mask)

                        for idx, row in enumerate(matches.iter_rows(named=True)):
                            results.append({
                                "keyword": keyword,
                                "column": col,
                                "row": idx,
                                "value": str(row[col]),
                                "file": Path(file_path).name
                            })

            logger.info(f"Polars search found {len(results)} matches in {Path(file_path).name}")
            return results

        except ImportError:
            return [{"error": "Polars not installed", "file_path": file_path}]
        except Exception as e:
            logger.error(f"Polars search failed: {e}")
            return [{"error": str(e), "file_path": file_path}]
