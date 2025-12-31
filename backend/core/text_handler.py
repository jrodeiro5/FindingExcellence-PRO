"""Text file handler for .txt files"""
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class TextHandler:
    """Handle plain text file reading and processing"""

    SUPPORTED_EXTENSIONS = ('.txt',)

    @staticmethod
    def read_text(file_path: str) -> tuple[str, str | None]:
        """
        Read plain text file

        Args:
            file_path: Path to .txt file

        Returns:
            (text_content, error_message)
            - text_content: Full file content as string
            - error_message: None if successful, error description if failed
        """
        try:
            file_path = Path(file_path)

            # Read file with automatic encoding detection
            encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
            content = None

            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    logger.info(f"Successfully read text file with {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue

            if content is None:
                return "", f"Could not decode file with any encoding"

            # Basic validation
            if not content.strip():
                return "", "File is empty"

            return content, None

        except FileNotFoundError:
            return "", f"File not found: {file_path}"
        except Exception as e:
            logger.error(f"Error reading text file: {e}")
            return "", f"Error reading file: {str(e)}"

    @staticmethod
    def get_line_count(file_path: str) -> int:
        """Get number of lines in text file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except Exception:
            return 0


if __name__ == "__main__":
    # Test
    test_file = "test.txt"
    content, error = TextHandler.read_text(test_file)
    if error:
        print(f"Error: {error}")
    else:
        print(f"Successfully read {len(content)} characters")
