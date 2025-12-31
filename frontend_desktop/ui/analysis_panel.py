"""File analysis panel component for AI document analysis."""

import time
import tkinter.filedialog as filedialog
from typing import Callable, Optional

import customtkinter as ctk


class EnhancedProgressIndicator(ctk.CTkFrame):
    """Shows elapsed time and status messages during analysis.

    Uses only self.after() for updates - NO background threads.
    This is the correct pattern for Tkinter/CustomTkinter.
    """

    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        self.start_time = 0.0
        self.status_message = ""
        self.is_running = False

        # Create label
        self.status_label = ctk.CTkLabel(
            self,
            text="",
            font=("Arial", 11),
            text_color="#FFB347"
        )
        self.status_label.pack(padx=20, pady=5)

    def start(self, message: str = "Analyzing"):
        """Start showing elapsed time with status message."""
        self.is_running = True
        self.start_time = time.time()
        self.status_message = message
        self._schedule_update()

    def _schedule_update(self):
        """Schedule UI update on main thread. Called repeatedly via self.after()."""
        if self.is_running:
            elapsed = time.time() - self.start_time
            text = f"{self.status_message}... ({elapsed:.1f}s)"
            self.status_label.configure(text=text, text_color="#FFB347")
            # Schedule next update in 100ms
            self.after(100, self._schedule_update)

    def set_status(self, message: str):
        """Update status message while timer is running."""
        self.status_message = message

    def stop(self, final_message: str = None) -> float:
        """Stop timer and return elapsed time."""
        elapsed = time.time() - self.start_time if self.start_time > 0 else 0
        self.is_running = False

        if final_message:
            self.status_label.configure(text=final_message, text_color="#52CC52")
        else:
            self.status_label.configure(text="")

        return elapsed


class AnalysisPanel(ctk.CTkFrame):
    """AI file analysis panel with upload and progress tracking."""

    def __init__(
        self,
        parent,
        on_analysis_callback: Callable,
        on_status_callback: Callable
    ):
        super().__init__(parent)
        self.on_analysis = on_analysis_callback
        self.on_status = on_status_callback
        self.selected_file: Optional[str] = None

        self._build_ui()

    def _build_ui(self):
        """Build analysis panel layout."""
        # Title
        title = ctk.CTkLabel(
            self,
            text="AI Document Analysis",
            font=("Arial", 14, "bold")
        )
        title.pack(padx=20, pady=(20, 10), anchor="w")

        # Enhanced progress indicator
        self.progress_indicator = EnhancedProgressIndicator(self)
        self.progress_indicator.pack(fill="x")

        # Instructions
        instructions = ctk.CTkLabel(
            self,
            text="Upload PDF, CSV, or Excel files for intelligent analysis",
            font=("Arial", 10),
            text_color="#888888"
        )
        instructions.pack(padx=20, pady=(0, 15), anchor="w")

        # File selection frame
        file_frame = ctk.CTkFrame(self, fg_color="#2a2a2a")
        file_frame.pack(fill="x", padx=20, pady=10)

        file_button_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        file_button_frame.pack(fill="x", padx=10, pady=10)

        self.upload_button = ctk.CTkButton(
            file_button_frame,
            text="Select File",
            height=40,
            font=("Arial", 11, "bold"),
            command=self._select_file
        )
        self.upload_button.pack(side="left", padx=(0, 10))

        self.file_label = ctk.CTkLabel(
            file_button_frame,
            text="No file selected",
            font=("Arial", 10),
            text_color="#888888"
        )
        self.file_label.pack(side="left", fill="x", expand=True)

        # File type info
        file_types_label = ctk.CTkLabel(
            file_frame,
            text="Supported: PDF, CSV (.csv), Excel (.xlsx, .xls)",
            font=("Arial", 9),
            text_color="#666666"
        )
        file_types_label.pack(padx=10, pady=(0, 10), anchor="w")

        # Analysis button
        self.analyze_button = ctk.CTkButton(
            self,
            text="Analyze",
            height=40,
            font=("Arial", 12, "bold"),
            command=self._on_analyze_clicked,
            state="disabled"
        )
        self.analyze_button.pack(fill="x", padx=20, pady=10)

        # Results display
        results_title = ctk.CTkLabel(
            self,
            text="Analysis Results:",
            font=("Arial", 12, "bold")
        )
        results_title.pack(padx=20, pady=(15, 10), anchor="w")

        self.results_text = ctk.CTkTextbox(
            self,
            height=300,
            font=("Courier", 10),
            wrap="word"
        )
        self.results_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.results_text.configure(state="disabled")

    def _select_file(self):
        """Open file browser dialog."""
        filetypes = [
            ("Document Files", "*.pdf *.csv *.xlsx *.xls"),
            ("PDF Files", "*.pdf"),
            ("CSV Files", "*.csv"),
            ("Excel Files", "*.xlsx *.xls"),
            ("All Files", "*.*")
        ]

        file_path = filedialog.askopenfilename(
            title="Select file for analysis",
            filetypes=filetypes
        )

        if file_path:
            self.selected_file = file_path
            # Handle both Windows and Unix paths
            filename = file_path.replace("/", "\\").split("\\")[-1]
            self.file_label.configure(text=filename, text_color="white")
            self.analyze_button.configure(state="normal")
            self.on_status(f"Selected: {filename}")

    def _on_analyze_clicked(self):
        """Handle analyze button click."""
        if not self.selected_file:
            self.on_status("Please select a file first")
            return

        self.on_analysis(self.selected_file)

    def disable_upload_button(self):
        """Disable upload during analysis."""
        self.upload_button.configure(state="disabled")
        self.analyze_button.configure(state="disabled")

    def enable_upload_button(self):
        """Enable upload after analysis completes."""
        self.upload_button.configure(state="normal")
        if self.selected_file:
            self.analyze_button.configure(state="normal")

    def display_results(self, results: str):
        """Display analysis results."""
        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", results)
        self.results_text.configure(state="disabled")

    def clear_results(self):
        """Clear results display."""
        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", "end")
        self.results_text.configure(state="disabled")

    def show_progress(self, message: str = "Analyzing"):
        """Show progress indicator with elapsed time."""
        self.progress_indicator.start(message)

    def update_progress_message(self, message: str):
        """Update progress message while analyzing."""
        self.progress_indicator.set_status(message)

    def hide_progress(self, final_message: str = None) -> float:
        """Hide progress indicator and return elapsed time."""
        return self.progress_indicator.stop(final_message)
