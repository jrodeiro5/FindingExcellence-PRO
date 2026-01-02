"""File analysis panel component for AI document analysis."""

import sys
import time
import tkinter.filedialog as filedialog
from pathlib import Path
from typing import Callable, Optional

import customtkinter as ctk

# Handle branding imports with fallback
try:
    from ..branding import COLORS, FONTS
except ImportError:
    # Fallback: add parent directory to path
    parent_dir = str(Path(__file__).parent.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from branding import COLORS, FONTS


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

        # Create label with Ayesa branding
        self.status_label = ctk.CTkLabel(
            self,
            text="",
            font=FONTS["body"],
            text_color=COLORS["primary"]
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
            self.status_label.configure(text=text, text_color=COLORS["primary"])
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
            self.status_label.configure(text=final_message, text_color=COLORS["accent"])
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
        self.analysis_type: str = "summary"  # Default analysis type

        self._build_ui()

    def _build_ui(self):
        """Build analysis panel layout with Ayesa branding."""
        # Title
        title = ctk.CTkLabel(
            self,
            text="AI Document Analysis",
            font=FONTS["heading"],
            text_color=COLORS["primary"]
        )
        title.pack(padx=20, pady=(20, 10), anchor="w")

        # Instructions
        instructions = ctk.CTkLabel(
            self,
            text="Upload PDF, CSV, or Excel files for intelligent analysis",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"]
        )
        instructions.pack(padx=20, pady=(0, 15), anchor="w")

        # File selection frame
        file_frame = ctk.CTkFrame(self, fg_color=COLORS["surface"], border_width=1, border_color=COLORS["border"])
        file_frame.pack(fill="x", padx=20, pady=10)

        file_button_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        file_button_frame.pack(fill="x", padx=10, pady=10)

        self.upload_button = ctk.CTkButton(
            file_button_frame,
            text="Select File",
            height=40,
            font=FONTS["heading"],
            fg_color=COLORS["primary"],
            text_color=COLORS["background"],
            hover_color="#0000A8",
            command=self._select_file
        )
        self.upload_button.pack(side="left", padx=(0, 10))

        self.file_label = ctk.CTkLabel(
            file_button_frame,
            text="No file selected",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"]
        )
        self.file_label.pack(side="left", fill="x", expand=True)

        # File type info
        file_types_label = ctk.CTkLabel(
            file_frame,
            text="Supported: PDF, CSV (.csv), Excel (.xlsx, .xls)",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"]
        )
        file_types_label.pack(padx=10, pady=(0, 10), anchor="w")

        # Analysis type selector
        type_label = ctk.CTkLabel(
            self,
            text="Analysis Type:",
            font=FONTS["heading"],
            text_color=COLORS["primary"]
        )
        type_label.pack(padx=20, pady=(15, 10), anchor="w")

        type_frame = ctk.CTkFrame(self, fg_color="transparent")
        type_frame.pack(fill="x", padx=20, pady=(0, 15))

        self.analysis_types = [
            ("Summary", "summary", "Extract key information from the document"),
            ("Key Points", "key_points", "List main points and findings"),
            ("Anomalies", "anomalies", "Detect unusual or notable data points"),
            ("Insights", "insights", "Extract actionable business insights"),
            ("Trends", "trends", "Identify patterns and trends")
        ]

        self.type_var = ctk.StringVar(value="summary")

        for label, value, tooltip in self.analysis_types:
            radio = ctk.CTkRadioButton(
                type_frame,
                text=label,
                variable=self.type_var,
                value=value,
                command=self._on_analysis_type_changed,
                font=FONTS["body"],
                text_color=COLORS["text_primary"]
            )
            radio.pack(side="left", padx=5)

        # Analysis button
        self.analyze_button = ctk.CTkButton(
            self,
            text="Analyze",
            height=40,
            font=FONTS["heading"],
            fg_color=COLORS["primary"],
            text_color=COLORS["background"],
            hover_color="#0000A8",
            command=self._on_analyze_clicked,
            state="disabled"
        )
        self.analyze_button.pack(fill="x", padx=20, pady=10)

        # Enhanced progress indicator (shown only during analysis)
        self.progress_indicator = EnhancedProgressIndicator(self)
        self.progress_indicator.pack(fill="x", padx=20, pady=10)

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
            self.file_label.configure(text=filename, text_color=COLORS["text_primary"])
            self.analyze_button.configure(state="normal")
            self.on_status(f"Selected: {filename}")

    def _on_analysis_type_changed(self):
        """Handle analysis type selection change."""
        self.analysis_type = self.type_var.get()
        self.on_status(f"Analysis type: {self.analysis_type}")

    def _on_analyze_clicked(self):
        """Handle analyze button click."""
        if not self.selected_file:
            self.on_status("Please select a file first")
            return

        self.on_analysis(self.selected_file, self.analysis_type)

    def disable_upload_button(self):
        """Disable upload during analysis."""
        self.upload_button.configure(state="disabled")
        self.analyze_button.configure(state="disabled")

    def enable_upload_button(self):
        """Enable upload after analysis completes."""
        self.upload_button.configure(state="normal")
        if self.selected_file:
            self.analyze_button.configure(state="normal")

    def show_progress(self, message: str = "Analyzing"):
        """Show progress indicator with elapsed time."""
        self.progress_indicator.start(message)

    def update_progress_message(self, message: str):
        """Update progress message while analyzing."""
        self.progress_indicator.set_status(message)

    def hide_progress(self, final_message: str = None) -> float:
        """Hide progress indicator and return elapsed time."""
        return self.progress_indicator.stop(final_message)
