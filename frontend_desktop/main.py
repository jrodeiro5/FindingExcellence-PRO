#!/usr/bin/env python3
"""
FindingExcellence PRO v2.0 - Desktop Frontend
Modern CustomTkinter-based desktop application with file search and AI analysis.
"""

import logging
import os
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(project_root / "finding_excellence_desktop.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Load environment variables
try:
    from dotenv import load_dotenv
    env_file = project_root / ".env"
    if env_file.exists():
        load_dotenv(env_file)
    logger.info(f"Loaded .env from {env_file}")
except ImportError:
    logger.warning("python-dotenv not found, environment variables may not load")


def main():
    """Main entry point for desktop application."""
    try:
        logger.info("Starting FindingExcellence PRO v2.0 Desktop")

        # Import from ui package (relative to frontend_desktop directory)
        import sys
        frontend_dir = Path(__file__).parent
        if str(frontend_dir) not in sys.path:
            sys.path.insert(0, str(frontend_dir))

        from ui.main_window import ExcelFinderApp

        app = ExcelFinderApp()
        logger.info("Application initialized")

        app.mainloop()
        logger.info("Application closed")

    except ImportError as e:
        logger.error(f"Import error: {e}")
        print(f"\n❌ Error: Missing dependencies")
        print(f"Please run: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n❌ Fatal error: {e}")
        print(f"Check log file for details")
        sys.exit(1)


if __name__ == "__main__":
    main()
