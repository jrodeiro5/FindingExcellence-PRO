"""
Data Analyzer - Extract statistics from tabular data before LLM processing.

Strategy: Extract key statistics with polars/pandas, then send condensed
summary to LLM for interpretation. This is much faster and more accurate
than sending raw CSV data to an LLM.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# Try polars first (faster), fall back to pandas
try:
    import polars as pl
    HAS_POLARS = True
    logger.info("Using Polars for data analysis (fast mode)")
except ImportError:
    HAS_POLARS = False
    logger.info("Polars not available, using Pandas")

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    logger.warning("Pandas not available")


class DataAnalyzer:
    """Extract statistics from CSV/Excel files for LLM summarization."""

    @staticmethod
    def analyze_csv(file_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Analyze CSV file and return structured summary for LLM.

        Args:
            file_path: Path to CSV file

        Returns:
            Tuple of (summary_text, metadata_dict)
        """
        if HAS_POLARS:
            return DataAnalyzer._analyze_with_polars(file_path)
        elif HAS_PANDAS:
            return DataAnalyzer._analyze_with_pandas(file_path)
        else:
            return "No data analysis library available (install polars or pandas)", {}

    @staticmethod
    def analyze_excel(file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Analyze Excel file and return structured summary for LLM."""
        if HAS_PANDAS:
            return DataAnalyzer._analyze_excel_with_pandas(file_path)
        else:
            return "Pandas required for Excel analysis", {}

    @staticmethod
    def _analyze_with_polars(file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Fast analysis using Polars."""
        try:
            df = pl.read_csv(file_path, infer_schema_length=1000, ignore_errors=True)

            metadata = {
                "rows": df.height,
                "columns": df.width,
                "column_names": df.columns,
            }

            lines = [
                f"## Dataset Overview",
                f"- Rows: {df.height:,}",
                f"- Columns: {df.width}",
                f"- Columns: {', '.join(df.columns)}",
                "",
                "## Column Types",
            ]

            # Column types
            for col in df.columns:
                dtype = str(df[col].dtype)
                null_count = df[col].null_count()
                null_pct = (null_count / df.height * 100) if df.height > 0 else 0
                lines.append(f"- {col}: {dtype} ({null_pct:.1f}% null)")

            lines.append("")
            lines.append("## Numeric Column Statistics")

            # Numeric statistics
            numeric_cols = [col for col in df.columns if df[col].dtype in [pl.Int64, pl.Int32, pl.Float64, pl.Float32]]

            for col in numeric_cols[:10]:  # Limit to first 10 numeric columns
                try:
                    stats = df[col].describe()
                    min_val = df[col].min()
                    max_val = df[col].max()
                    mean_val = df[col].mean()
                    lines.append(f"- {col}: min={min_val}, max={max_val}, mean={mean_val:.2f}" if mean_val else f"- {col}: min={min_val}, max={max_val}")
                except Exception:
                    pass

            # Categorical/string column value counts
            string_cols = [col for col in df.columns if df[col].dtype == pl.Utf8]

            if string_cols:
                lines.append("")
                lines.append("## Categorical Column Top Values")

                for col in string_cols[:5]:  # Limit to first 5 string columns
                    try:
                        unique_count = df[col].n_unique()
                        if unique_count <= 20:
                            top_values = df.group_by(col).count().sort("count", descending=True).head(5)
                            top_str = ", ".join([f"{row[col]}({row['count']})" for row in top_values.iter_rows(named=True)])
                            lines.append(f"- {col} ({unique_count} unique): {top_str}")
                        else:
                            lines.append(f"- {col}: {unique_count} unique values")
                    except Exception:
                        pass

            # Sample data (first 3 rows)
            lines.append("")
            lines.append("## Sample Data (first 3 rows)")
            try:
                sample = df.head(3)
                for i, row in enumerate(sample.iter_rows(named=True)):
                    row_str = ", ".join([f"{k}={v}" for k, v in list(row.items())[:6]])
                    lines.append(f"Row {i+1}: {row_str}")
            except Exception:
                lines.append("(Unable to display sample)")

            summary = "\n".join(lines)
            return summary, metadata

        except Exception as e:
            logger.error(f"Polars analysis failed: {e}")
            return f"Error analyzing CSV: {str(e)}", {}

    @staticmethod
    def _analyze_with_pandas(file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Analysis using Pandas (fallback)."""
        try:
            df = pd.read_csv(file_path, nrows=10000)  # Limit for speed

            metadata = {
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": list(df.columns),
            }

            lines = [
                f"## Dataset Overview",
                f"- Rows: {len(df):,}",
                f"- Columns: {len(df.columns)}",
                f"- Columns: {', '.join(df.columns)}",
                "",
                "## Column Types",
            ]

            # Column types and null counts
            for col in df.columns:
                dtype = str(df[col].dtype)
                null_pct = df[col].isnull().sum() / len(df) * 100
                lines.append(f"- {col}: {dtype} ({null_pct:.1f}% null)")

            lines.append("")
            lines.append("## Numeric Column Statistics")

            # Numeric statistics
            numeric_df = df.select_dtypes(include=['int64', 'float64', 'int32', 'float32'])

            for col in list(numeric_df.columns)[:10]:
                try:
                    min_val = df[col].min()
                    max_val = df[col].max()
                    mean_val = df[col].mean()
                    lines.append(f"- {col}: min={min_val}, max={max_val}, mean={mean_val:.2f}")
                except Exception:
                    pass

            # Categorical columns
            object_cols = df.select_dtypes(include=['object']).columns

            if len(object_cols) > 0:
                lines.append("")
                lines.append("## Categorical Column Top Values")

                for col in list(object_cols)[:5]:
                    try:
                        unique_count = df[col].nunique()
                        if unique_count <= 20:
                            top_values = df[col].value_counts().head(5)
                            top_str = ", ".join([f"{idx}({val})" for idx, val in top_values.items()])
                            lines.append(f"- {col} ({unique_count} unique): {top_str}")
                        else:
                            lines.append(f"- {col}: {unique_count} unique values")
                    except Exception:
                        pass

            # Sample data
            lines.append("")
            lines.append("## Sample Data (first 3 rows)")
            try:
                for i, row in df.head(3).iterrows():
                    row_dict = row.to_dict()
                    row_str = ", ".join([f"{k}={v}" for k, v in list(row_dict.items())[:6]])
                    lines.append(f"Row {i+1}: {row_str}")
            except Exception:
                lines.append("(Unable to display sample)")

            summary = "\n".join(lines)
            return summary, metadata

        except Exception as e:
            logger.error(f"Pandas analysis failed: {e}")
            return f"Error analyzing CSV: {str(e)}", {}

    @staticmethod
    def _analyze_excel_with_pandas(file_path: str) -> Tuple[str, Dict[str, Any]]:
        """Analyze Excel file using Pandas."""
        try:
            # Read all sheets
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names

            all_lines = [
                f"## Excel Workbook Overview",
                f"- Sheets: {len(sheet_names)}",
                f"- Sheet names: {', '.join(sheet_names)}",
                "",
            ]

            metadata = {
                "sheets": len(sheet_names),
                "sheet_names": sheet_names,
            }

            # Analyze first sheet (or all if few sheets)
            sheets_to_analyze = sheet_names[:3]  # Max 3 sheets

            for sheet in sheets_to_analyze:
                df = pd.read_excel(file_path, sheet_name=sheet, nrows=5000)

                all_lines.append(f"### Sheet: {sheet}")
                all_lines.append(f"- Rows: {len(df):,}, Columns: {len(df.columns)}")
                all_lines.append(f"- Columns: {', '.join(df.columns[:10])}")

                # Quick stats for numeric columns
                numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns[:5]
                if len(numeric_cols) > 0:
                    all_lines.append("- Key metrics:")
                    for col in numeric_cols:
                        try:
                            all_lines.append(f"  - {col}: sum={df[col].sum():.0f}, mean={df[col].mean():.2f}")
                        except:
                            pass

                all_lines.append("")

            summary = "\n".join(all_lines)
            return summary, metadata

        except Exception as e:
            logger.error(f"Excel analysis failed: {e}")
            return f"Error analyzing Excel: {str(e)}", {}


def get_data_summary(file_path: str, file_type: str) -> Tuple[str, Dict[str, Any]]:
    """
    Get structured data summary for LLM processing.

    Args:
        file_path: Path to data file
        file_type: File extension (.csv, .xlsx, etc.)

    Returns:
        Tuple of (summary_text, metadata)
    """
    if file_type in ['.csv']:
        return DataAnalyzer.analyze_csv(file_path)
    elif file_type in ['.xlsx', '.xls', '.xlsm']:
        return DataAnalyzer.analyze_excel(file_path)
    else:
        return f"Unsupported file type for data analysis: {file_type}", {}
