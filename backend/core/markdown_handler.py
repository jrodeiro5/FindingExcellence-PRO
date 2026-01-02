"""Handler for Markdown files."""

import logging
from pathlib import Path
from typing import Tuple

logger = logging.getLogger(__name__)


class MarkdownHandler:
    """Extract text from Markdown files."""

    SUPPORTED_EXTENSIONS = ('.md', '.markdown', '.mdown', '.mkd', '.mkdn')

    @staticmethod
    def read_markdown(file_path: str) -> Tuple[str, str | None]:
        """
        Extract text from a Markdown file.

        Args:
            file_path: Path to the Markdown file

        Returns:
            (content, error) - content is str, error is None on success
        """
        try:
            # Try UTF-8 first
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            logger.info(f"Extracted {len(content)} characters from Markdown file: {Path(file_path).name}")
            return content, None

        except FileNotFoundError:
            error_msg = f"File not found: {file_path}"
            logger.error(error_msg)
            return "", error_msg
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                logger.info(f"Extracted {len(content)} characters from Markdown file (latin-1): {Path(file_path).name}")
                return content, None
            except Exception as e:
                error_msg = f"Error reading Markdown file: {str(e)}"
                logger.error(error_msg)
                return "", error_msg
        except Exception as e:
            error_msg = f"Error reading Markdown file: {str(e)}"
            logger.error(error_msg)
            return "", error_msg
