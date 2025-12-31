"""CSV file handler for .csv files"""
import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


class CSVHandler:
    """Handle CSV file reading and processing"""

    SUPPORTED_EXTENSIONS = ('.csv',)
    MAX_PREVIEW_ROWS = 10

    @staticmethod
    def read_csv(file_path: str) -> tuple[str, str | None]:
        """
        Read CSV file and format as readable text

        Args:
            file_path: Path to .csv file

        Returns:
            (formatted_text, error_message)
            - formatted_text: CSV content formatted as markdown table
            - error_message: None if successful, error description if failed
        """
        try:
            file_path = Path(file_path)

            # Try to read CSV with pandas - with multiple fallback strategies
            df = None
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']

            # Strategy 1: Standard read
            try:
                df = pd.read_csv(file_path)
            except Exception as e:
                logger.debug(f"Standard CSV read failed: {e}")

                # Strategy 2: Try with different encodings
                for encoding in encodings:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        logger.info(f"Successfully read CSV with {encoding} encoding")
                        break
                    except Exception:
                        continue

                # Strategy 3: If still failing, try with error handling for bad lines
                if df is None:
                    for encoding in encodings:
                        try:
                            # Skip bad lines and handle errors more gracefully
                            df = pd.read_csv(
                                file_path,
                                encoding=encoding,
                                on_bad_lines='skip',  # Skip lines with wrong number of fields
                                engine='python'  # Use python engine for more flexibility
                            )
                            logger.info(f"Successfully read CSV with {encoding} encoding (skipping bad lines)")
                            break
                        except Exception:
                            continue

                # Strategy 4: Last resort - try with maximum error tolerance
                if df is None:
                    try:
                        df = pd.read_csv(
                            file_path,
                            encoding='utf-8',
                            on_bad_lines='skip',
                            sep=',',
                            quotechar='"',
                            engine='python'
                        )
                        logger.info("Successfully read CSV with error tolerance enabled")
                    except Exception as final_error:
                        return "", f"Could not read CSV file (data format error): {str(final_error)}"

            if df is None or df.empty:
                return "", "CSV file is empty or could not be parsed"

            # Format as readable text with table representation
            text_output = CSVHandler._format_dataframe(df)

            logger.info(f"Successfully read CSV: {df.shape[0]} rows, {df.shape[1]} columns")
            return text_output, None

        except FileNotFoundError:
            return "", f"File not found: {file_path}"
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            return "", f"Error reading file: {str(e)}"

    @staticmethod
    def _format_dataframe(df: pd.DataFrame) -> str:
        """
        Format pandas DataFrame as readable text with summary and preview

        Args:
            df: pandas DataFrame

        Returns:
            Formatted text suitable for AI analysis
        """
        lines = []

        # Summary
        lines.append(f"# CSV Summary")
        lines.append(f"- Rows: {df.shape[0]}")
        lines.append(f"- Columns: {df.shape[1]}")
        lines.append(f"- Column Names: {', '.join(df.columns.tolist())}")
        lines.append("")

        # Data types
        lines.append("## Data Types")
        for col, dtype in df.dtypes.items():
            lines.append(f"- {col}: {dtype}")
        lines.append("")

        # Statistics for numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            lines.append("## Numeric Statistics")
            stats = df[numeric_cols].describe().to_string()
            lines.append(stats)
            lines.append("")

        # Preview as table
        lines.append("## Data Preview")
        preview_rows = min(CSVHandler.MAX_PREVIEW_ROWS, len(df))

        # Markdown table format (better for LLM comprehension)
        preview_df = df.head(preview_rows)
        lines.append(preview_df.to_markdown(index=False))

        if len(df) > preview_rows:
            lines.append(f"\n... and {len(df) - preview_rows} more rows")

        return "\n".join(lines)

    @staticmethod
    def get_preview(file_path: str, max_rows: int = 5, max_cols: int = 5) -> dict:
        """
        Get preview of CSV file for UI display

        Returns:
            {
                "rows": int,
                "columns": int,
                "column_names": [str],
                "preview_data": [[str]],  # First max_rows x max_cols
                "error": str | None
            }
        """
        try:
            df = pd.read_csv(file_path, encoding='utf-8', on_bad_lines='skip')

            preview_df = df.iloc[:max_rows, :max_cols]
            preview_data = preview_df.values.tolist()

            return {
                "rows": df.shape[0],
                "columns": df.shape[1],
                "column_names": df.columns.tolist(),
                "preview_data": preview_data,
                "error": None
            }
        except Exception as e:
            logger.error(f"Error getting CSV preview: {e}")
            return {
                "rows": 0,
                "columns": 0,
                "column_names": [],
                "preview_data": [],
                "error": str(e)
            }


if __name__ == "__main__":
    # Test
    test_file = "test.csv"
    content, error = CSVHandler.read_csv(test_file)
    if error:
        print(f"Error: {error}")
    else:
        print(f"Successfully read CSV:\n{content}")
