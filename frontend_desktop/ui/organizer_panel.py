"""File organizer panel component for the desktop UI."""

import sys
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


class OrganizerPanel(ctk.CTkFrame):
    """File organizer panel with folder selection and clustering parameters."""

    def __init__(
        self,
        parent,
        on_organize_callback: Callable,
        on_status_callback: Callable
    ):
        super().__init__(parent)
        self.on_organize = on_organize_callback
        self.on_status = on_status_callback

        self.selected_folder: Optional[str] = None

        self._build_ui()

    def _build_ui(self):
        """Build organizer panel layout with Ayesa branding."""
        # Title
        title = ctk.CTkLabel(
            self,
            text="File Organizer",
            font=FONTS["heading"],
            text_color=COLORS["primary"]
        )
        title.pack(padx=15, pady=(10, 5), anchor="w")

        # Description
        description = ctk.CTkLabel(
            self,
            text="Organize files into thematic groups using content-based clustering (TF-IDF + KMeans)",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"]
        )
        description.pack(padx=15, pady=(0, 10), anchor="w")

        # Folder selection frame
        folder_frame = ctk.CTkFrame(self, fg_color="transparent")
        folder_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(
            folder_frame,
            text="Folder:",
            font=FONTS["body"],
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=(0, 10))

        self.folder_display = ctk.CTkLabel(
            folder_frame,
            text="No folder selected",
            font=FONTS["body"],
            text_color=COLORS["text_secondary"]
        )
        self.folder_display.pack(side="left", fill="x", expand=True)

        self.select_folder_button = ctk.CTkButton(
            folder_frame,
            text="Browse",
            width=100,
            height=35,
            font=FONTS["body"],
            fg_color=COLORS["primary"],
            text_color=COLORS["background"],
            hover_color="#0000CC",
            command=self._on_folder_select
        )
        self.select_folder_button.pack(side="left", padx=(10, 0))

        # Cluster count frame
        cluster_frame = ctk.CTkFrame(self, fg_color="transparent")
        cluster_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            cluster_frame,
            text="Cluster Count:",
            font=FONTS["body"],
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=(0, 10))

        # Slider for cluster count
        self.cluster_var = ctk.IntVar(value=10)
        self.cluster_slider = ctk.CTkSlider(
            cluster_frame,
            from_=2,
            to=20,
            number_of_steps=18,
            variable=self.cluster_var,
            height=5,
            button_length=20,
            button_color=COLORS["primary"],
            progress_color=COLORS["primary"],
            fg_color=COLORS["surface"]
        )
        self.cluster_slider.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.cluster_label = ctk.CTkLabel(
            cluster_frame,
            text="10",
            font=FONTS["body"],
            text_color=COLORS["text_primary"],
            width=30
        )
        self.cluster_label.pack(side="left")

        # Update label when slider changes
        def _on_cluster_change(value):
            self.cluster_label.configure(text=str(int(value)))

        self.cluster_slider.configure(command=_on_cluster_change)

        # Language selection frame
        lang_frame = ctk.CTkFrame(self, fg_color="transparent")
        lang_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(
            lang_frame,
            text="Language:",
            font=FONTS["body"],
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=(0, 10))

        self.language_var = ctk.StringVar(value="Spanish")
        self.language_dropdown = ctk.CTkComboBox(
            lang_frame,
            variable=self.language_var,
            values=["Spanish", "English"],
            width=150,
            height=35,
            font=FONTS["body"],
            fg_color=COLORS["surface"],
            text_color=COLORS["text_secondary"],
            border_color=COLORS["primary"],
            border_width=1
        )
        self.language_dropdown.pack(side="left", fill="x")

        # Supported formats info
        formats_label = ctk.CTkLabel(
            self,
            text="Supported formats: PDF, Excel (.xlsx, .xls, .xlsm), Word (.docx), Text (.txt, .csv, .md)",
            font=FONTS["small"],
            text_color=COLORS["text_secondary"]
        )
        formats_label.pack(padx=15, pady=(5, 10), anchor="w")

        # Action buttons frame
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=15, pady=(10, 15))

        self.organize_button = ctk.CTkButton(
            button_frame,
            text="Analyze & Organize",
            height=40,
            font=FONTS["body"],
            fg_color=COLORS["primary"],
            text_color=COLORS["background"],
            hover_color="#0000CC",
            command=self._on_organize_clicked
        )
        self.organize_button.pack(side="left", fill="x", expand=True, padx=(0, 5))

        # Clear button
        self.clear_button = ctk.CTkButton(
            button_frame,
            text="Clear",
            height=40,
            width=80,
            font=FONTS["body"],
            fg_color=COLORS["accent"],
            text_color=COLORS["background"],
            hover_color="#E01670",
            command=self._on_clear_clicked
        )
        self.clear_button.pack(side="left", padx=(5, 0))

    def _on_folder_select(self):
        """Handle folder selection."""
        folder = filedialog.askdirectory(title="Select folder to organize")
        if folder:
            self.selected_folder = folder
            # Display shortened path if too long
            display_path = folder if len(folder) <= 60 else f"...{folder[-57:]}"
            self.folder_display.configure(text=display_path)
            self.on_status(f"Selected folder: {folder}")

    def _on_organize_clicked(self):
        """Handle organize button click."""
        if not self.selected_folder:
            self.on_status("Please select a folder first", color="#E5383B")
            return

        cluster_count = self.cluster_var.get()
        language = self.language_var.get().lower()

        self.on_organize(self.selected_folder, cluster_count, language)

    def _on_clear_clicked(self):
        """Clear folder selection and reset to defaults."""
        self.selected_folder = None
        self.folder_display.configure(text="No folder selected")
        self.cluster_var.set(10)
        self.language_var.set("Spanish")
        self.on_status("Selection cleared")

    def disable_controls(self):
        """Disable UI controls during processing."""
        self.select_folder_button.configure(state="disabled")
        self.cluster_slider.configure(state="disabled")
        self.language_dropdown.configure(state="disabled")
        self.organize_button.configure(state="disabled")

    def enable_controls(self):
        """Enable UI controls after processing."""
        self.select_folder_button.configure(state="normal")
        self.cluster_slider.configure(state="normal")
        self.language_dropdown.configure(state="normal")
        self.organize_button.configure(state="normal")
