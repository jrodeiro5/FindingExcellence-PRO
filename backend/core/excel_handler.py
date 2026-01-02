"""Excel file handler for .xlsx and .xls files"""
import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


class ExcelHandler:
    """Handle Excel file reading and processing"""

    SUPPORTED_EXTENSIONS = ('.xlsx', '.xls', '.xlsm')
    MAX_PREVIEW_ROWS = 10

    @staticmethod
    def read_excel(file_path: str) -> tuple[str, str | None]:
        """
        Read Excel file and format as readable text

        Args:
            file_path: Path to .xlsx or .xls file

        Returns:
            (formatted_text, error_message)
            - formatted_text: Excel content formatted from all sheets
            - error_message: None if successful, error description if failed
        """
        try:
            file_path = Path(file_path)

            # Read all sheets
            xls = pd.ExcelFile(file_path)
            try:
                sheet_names = xls.sheet_names

                if not sheet_names:
                    return "", "Excel file has no sheets"

                lines = []
                lines.append(f"# Excel File Summary")
                lines.append(f"- Number of sheets: {len(sheet_names)}")
                lines.append(f"- Sheet names: {', '.join(sheet_names)}")
                lines.append("")

                # Process each sheet
                for sheet_name in sheet_names:
                    try:
                        df = pd.read_excel(file_path, sheet_name=sheet_name)

                        if df.empty:
                            lines.append(f"## Sheet: {sheet_name}")
                            lines.append("(Empty sheet)")
                            lines.append("")
                            continue

                        # Sheet header
                        lines.append(f"## Sheet: {sheet_name}")
                        lines.append(f"- Rows: {df.shape[0]}")
                        lines.append(f"- Columns: {df.shape[1]}")
                        lines.append(f"- Columns: {', '.join(df.columns.tolist())}")
                        lines.append("")

                        # Preview as table
                        lines.append("### Data Preview")
                        preview_rows = min(ExcelHandler.MAX_PREVIEW_ROWS, len(df))
                        preview_df = df.head(preview_rows)
                        lines.append(preview_df.to_markdown(index=False))

                        if len(df) > preview_rows:
                            lines.append(f"\n... and {len(df) - preview_rows} more rows")

                        lines.append("")

                    except Exception as e:
                        logger.warning(f"Error reading sheet '{sheet_name}': {e}")
                        lines.append(f"## Sheet: {sheet_name}")
                        lines.append(f"(Error reading sheet: {str(e)})")
                        lines.append("")

                text_output = "\n".join(lines)
                logger.info(f"Successfully read Excel file with {len(sheet_names)} sheets")
                return text_output, None
            finally:
                xls.close()  # Explicitly close the ExcelFile handle

        except FileNotFoundError:
            return "", f"File not found: {file_path}"
        except Exception as e:
            logger.error(f"Error reading Excel file: {e}")
            return "", f"Error reading file: {str(e)}"

    @staticmethod
    def get_preview(file_path: str, max_rows: int = 5, max_cols: int = 5) -> dict:
        """
        Get preview of first sheet in Excel file for UI display

        Returns:
            {
                "sheet_names": [str],
                "active_sheet": str,
                "rows": int,
                "columns": int,
                "column_names": [str],
                "preview_data": [[str]],  # First max_rows x max_cols
                "error": str | None
            }
        """
        try:
            xls = pd.ExcelFile(file_path)
            try:
                sheet_names = xls.sheet_names

                if not sheet_names:
                    return {
                        "sheet_names": [],
                        "active_sheet": None,
                        "rows": 0,
                        "columns": 0,
                        "column_names": [],
                        "preview_data": [],
                        "error": "No sheets in Excel file"
                    }

                # Read first sheet
                active_sheet = sheet_names[0]
                df = pd.read_excel(file_path, sheet_name=active_sheet)

                preview_df = df.iloc[:max_rows, :max_cols]
                preview_data = preview_df.values.tolist()

                return {
                    "sheet_names": sheet_names,
                    "active_sheet": active_sheet,
                    "rows": df.shape[0],
                    "columns": df.shape[1],
                    "column_names": df.columns.tolist(),
                    "preview_data": preview_data,
                    "error": None
                }
            finally:
                xls.close()  # Explicitly close the ExcelFile handle
        except Exception as e:
            logger.error(f"Error getting Excel preview: {e}")
            return {
                "sheet_names": [],
                "active_sheet": None,
                "rows": 0,
                "columns": 0,
                "column_names": [],
                "preview_data": [],
                "error": str(e)
            }


if __name__ == "__main__":
    # Test
    test_file = "test.xlsx"
    content, error = ExcelHandler.read_excel(test_file)
    if error:
        print(f"Error: {error}")
    else:
        print(f"Successfully read Excel:\n{content}")
