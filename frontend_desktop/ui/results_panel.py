"""Results display panel for search and analysis results."""

from typing import Any, Dict, List

import customtkinter as ctk


class ResultsPanel(ctk.CTkFrame):
    """Panel for displaying file search and analysis results."""

    def __init__(self, parent):
        super().__init__(parent, fg_color="#1a1a1a")

        self._build_ui()

    def _build_ui(self):
        """Build results panel layout."""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 10))

        self.title_label = ctk.CTkLabel(
            header_frame,
            text="Results",
            font=("Arial", 12, "bold")
        )
        self.title_label.pack(side="left")

        self.count_label = ctk.CTkLabel(
            header_frame,
            text="",
            font=("Arial", 10),
            text_color="#888888"
        )
        self.count_label.pack(side="right")

        # Results text widget
        self.results_text = ctk.CTkTextbox(
            self,
            font=("Courier", 9),
            wrap="word",
            activate_scrollbars=True
        )
        self.results_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.results_text.configure(state="disabled")

    def display_results(self, results: List[Dict[str, Any]]):
        """
        Display file search results.

        Args:
            results: List of file result dicts with keys: filename, path, modified_date
        """
        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", "end")

        if not results:
            self.results_text.insert("end", "No files found.")
            self.count_label.configure(text="0 files")
        else:
            # Format results nicely
            for i, file_info in enumerate(results, 1):
                filename = file_info.get("filename", "Unknown")
                path = file_info.get("path", "")
                modified = file_info.get("modified_date", "")

                # Header for each file
                self.results_text.insert("end", f"{i}. {filename}\n", "filename")
                self.results_text.insert("end", f"   Path: {path}\n", "info")
                if modified:
                    self.results_text.insert("end", f"   Modified: {modified}\n", "info")
                self.results_text.insert("end", "\n")

            self.count_label.configure(text=f"{len(results)} files found")

        self.results_text.configure(state="disabled")

    def display_analysis_result(self, result: str):
        """
        Display AI analysis result.

        Args:
            result: Analysis result text
        """
        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", result)
        self.results_text.configure(state="disabled")

        self.title_label.configure(text="Analysis Results")
        lines = result.count("\n")
        self.count_label.configure(text=f"{lines} lines")

    def clear_results(self):
        """Clear all results."""
        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", "end")
        self.results_text.configure(state="disabled")
        self.count_label.configure(text="")
        self.title_label.configure(text="Results")
