"""Interactive results table with right-click context menu and file operations."""

import os
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import customtkinter as ctk

# Handle branding imports with fallback
try:
    from ..branding import COLORS
except ImportError:
    # Fallback: add parent directory to path
    parent_dir = str(Path(__file__).parent.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from branding import COLORS


class InteractiveResultsPanel(ctk.CTkFrame):
    """Interactive results table with file operations (copy, open, etc)."""

    def __init__(self, parent, on_status_callback: Optional[Callable] = None):
        super().__init__(parent, fg_color=COLORS["background"])
        self.on_status = on_status_callback or (lambda x: None)
        self.results: List[Dict[str, Any]] = []
        self.filtered_results: List[Dict[str, Any]] = []  # Results after quick filter
        self.selected_row: Optional[int] = None
        self.sort_column: str = "filename"  # Default sort column
        self.sort_ascending: bool = True   # Sort direction
        self.quick_filter_text: str = ""  # Current quick filter text

        self._build_ui()

    def _build_ui(self):
        """Build interactive results panel layout with Ayesa branding."""
        # Header frame
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 10))

        self.title_label = ctk.CTkLabel(
            header_frame,
            text="Results",
            font=("Arial", 12, "bold"),
            text_color=COLORS["primary"]
        )
        self.title_label.pack(side="left")

        self.count_label = ctk.CTkLabel(
            header_frame,
            text="",
            font=("Arial", 10),
            text_color=COLORS["text_secondary"]
        )
        self.count_label.pack(side="left", padx=(20, 0))

        # Cache status indicator
        self.cache_label = ctk.CTkLabel(
            header_frame,
            text="",
            font=("Arial", 9),
            text_color=COLORS["text_secondary"]
        )
        self.cache_label.pack(side="right")

        # Quick filter frame
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(
            filter_frame,
            text="Quick Filter:",
            font=("Arial", 9),
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=(0, 5))

        self.quick_filter_entry = ctk.CTkEntry(
            filter_frame,
            placeholder_text="Search results by filename or path...",
            height=28,
            font=("Arial", 9),
            fg_color=COLORS["surface"],
            text_color=COLORS["text_secondary"],
            border_color=COLORS["border"],
            border_width=1
        )
        self.quick_filter_entry.pack(side="left", fill="x", expand=True)
        self.quick_filter_entry.bind("<KeyRelease>", self._on_quick_filter_change)

        # Clear filter button
        ctk.CTkButton(
            filter_frame,
            text="✕ Clear",
            width=60,
            height=28,
            font=("Arial", 9),
            fg_color=COLORS["accent"],
            text_color=COLORS["background"],
            hover_color="#E01670",
            command=self._clear_quick_filter
        ).pack(side="left", padx=(5, 0))

        # Results container (Treeview-like table using Frame + Listbox)
        table_frame = ctk.CTkFrame(self, fg_color=COLORS["surface"], border_width=1, border_color=COLORS["border"])
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Column headers (clickable for sorting)
        header_row = ctk.CTkFrame(table_frame, fg_color=COLORS["primary"], height=25)
        header_row.pack(fill="x")
        header_row.pack_propagate(False)

        # Filename header
        filename_header = ctk.CTkLabel(
            header_row,
            text="Filename ▼",
            font=("Arial", 10, "bold"),
            text_color=COLORS["background"],
            cursor="hand2"
        )
        filename_header.pack(side="left", padx=8, fill="x", expand=True)
        filename_header.bind("<Button-1>", lambda e: self._sort_results("filename"))

        # Path header
        path_header = ctk.CTkLabel(
            header_row,
            text="Path",
            font=("Arial", 10, "bold"),
            text_color=COLORS["background"],
            cursor="hand2"
        )
        path_header.pack(side="left", padx=8, fill="x", expand=True)
        path_header.bind("<Button-1>", lambda e: self._sort_results("path"))

        # Modified header
        modified_header = ctk.CTkLabel(
            header_row,
            text="Modified",
            font=("Arial", 10, "bold"),
            text_color=COLORS["background"],
            cursor="hand2",
            width=130
        )
        modified_header.pack(side="left", padx=8)
        modified_header.bind("<Button-1>", lambda e: self._sort_results("modified"))

        # Type header
        type_header = ctk.CTkLabel(
            header_row,
            text="Type",
            font=("Arial", 10, "bold"),
            text_color=COLORS["background"],
            cursor="hand2",
            width=60
        )
        type_header.pack(side="left", padx=8)
        type_header.bind("<Button-1>", lambda e: self._sort_results("type"))

        # Store header references for updating sort indicators
        self.headers = {
            "filename": filename_header,
            "path": path_header,
            "modified": modified_header,
            "type": type_header
        }

        # Results list container
        self.list_frame = ctk.CTkFrame(table_frame, fg_color="#0a0a0a")
        self.list_frame.pack(fill="both", expand=True)

        # Scrollbar
        scrollbar = ctk.CTkScrollbar(self.list_frame)
        scrollbar.pack(side="right", fill="y")

        # Results canvas for scrolling
        self.canvas = tk.Canvas(
            self.list_frame,
            bg=COLORS["surface"],
            highlightthickness=0,
            yscrollcommand=scrollbar.set
        )
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.configure(command=self.canvas.yview)

        # Inner frame for results
        self.inner_frame = ctk.CTkFrame(self.canvas, fg_color=COLORS["surface"])
        self.canvas_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        # Bind mousewheel for scrolling
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)
        self.canvas.bind("<Button-5>", self._on_mousewheel)

        # Bind canvas resize to update inner frame width
        self.canvas.bind("<Configure>", self._on_canvas_configure)

    def _on_canvas_configure(self, event):
        """Update inner frame width when canvas resizes."""
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        if event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")

    def _on_quick_filter_change(self, event=None):
        """Handle quick filter text entry changes."""
        self.quick_filter_text = self.quick_filter_entry.get().strip().lower()

        # Filter results based on quick filter text
        if self.quick_filter_text:
            self.filtered_results = [
                r for r in self.results
                if self.quick_filter_text in r.get("filename", "").lower()
                   or self.quick_filter_text in r.get("path", "").lower()
            ]
        else:
            self.filtered_results = self.results

        # Re-display with filtered results
        if self.results:
            self._refresh_display()

    def _clear_quick_filter(self):
        """Clear the quick filter."""
        self.quick_filter_entry.delete(0, "end")
        self.quick_filter_text = ""
        self.filtered_results = self.results

        if self.results:
            self._refresh_display()

        self.on_status("Filter cleared")

    def _refresh_display(self):
        """Refresh the results display with current filtered results."""
        # Sort filtered results based on current sort column
        sorted_results = sorted(
            self.filtered_results,
            key=lambda x: x.get(self.sort_column, "").lower() if isinstance(x.get(self.sort_column), str) else x.get(self.sort_column, 0),
            reverse=not self.sort_ascending
        )

        # Clear previous results
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        if not sorted_results:
            empty_label = ctk.CTkLabel(
                self.inner_frame,
                text="No files match filter.",
                font=("Arial", 11),
                text_color=COLORS["text_secondary"]
            )
            empty_label.pack(padx=10, pady=20)
            self.count_label.configure(text=f"{len(self.filtered_results)}/{len(self.results)} files")
            return

        # Add result rows
        for i, file_info in enumerate(sorted_results):
            self._create_result_row(i, file_info)

        # Update counts
        if self.quick_filter_text:
            self.count_label.configure(text=f"{len(self.filtered_results)}/{len(self.results)} files")
        else:
            self.count_label.configure(text=f"{len(self.results)} files")

        # Update cache label
        if hasattr(self, '_is_cached'):
            if self._is_cached:
                self.cache_label.configure(text="📦 Cached results")
            else:
                self.cache_label.configure(text="🔍 Live search")

        # Update canvas scroll region
        self.inner_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _sort_results(self, column: str):
        """Sort results by clicking column header."""
        # Toggle sort direction if same column
        if self.sort_column == column:
            self.sort_ascending = not self.sort_ascending
        else:
            self.sort_column = column
            self.sort_ascending = True

        # Update header indicators
        for col, header in self.headers.items():
            if col == column:
                arrow = "▲" if self.sort_ascending else "▼"
                header.configure(text=f"{col.capitalize()} {arrow}", text_color="#CCCCCC")
            else:
                header.configure(text=col.capitalize(), text_color="#999999")

        # Re-display with new sort (preserves current quick filter)
        if self.results:
            self._refresh_display()

    def display_results(self, results: List[Dict[str, Any]], is_cached: bool = False):
        """
        Display file search results in interactive table.

        Args:
            results: List of file result dicts
            is_cached: Whether these results came from cache
        """
        self.results = results
        self.filtered_results = results  # Initialize filtered_results with all results
        self._is_cached = is_cached

        # Clear quick filter when new results are displayed
        self.quick_filter_entry.delete(0, "end")
        self.quick_filter_text = ""

        # Sort results based on current sort column
        sorted_results = sorted(
            results,
            key=lambda x: x.get(self.sort_column, "").lower() if isinstance(x.get(self.sort_column), str) else x.get(self.sort_column, 0),
            reverse=not self.sort_ascending
        )

        # Clear previous results
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        if not sorted_results:
            empty_label = ctk.CTkLabel(
                self.inner_frame,
                text="No files found.",
                font=("Arial", 11),
                text_color=COLORS["text_secondary"]
            )
            empty_label.pack(padx=10, pady=20)
            self.count_label.configure(text="0 files")
            self.cache_label.configure(text="")
            return

        # Add result rows (use sorted results)
        for i, file_info in enumerate(sorted_results):
            self._create_result_row(i, file_info)

        # Update counts
        self.count_label.configure(text=f"{len(results)} files")

        if is_cached:
            self.cache_label.configure(text="📦 Cached results")
        else:
            self.cache_label.configure(text="🔍 Live search")

        # Update canvas scroll region
        self.inner_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _create_result_row(self, index: int, file_info: Dict[str, Any]):
        """Create an interactive result row."""
        row_frame = ctk.CTkFrame(self.inner_frame, fg_color=COLORS["background"], height=48)
        row_frame.pack(fill="x", padx=2, pady=2)
        row_frame.pack_propagate(False)

        # Store index for context menu
        row_frame.index = index
        row_frame.file_info = file_info

        # Filename
        filename = file_info.get("filename", "Unknown")
        path = file_info.get("path", "")
        modified = file_info.get("modified", "")
        file_type = file_info.get("type", "file")

        filename_label = ctk.CTkLabel(
            row_frame,
            text=filename,
            font=("Courier", 10),
            text_color=COLORS["primary"],
            anchor="w"
        )
        filename_label.pack(side="left", padx=8, fill="x", expand=True)

        # Path (truncated)
        truncated_path = path if len(path) < 40 else "..." + path[-37:]
        path_label = ctk.CTkLabel(
            row_frame,
            text=truncated_path,
            font=("Courier", 9),
            text_color=COLORS["text_secondary"],
            anchor="w"
        )
        path_label.pack(side="left", padx=8, fill="x", expand=True)

        # Modified date
        modified_label = ctk.CTkLabel(
            row_frame,
            text=modified[:10] if modified else "",
            font=("Courier", 9),
            text_color=COLORS["text_secondary"],
            width=130
        )
        modified_label.pack(side="left", padx=8)

        # File type
        type_label = ctk.CTkLabel(
            row_frame,
            text=file_type[:6],
            font=("Courier", 9),
            text_color=COLORS["text_secondary"],
            width=60
        )
        type_label.pack(side="left", padx=8)

        # Bind events
        for label in [filename_label, path_label, modified_label, type_label]:
            label.bind("<Button-1>", lambda e, r=row_frame: self._on_row_click(r))
            label.bind("<Button-3>", lambda e, r=row_frame: self._show_context_menu(r, e))
            label.bind("<Double-Button-1>", lambda e, r=row_frame: self._on_double_click(r))

        # Hover effect
        row_frame.bind("<Enter>", lambda e, r=row_frame: self._highlight_row(r, True))
        row_frame.bind("<Leave>", lambda e, r=row_frame: self._highlight_row(r, False))
        filename_label.bind("<Enter>", lambda e, r=row_frame: self._highlight_row(r, True))
        filename_label.bind("<Leave>", lambda e, r=row_frame: self._highlight_row(r, False))
        path_label.bind("<Enter>", lambda e, r=row_frame: self._highlight_row(r, True))
        path_label.bind("<Leave>", lambda e, r=row_frame: self._highlight_row(r, False))

    def _on_row_click(self, row_frame):
        """Handle row selection."""
        # Remove previous selection
        for widget in self.inner_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                widget.configure(fg_color=COLORS["background"])

        # Highlight selected row
        row_frame.configure(fg_color="#E8E8F5")
        self.selected_row = row_frame.index

    def _highlight_row(self, row_frame, is_hover):
        """Highlight row on hover."""
        if is_hover and row_frame != self.selected_row:
            row_frame.configure(fg_color="#F5F5F9")
        elif not is_hover and row_frame != self.selected_row:
            row_frame.configure(fg_color=COLORS["background"])

    def _on_double_click(self, row_frame):
        """Open file on double-click."""
        file_path = row_frame.file_info.get("path", "")
        if file_path and os.path.exists(file_path):
            try:
                if os.name == "nt":  # Windows
                    os.startfile(file_path)
                elif os.name == "posix":  # macOS/Linux
                    subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", file_path])
                self.on_status(f"Opened: {file_path}")
            except Exception as e:
                self.on_status(f"Error opening file: {e}")

    def _show_context_menu(self, row_frame, event):
        """Show right-click context menu."""
        file_path = row_frame.file_info.get("path", "")
        filename = row_frame.file_info.get("filename", "")

        if not os.path.exists(file_path):
            self.on_status("File no longer exists")
            return

        # Create context menu with Ayesa branding
        context_menu = tk.Menu(
            self.canvas,
            tearoff=False,
            bg=COLORS["surface"],
            fg=COLORS["text_primary"],
            activebackground=COLORS["primary"],
            activeforeground=COLORS["background"]
        )

        context_menu.add_command(
            label="📋 Copy Full Path",
            command=lambda: self._copy_to_clipboard(file_path)
        )
        context_menu.add_command(
            label="📄 Copy Filename",
            command=lambda: self._copy_to_clipboard(filename)
        )
        context_menu.add_separator()
        context_menu.add_command(
            label="📂 Open File Location",
            command=lambda: self._open_folder(file_path)
        )
        context_menu.add_command(
            label="▶️ Open File",
            command=lambda: self._on_double_click(row_frame)
        )
        context_menu.add_separator()
        context_menu.add_command(
            label="ℹ️ File Properties",
            command=lambda: self._show_file_info(file_path)
        )

        # Show menu at cursor position
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def _copy_to_clipboard(self, text: str):
        """Copy text to clipboard."""
        try:
            # Use tkinter's clipboard functionality
            self.clipboard_clear()
            self.clipboard_append(text)
            self.update()  # Required for clipboard to work
            self.on_status(f"Copied: {text[:50]}...")
        except Exception as e:
            self.on_status(f"Copy error: {e}")

    def _open_folder(self, file_path: str):
        """Open file's containing folder."""
        try:
            folder = os.path.dirname(file_path)
            if os.name == "nt":  # Windows
                os.startfile(folder)
            elif os.name == "posix":  # macOS/Linux
                subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", folder])
            self.on_status(f"Opened folder: {folder}")
        except Exception as e:
            self.on_status(f"Error opening folder: {e}")

    def _show_file_info(self, file_path: str):
        """Show file properties in status or dialog."""
        try:
            stat = os.stat(file_path)
            size_mb = stat.st_size / (1024 * 1024)
            from datetime import datetime
            mod_time = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")

            info = f"File: {Path(file_path).name} | Size: {size_mb:.2f} MB | Modified: {mod_time}"
            self.on_status(info)
        except Exception as e:
            self.on_status(f"Error reading file info: {e}")

    def display_analysis_result(self, result: str):
        """Display AI analysis result (text mode)."""
        # Clear previous content
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        # Add analysis text with Ayesa branding
        text_widget = tk.Text(
            self.inner_frame,
            bg=COLORS["surface"],
            fg=COLORS["text_primary"],
            font=("Courier", 9),
            wrap="word",
            height=20,
            insertbackground=COLORS["primary"]
        )
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        text_widget.insert("1.0", result)
        text_widget.configure(state="disabled")

        self.title_label.configure(text="Analysis Results", text_color=COLORS["primary"])
        lines = result.count("\n")
        self.count_label.configure(text=f"{lines} lines")

    def clear_results(self):
        """Clear all results."""
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        self.count_label.configure(text="")
        self.cache_label.configure(text="")
        self.title_label.configure(text="Results")
        self.results = []
        self.selected_row = None

        # Reset canvas
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


import sys
