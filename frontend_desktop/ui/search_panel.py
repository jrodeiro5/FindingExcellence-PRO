"""File search panel component."""

import os
import re
import sys
import tkinter.filedialog as filedialog
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional

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


class SearchPanel(ctk.CTkFrame):
    """File search panel with keyword input and folder selection."""

    def __init__(
        self,
        parent,
        on_search_callback: Callable,
        on_cancel_callback: Callable,
        on_status_callback: Callable
    ):
        super().__init__(parent)
        self.on_search = on_search_callback
        self.on_cancel = on_cancel_callback
        self.on_status = on_status_callback

        # Default folders from environment
        self.search_folders = self._get_default_folders()

        self._build_ui()

    def _get_default_folders(self) -> List[str]:
        """Get default search folders from environment or use Desktop/Downloads."""
        try:
            default = os.getenv("DEFAULT_SEARCH_FOLDERS", "")
            if default:
                return [f.strip() for f in default.split(",")]
        except:
            pass

        # Fallback to Desktop and Downloads
        username = os.getenv("USERNAME", "User")
        return [
            f"C:\\Users\\{username}\\Desktop",
            f"C:\\Users\\{username}\\Downloads"
        ]

    def _build_ui(self):
        """Build search panel layout with Ayesa branding."""
        # Title
        title = ctk.CTkLabel(
            self,
            text="File Search",
            font=FONTS["heading"],
            text_color=COLORS["primary"]
        )
        title.pack(padx=15, pady=(10, 5), anchor="w")

        # Keyword frame
        keyword_frame = ctk.CTkFrame(self, fg_color="transparent")
        keyword_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(
            keyword_frame,
            text="Keywords:",
            font=FONTS["body"],
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=(0, 10))

        self.keyword_entry = ctk.CTkEntry(
            keyword_frame,
            placeholder_text="e.g., invoice, report, data...",
            height=35,
            font=FONTS["body"],
            fg_color=COLORS["surface"],
            text_color=COLORS["text_secondary"],
            border_color=COLORS["primary"],
            border_width=1
        )
        self.keyword_entry.pack(side="left", fill="x", expand=True)
        self.keyword_entry.bind("<Return>", lambda e: self._on_search_clicked())

        # Case sensitive checkbox
        self.case_sensitive_var = ctk.BooleanVar(value=False)
        self.case_sensitive_check = ctk.CTkCheckBox(
            keyword_frame,
            text="Case Sensitive",
            variable=self.case_sensitive_var,
            font=FONTS["small"],
            text_color=COLORS["text_primary"],
            fg_color=COLORS["primary"],
            hover_color="#0000A8",
            border_color=COLORS["primary"]
        )
        self.case_sensitive_check.pack(side="left", padx=(10, 0))

        # Date range frame
        date_frame = ctk.CTkFrame(self, fg_color="transparent")
        date_frame.pack(fill="x", padx=15, pady=4)

        ctk.CTkLabel(
            date_frame,
            text="Date:",
            font=FONTS["small"],
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=(0, 5))

        # Start date
        ctk.CTkLabel(
            date_frame,
            text="From:",
            font=FONTS["small"],
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=(5, 2))
        self.start_date_entry = ctk.CTkEntry(
            date_frame,
            placeholder_text="YYYY-MM-DD",
            width=95,
            height=25,
            font=FONTS["small"],
            fg_color=COLORS["surface"],
            text_color=COLORS["text_secondary"],
            border_color=COLORS["primary"],
            border_width=1
        )
        self.start_date_entry.pack(side="left", padx=(0, 5))

        # End date
        ctk.CTkLabel(
            date_frame,
            text="To:",
            font=FONTS["small"],
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=(5, 2))
        self.end_date_entry = ctk.CTkEntry(
            date_frame,
            placeholder_text="YYYY-MM-DD",
            width=95,
            height=25,
            font=FONTS["small"],
            fg_color=COLORS["surface"],
            text_color=COLORS["text_secondary"],
            border_color=COLORS["primary"],
            border_width=1
        )
        self.end_date_entry.pack(side="left", padx=(0, 5))

        # Clear dates button
        self.clear_dates_button = ctk.CTkButton(
            date_frame,
            text="Clear",
            width=50,
            height=25,
            font=FONTS["small"],
            fg_color=COLORS["accent"],
            text_color=COLORS["background"],
            hover_color="#E01670",
            command=self._clear_dates
        )
        self.clear_dates_button.pack(side="left", padx=(2, 0))

        # Exclude keywords frame
        exclude_frame = ctk.CTkFrame(self, fg_color="transparent")
        exclude_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(
            exclude_frame,
            text="Exclude:",
            font=FONTS["body"],
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=(0, 10))

        self.exclude_entry = ctk.CTkEntry(
            exclude_frame,
            placeholder_text="e.g., temp, backup, old...",
            height=35,
            font=FONTS["body"],
            fg_color=COLORS["surface"],
            text_color=COLORS["text_secondary"],
            border_color=COLORS["primary"],
            border_width=1
        )
        self.exclude_entry.pack(side="left", fill="x", expand=True)

        # File type frame
        filetype_frame = ctk.CTkFrame(self, fg_color="transparent")
        filetype_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(
            filetype_frame,
            text="File Types:",
            font=FONTS["body"],
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=(0, 10))

        self.file_type_var = ctk.StringVar(value="All")
        self.file_type_dropdown = ctk.CTkComboBox(
            filetype_frame,
            variable=self.file_type_var,
            values=["All", "Documents (.docx, .pdf, .txt)", "Spreadsheets (.xlsx, .xls, .csv)", "Images (.png, .jpg, .jpeg, .gif)", "Archives (.zip, .rar, .7z)", "Custom..."],
            height=35,
            font=FONTS["body"],
            fg_color=COLORS["surface"],
            text_color=COLORS["text_secondary"],
            border_color=COLORS["primary"],
            border_width=1
        )
        self.file_type_dropdown.pack(side="left", fill="x", expand=True)
        self.file_type_dropdown.bind("<<ComboboxSelected>>", self._on_file_type_changed)

        # Custom file types entry (initially hidden)
        self.custom_file_types_entry = ctk.CTkEntry(
            filetype_frame,
            placeholder_text=".docx .xlsx .pdf",
            height=35,
            font=FONTS["body"],
            fg_color=COLORS["surface"],
            text_color=COLORS["text_secondary"],
            border_color=COLORS["primary"],
            border_width=1
        )
        # Don't pack yet - will show when "Custom..." is selected

        # File size frame
        filesize_frame = ctk.CTkFrame(self, fg_color="transparent")
        filesize_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(
            filesize_frame,
            text="Size:",
            font=FONTS["body"],
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=(0, 10))

        # Min size
        ctk.CTkLabel(
            filesize_frame,
            text="Min:",
            font=FONTS["small"],
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=(5, 2))

        self.min_size_entry = ctk.CTkEntry(
            filesize_frame,
            placeholder_text="0",
            width=60,
            height=35,
            font=FONTS["body"],
            fg_color=COLORS["surface"],
            text_color=COLORS["text_secondary"],
            border_color=COLORS["primary"],
            border_width=1
        )
        self.min_size_entry.pack(side="left", padx=(0, 5))

        # Max size
        ctk.CTkLabel(
            filesize_frame,
            text="Max:",
            font=FONTS["small"],
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=(5, 2))

        self.max_size_entry = ctk.CTkEntry(
            filesize_frame,
            placeholder_text="999",
            width=60,
            height=35,
            font=FONTS["body"],
            fg_color=COLORS["surface"],
            text_color=COLORS["text_secondary"],
            border_color=COLORS["primary"],
            border_width=1
        )
        self.max_size_entry.pack(side="left", padx=(0, 5))

        # Size unit dropdown
        self.size_unit_var = ctk.StringVar(value="MB")
        self.size_unit_dropdown = ctk.CTkComboBox(
            filesize_frame,
            variable=self.size_unit_var,
            values=["KB", "MB", "GB"],
            width=50,
            height=35,
            font=FONTS["body"],
            fg_color=COLORS["surface"],
            text_color=COLORS["text_secondary"],
            border_color=COLORS["primary"],
            border_width=1
        )
        self.size_unit_dropdown.pack(side="left", padx=(0, 5))

        # Folder selection
        folder_label = ctk.CTkLabel(
            self,
            text="Folders:",
            font=FONTS["small"],
            text_color=COLORS["text_primary"]
        )
        folder_label.pack(padx=15, pady=(5, 2), anchor="w")

        # Folder display (scrollable)
        folder_frame = ctk.CTkFrame(self, fg_color=COLORS["surface"], border_width=1, border_color=COLORS["border"])
        folder_frame.pack(fill="x", padx=15, pady=2)

        self.folder_text = ctk.CTkTextbox(
            folder_frame,
            height=60,
            font=FONTS["small"],
            wrap="word",
            fg_color=COLORS["surface"],
            text_color=COLORS["text_secondary"]
        )
        self.folder_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.folder_text.configure(state="disabled")

        # Update folder display
        self._update_folder_display()

        # Folder buttons frame
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=15, pady=3)

        ctk.CTkButton(
            button_frame,
            text="Browse",
            width=70,
            height=24,
            font=FONTS["small"],
            fg_color=COLORS["primary"],
            text_color=COLORS["background"],
            hover_color="#0000A8",
            command=self._browse_folder
        ).pack(side="left", padx=(0, 5))

        ctk.CTkButton(
            button_frame,
            text="Clear All",
            width=70,
            height=24,
            font=FONTS["small"],
            fg_color=COLORS["accent"],
            text_color=COLORS["background"],
            hover_color="#E01670",
            command=self._clear_folders
        ).pack(side="left", padx=(0, 5))

        # Button container for search/cancel toggle
        self.button_container = ctk.CTkFrame(self, fg_color="transparent")
        self.button_container.pack(fill="x", padx=15, pady=5)

        # Search button
        self.search_button = ctk.CTkButton(
            self.button_container,
            text="Search",
            height=40,
            font=FONTS["heading"],
            fg_color=COLORS["primary"],
            text_color=COLORS["background"],
            hover_color="#0000A8",
            command=self._on_search_clicked
        )
        self.search_button.pack(fill="x")

        # Cancel button (hidden initially)
        self.cancel_button = ctk.CTkButton(
            self.button_container,
            text="Cancel Search",
            height=40,
            font=FONTS["heading"],
            fg_color=COLORS["accent"],
            text_color=COLORS["background"],
            hover_color="#E01670",
            command=self._on_cancel_clicked
        )
        # Don't pack yet - will show when search starts

    def _update_folder_display(self):
        """Update folder display text."""
        self.folder_text.configure(state="normal")
        self.folder_text.delete("1.0", "end")

        if self.search_folders:
            for folder in self.search_folders:
                self.folder_text.insert("end", f"{folder}\n")
        else:
            self.folder_text.insert("end", "No folders selected")

        self.folder_text.configure(state="disabled")

    def _browse_folder(self):
        """Open folder browser dialog."""
        folder = filedialog.askdirectory(title="Select folder to search")
        if folder and folder not in self.search_folders:
            self.search_folders.append(folder)
            self._update_folder_display()
            self.on_status(f"Added: {folder}")

    def _clear_folders(self):
        """Clear all selected folders."""
        self.search_folders.clear()
        self._update_folder_display()
        self.on_status("Cleared all folders")

    def _clear_dates(self):
        """Clear date input fields."""
        self.start_date_entry.delete(0, "end")
        self.end_date_entry.delete(0, "end")
        self.on_status("Date filters cleared")

    def _on_file_type_changed(self, event=None):
        """Handle file type dropdown change."""
        selected = self.file_type_var.get()
        if selected == "Custom...":
            # Show custom file types entry
            self.custom_file_types_entry.pack(side="left", fill="x", expand=True, padx=(5, 0))
        else:
            # Hide custom file types entry
            self.custom_file_types_entry.pack_forget()

    def _get_file_type_extensions(self) -> list:
        """Get file extensions based on selected file type."""
        selected = self.file_type_var.get()

        type_map = {
            "All": [],
            "Documents (.docx, .pdf, .txt)": [".docx", ".pdf", ".txt", ".doc"],
            "Spreadsheets (.xlsx, .xls, .csv)": [".xlsx", ".xls", ".csv", ".xlsm"],
            "Images (.png, .jpg, .jpeg, .gif)": [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff"],
            "Archives (.zip, .rar, .7z)": [".zip", ".rar", ".7z", ".tar", ".gz"],
        }

        if selected in type_map:
            return type_map[selected]
        elif selected == "Custom...":
            # Parse custom extensions
            custom_text = self.custom_file_types_entry.get().strip()
            if custom_text:
                # Split by space or comma
                extensions = re.split(r'[,\s]+', custom_text)
                # Ensure they start with dot
                return ["." + ext.lstrip(".") if ext else "" for ext in extensions if ext]
            return []
        return []

    def _parse_file_size(self, size_str: str, unit: str) -> Optional[int]:
        """Parse file size string and convert to bytes."""
        if not size_str.strip():
            return None

        try:
            size_num = float(size_str.strip())
            unit_multiplier = {
                "KB": 1024,
                "MB": 1024 * 1024,
                "GB": 1024 * 1024 * 1024
            }
            return int(size_num * unit_multiplier.get(unit, 1024 * 1024))
        except ValueError:
            return None

    def _validate_date(self, date_str: str) -> bool:
        """
        Validate date string format (YYYY-MM-DD).

        Args:
            date_str: Date string to validate

        Returns:
            True if valid or empty, False otherwise
        """
        if not date_str.strip():
            return True  # Empty is valid (no filter)

        # Check format
        pattern = r'^\d{4}-\d{2}-\d{2}$'
        if not re.match(pattern, date_str):
            return False

        # Validate it's a real date
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def _on_search_clicked(self):
        """Handle search button click."""
        keyword = self.keyword_entry.get().strip()

        if not keyword:
            self.on_status("Please enter search keywords")
            return

        if not self.search_folders:
            self.on_status("Please select at least one folder")
            return

        # Get and validate dates
        start_date = self.start_date_entry.get().strip()
        end_date = self.end_date_entry.get().strip()

        if start_date and not self._validate_date(start_date):
            self.on_status("Invalid start date format (use YYYY-MM-DD)")
            return

        if end_date and not self._validate_date(end_date):
            self.on_status("Invalid end date format (use YYYY-MM-DD)")
            return

        # Get exclude keywords
        exclude_keywords = self.exclude_entry.get().strip()
        exclude_list = [kw.strip() for kw in exclude_keywords.split(",") if kw.strip()] if exclude_keywords else []

        # Get file type extensions
        file_extensions = self._get_file_type_extensions()

        # Get file size filters
        min_size = self._parse_file_size(self.min_size_entry.get(), self.size_unit_var.get())
        max_size = self._parse_file_size(self.max_size_entry.get(), self.size_unit_var.get())

        # Validate size filters
        if min_size and max_size and min_size > max_size:
            self.on_status("Min size cannot be greater than max size")
            return

        # Pass all parameters
        self.on_search(
            keyword,
            self.search_folders,
            self.case_sensitive_var.get(),
            start_date if start_date else None,
            end_date if end_date else None,
            exclude_list,
            file_extensions,
            min_size,
            max_size
        )

    def _on_cancel_clicked(self):
        """Handle cancel button click."""
        self.on_cancel()

    def set_searching_state(self, is_searching: bool):
        """Toggle between search/cancel button visibility and disable inputs."""
        if is_searching:
            self.search_button.pack_forget()
            self.cancel_button.pack(fill="x")
            self.keyword_entry.configure(state="disabled")
            self.case_sensitive_check.configure(state="disabled")
            self.start_date_entry.configure(state="disabled")
            self.end_date_entry.configure(state="disabled")
            self.clear_dates_button.configure(state="disabled")
        else:
            self.cancel_button.pack_forget()
            self.search_button.pack(fill="x")
            self.keyword_entry.configure(state="normal")
            self.case_sensitive_check.configure(state="normal")
            self.start_date_entry.configure(state="normal")
            self.end_date_entry.configure(state="normal")
            self.clear_dates_button.configure(state="normal")

    def disable_search_button(self):
        """Disable search button during search (legacy method)."""
        self.set_searching_state(True)

    def enable_search_button(self):
        """Enable search button after search completes (legacy method)."""
        self.set_searching_state(False)
