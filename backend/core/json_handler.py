"""Handler for JSON files."""

import json
import logging
from pathlib import Path
from typing import Tuple

logger = logging.getLogger(__name__)


class JSONHandler:
    """Extract text from JSON files."""

    SUPPORTED_EXTENSIONS = ('.json',)

    @staticmethod
    def read_json(file_path: str) -> Tuple[str, str | None]:
        """
        Extract text from a JSON file.

        Args:
            file_path: Path to the JSON file

        Returns:
            (content, error) - content is str, error is None on success
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError as e:
                    error_msg = f"Invalid JSON format: {str(e)}"
                    logger.error(error_msg)
                    return "", error_msg

            # Pretty print JSON for readability
            content = json.dumps(data, indent=2, ensure_ascii=False)
            logger.info(f"Extracted {len(content)} characters from JSON file: {Path(file_path).name}")
            return content, None

        except FileNotFoundError:
            error_msg = f"File not found: {file_path}"
            logger.error(error_msg)
            return "", error_msg
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    data = json.load(f)
                content = json.dumps(data, indent=2, ensure_ascii=False)
                logger.info(f"Extracted {len(content)} characters from JSON file (latin-1): {Path(file_path).name}")
                return content, None
            except Exception as e:
                error_msg = f"Error reading JSON file: {str(e)}"
                logger.error(error_msg)
                return "", error_msg
        except Exception as e:
            error_msg = f"Error reading JSON file: {str(e)}"
            logger.error(error_msg)
            return "", error_msg
