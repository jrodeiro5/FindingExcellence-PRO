"""Main application window with tabbed interface."""

import logging
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import customtkinter as ctk

# Handle relative imports for both package and direct execution
try:
    from ..api_client import BackendClient
    from ..core.file_search import FileSearch
except ImportError:
    # Fallback: add parent directory to path
    parent_dir = str(Path(__file__).parent.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from api_client import BackendClient
    from core.file_search import FileSearch

from .analysis_panel import AnalysisPanel
from .results_panel import ResultsPanel
from .search_panel import SearchPanel

logger = logging.getLogger(__name__)


class ExcelFinderApp(ctk.CTk):
    """Main application window with File Search and AI Analysis tabs."""

    def __init__(self):
        super().__init__()

        # Window setup
        self.title("FindingExcellence PRO v2.0")
        self.geometry("900x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Backend client (for AI features only)
        self.api_client = BackendClient(host="http://localhost:8000")

        # Direct file search (no API needed)
        self.cancel_event = threading.Event()
        self.file_search = FileSearch(cancel_event=self.cancel_event)
        self.search_thread: Optional[threading.Thread] = None

        # State for AI analysis
        self.analysis_thread: Optional[threading.Thread] = None
        self.analysis_start_time: float = 0

        # Build UI
        self._build_ui()

        # Check backend connection on startup (for AI features)
        self._check_backend_connection()

        # Set close handler
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _build_ui(self):
        """Build main UI layout."""
        # Header
        header = ctk.CTkFrame(self, fg_color="#1a1a1a", height=40)
        header.pack(side="top", fill="x", padx=0, pady=0)
        header.pack_propagate(False)

        title = ctk.CTkLabel(
            header,
            text="FindingExcellence PRO v2.0",
            font=("Arial", 16, "bold"),
            text_color="white"
        )
        title.pack(side="left", padx=20, pady=10)

        self.status_label = ctk.CTkLabel(
            header,
            text="Ready",
            font=("Arial", 11),
            text_color="#52CC52"
        )
        self.status_label.pack(side="right", padx=20, pady=10)

        # Main content area
        content_frame = ctk.CTkFrame(self)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Tabview
        self.tabview = ctk.CTkTabview(content_frame)
        self.tabview.pack(fill="both", expand=True)

        # Tab 1: File Search
        search_tab = self.tabview.add("File Search")
        self.search_panel = SearchPanel(
            search_tab,
            on_search_callback=self._on_search_start,
            on_cancel_callback=self._on_cancel_search,
            on_status_callback=self._update_status
        )
        self.search_panel.pack(fill="both", expand=True)

        # Tab 2: AI Analysis
        analysis_tab = self.tabview.add("AI Analysis")
        self.analysis_panel = AnalysisPanel(
            analysis_tab,
            on_analysis_callback=self._on_analysis_start,
            on_status_callback=self._update_status
        )
        self.analysis_panel.pack(fill="both", expand=True)

        # Results panel (shared between tabs)
        self.results_panel = ResultsPanel(content_frame)
        self.results_panel.pack(fill="both", expand=True, pady=(10, 0))

        # Progress bar (hidden initially)
        self.progress_bar = ctk.CTkProgressBar(content_frame, height=8)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", pady=(10, 0))
        self.progress_bar.pack_forget()  # Hide initially

    def _check_backend_connection(self):
        """Check if backend is running (for AI features)."""
        def check():
            is_connected = self.api_client.health_check()
            if is_connected:
                self.after(0, lambda: self._update_status("Ready (AI available)", color="#52CC52"))
            else:
                self.after(0, lambda: self._update_status("Ready (AI offline)", color="#FFB347"))

        thread = threading.Thread(target=check, daemon=True)
        thread.start()

    def _update_status(self, message: str, color: str = "#FFB347"):
        """Update status label (thread-safe)."""
        self.status_label.configure(text=message, text_color=color)

    # ==================== FILE SEARCH (Direct Python - No API) ====================

    def _on_search_start(self, keyword: str, folders: list, case_sensitive: bool = False,
                         start_date: str = None, end_date: str = None):
        """Start file search directly (no API needed)."""
        if not keyword.strip():
            self._update_status("Please enter search keywords", color="#FF6B6B")
            return

        if not folders:
            self._update_status("Please select at least one folder", color="#FF6B6B")
            return

        # Reset cancel event and clear previous results
        self.cancel_event.clear()
        self.results_panel.clear_results()

        # Update UI state
        self.search_panel.set_searching_state(True)
        self._update_status("Starting search...", color="#FFB347")
        self.progress_bar.pack(fill="x", pady=(10, 0))
        self.progress_bar.set(0)
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()

        # Run search in background thread
        self.search_thread = threading.Thread(
            target=self._run_search,
            args=(keyword, folders, case_sensitive, start_date, end_date),
            daemon=True
        )
        self.search_thread.start()

    def _run_search(self, keyword: str, folders: list, case_sensitive: bool,
                    start_date: str = None, end_date: str = None):
        """Background search worker with status callbacks."""
        try:
            # Split keywords by space or comma
            keywords = [k.strip() for k in keyword.replace(',', ' ').split() if k.strip()]

            # Convert date strings to date objects if provided
            parsed_start = None
            parsed_end = None

            if start_date:
                parsed_start = datetime.strptime(start_date, '%Y-%m-%d').date()
            if end_date:
                parsed_end = datetime.strptime(end_date, '%Y-%m-%d').date()

            results = self.file_search.search_by_filename(
                folder_paths=folders,
                filename_keywords=keywords,
                case_sensitive=case_sensitive,
                start_date=parsed_start,
                end_date=parsed_end,
                supported_extensions=None,
                status_callback=self._on_search_status
            )

            # Update UI on main thread
            self.after(0, lambda: self._on_search_complete(results))

        except Exception as e:
            logger.error(f"Search error: {e}")
            self.after(0, lambda: self._on_search_error(str(e)))

    def _on_search_status(self, message: str):
        """Called by FileSearch with progress updates."""
        # Schedule UI update on main thread
        self.after(0, lambda: self._update_status(message, color="#FFB347"))

    def _on_cancel_search(self):
        """Cancel ongoing search."""
        self.cancel_event.set()
        self._update_status("Cancelling search...", color="#FF6B6B")

    def _on_search_complete(self, results: list):
        """Called when search finishes."""
        # Stop progress bar
        self.progress_bar.stop()
        self.progress_bar.pack_forget()

        # Reset UI state
        self.search_panel.set_searching_state(False)

        # Update status based on whether cancelled or completed
        if self.cancel_event.is_set():
            self._update_status(f"Search cancelled. Found {len(results)} files.", color="#FFB347")
        else:
            self._update_status(f"Found {len(results)} files", color="#52CC52")

        # Display results
        self.results_panel.display_results(results)

    def _on_search_error(self, error: str):
        """Called when search encounters an error."""
        # Stop progress bar
        self.progress_bar.stop()
        self.progress_bar.pack_forget()

        # Reset UI state
        self.search_panel.set_searching_state(False)
        self._update_status(f"Error: {error}", color="#FF6B6B")

    # ==================== AI ANALYSIS (Uses Backend API - Synchronous) ====================

    def _on_analysis_start(self, file_path: str):
        """Called when user clicks Analyze button."""
        if not file_path:
            self._update_status("No file selected", color="#FF6B6B")
            return

        # Check backend connection first
        if not self.api_client.health_check():
            self._update_status("Backend offline. Start backend first.", color="#FF6B6B")
            return

        # Disable UI and show progress
        self.analysis_panel.disable_upload_button()
        self.results_panel.clear_results()
        self._update_status("Analyzing file...", color="#FFB347")

        # Show enhanced progress indicator with elapsed time
        self.analysis_panel.show_progress("Analyzing")

        # Show indeterminate progress bar
        self.progress_bar.pack(fill="x", pady=(10, 0))
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()

        # Track start time for elapsed display
        self.analysis_start_time = time.time()

        # Start analysis in background thread
        self.analysis_thread = threading.Thread(
            target=self._run_analysis,
            args=(file_path,),
            daemon=True
        )
        self.analysis_thread.start()

    def _run_analysis(self, file_path: str):
        """Background worker for file analysis. Only calls self.after() once at the end."""
        try:
            # Call the synchronous API - this blocks until complete
            result = self.api_client.analyze_file(file_path)

            if result.get("success"):
                # Extract analysis result - may be nested dict from ai_services
                analysis_data = result.get("analysis", {})
                if isinstance(analysis_data, dict):
                    # Backend returns nested structure: {"analysis": {"analysis": "text", "model": ...}}
                    analysis_text = analysis_data.get("analysis", "No analysis returned")
                    model = analysis_data.get("model", "unknown")
                    latency_ms = analysis_data.get("latency_ms", 0)
                else:
                    # Direct string response
                    analysis_text = str(analysis_data)
                    model = result.get("model", "unknown")
                    latency_ms = 0

                file_info = result.get("file_info", {})
                timing = result.get("timing", {"total_ms": latency_ms})

                # Format result with metadata
                formatted_result = self._format_analysis_result(
                    analysis_text,
                    file_info,
                    timing,
                    model
                )

                # Schedule UI update on main thread - ONLY self.after() call
                self.after(0, lambda r=formatted_result: self._on_analysis_complete(r))
            else:
                error = result.get("error", "Unknown error")
                # Schedule UI update on main thread - ONLY self.after() call
                self.after(0, lambda e=error: self._on_analysis_error(e))

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Analysis error: {error_msg}")
            # Schedule UI update on main thread - ONLY self.after() call
            self.after(0, lambda msg=error_msg: self._on_analysis_error(msg))

    def _format_analysis_result(self, analysis: str, file_info: dict, timing: dict, model: str) -> str:
        """Format analysis result with metadata header."""
        header_lines = [
            "=" * 60,
            "AI DOCUMENT ANALYSIS",
            "=" * 60,
            f"File: {file_info.get('name', 'Unknown')}",
            f"Type: {file_info.get('type', 'Unknown')}",
            f"Size: {file_info.get('size', 0) / 1024:.1f} KB",
        ]

        if file_info.get('pages', 0) > 1:
            header_lines.append(f"Pages: {file_info.get('pages')}")

        if timing:
            total_ms = timing.get('total_ms', 0)
            header_lines.append(f"Processing time: {total_ms / 1000:.1f}s")

        header_lines.extend([
            f"Model: {model}",
            "=" * 60,
            "",
            analysis
        ])

        return "\n".join(header_lines)

    def _on_analysis_complete(self, result: str):
        """Called when analysis finishes successfully."""
        # Stop progress bar
        self.progress_bar.stop()
        self.progress_bar.pack_forget()

        # Calculate total elapsed time
        elapsed = time.time() - self.analysis_start_time

        # Stop progress indicator and show completion message
        self.analysis_panel.hide_progress(f"Complete ({elapsed:.1f}s)")

        # Re-enable UI
        self.analysis_panel.enable_upload_button()

        self._update_status(f"Analysis complete ({elapsed:.1f}s)", color="#52CC52")

        # Display results in the analysis panel's own results area
        self.analysis_panel.display_results(result)

        # Also update the shared results panel
        self.results_panel.display_analysis_result(result)

    def _on_analysis_error(self, error: str):
        """Called when analysis encounters an error."""
        # Stop progress bar
        self.progress_bar.stop()
        self.progress_bar.pack_forget()

        # Stop progress indicator
        self.analysis_panel.hide_progress("Error")

        # Re-enable UI
        self.analysis_panel.enable_upload_button()
        self._update_status(f"Error: {error}", color="#FF6B6B")

    def _on_closing(self):
        """Handle window close."""
        try:
            # Cancel any ongoing search
            self.cancel_event.set()
            self.api_client.close()
            self.destroy()
        except Exception as e:
            logger.error(f"Close error: {e}")
            self.destroy()


def main():
    """Main entry point."""
    app = ExcelFinderApp()
    app.mainloop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
