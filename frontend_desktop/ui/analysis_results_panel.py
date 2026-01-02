"""Specialized results panel for AI analysis output (text-only)."""

import sys
import tkinter as tk
from pathlib import Path
from typing import Callable, Optional

import customtkinter as ctk

# Handle branding imports with fallback
try:
    from ..branding import COLORS, FONTS
except ImportError:
    parent_dir = str(Path(__file__).parent.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from branding import COLORS, FONTS


class AnalysisResultsPanel(ctk.CTkFrame):
    """Large text area for displaying AI analysis results."""

    def __init__(self, parent, on_status_callback: Optional[Callable] = None):
        super().__init__(parent, fg_color=COLORS["background"])
        self.on_status = on_status_callback or (lambda x: None)

        self._build_ui()

    def _build_ui(self):
        """Build analysis results panel with large text area."""
        # Header frame
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 10))

        self.title_label = ctk.CTkLabel(
            header_frame,
            text="Analysis Results",
            font=FONTS["heading"],
            text_color=COLORS["primary"]
        )
        self.title_label.pack(side="left")

        # Copy button
        ctk.CTkButton(
            header_frame,
            text="📋 Copy Results",
            width=100,
            height=28,
            font=FONTS["small"],
            fg_color=COLORS["primary"],
            text_color=COLORS["background"],
            hover_color="#0000A8",
            command=self._copy_results
        ).pack(side="right", padx=(10, 0))

        # Clear button
        ctk.CTkButton(
            header_frame,
            text="✕ Clear",
            width=80,
            height=28,
            font=FONTS["small"],
            fg_color=COLORS["accent"],
            text_color=COLORS["background"],
            hover_color="#E01670",
            command=self._clear_results
        ).pack(side="right")

        # Large text area for analysis output
        text_frame = ctk.CTkFrame(self, fg_color=COLORS["surface"], border_width=1, border_color=COLORS["border"])
        text_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Create scrollable text widget
        self.text_widget = tk.Text(
            text_frame,
            bg=COLORS["surface"],
            fg=COLORS["text_primary"],
            font=("Courier", 11),
            wrap="word",
            insertbackground=COLORS["primary"],
            relief="flat",
            borderwidth=0
        )
        self.text_widget.pack(fill="both", expand=True, padx=10, pady=10)

        # Add scrollbar
        scrollbar = ctk.CTkScrollbar(
            text_frame,
            command=self.text_widget.yview,
            fg_color=COLORS["surface"],
            button_color=COLORS["primary"]
        )
        scrollbar.pack(side="right", fill="y")
        self.text_widget.config(yscrollcommand=scrollbar.set)

    def display_analysis_result(self, result: str):
        """Display AI analysis result in large text area."""
        self.text_widget.config(state="normal")
        self.text_widget.delete("1.0", "end")
        self.text_widget.insert("1.0", result)
        self.text_widget.config(state="disabled")

        # Update title with line count
        line_count = result.count("\n") + 1
        self.title_label.configure(text=f"Analysis Results ({line_count} lines)")

    def _copy_results(self):
        """Copy all results to clipboard."""
        try:
            text = self.text_widget.get("1.0", "end-1c")
            if text:
                self.text_widget.clipboard_clear()
                self.text_widget.clipboard_append(text)
                self.text_widget.update()
                self.on_status("Analysis results copied to clipboard")
            else:
                self.on_status("No results to copy")
        except Exception as e:
            self.on_status(f"Copy error: {e}")

    def _clear_results(self):
        """Clear all results."""
        self.text_widget.config(state="normal")
        self.text_widget.delete("1.0", "end")
        self.text_widget.config(state="disabled")
        self.title_label.configure(text="Analysis Results")
        self.on_status("Results cleared")

    def clear_results(self):
        """Public method to clear results."""
        self._clear_results()
