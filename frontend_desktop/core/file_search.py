"""
File search module.

This module contains functionality for searching files by filename criteria.
Pure Python implementation - no API dependencies.
"""

import datetime
import logging
import os
import threading
import time


class FileSearch:
    """
    Handles filename-based searching.
    """

    def __init__(self, cancel_event=None):
        """
        Initialize the file search functionality.

        Args:
            cancel_event: Threading event for cancellation
        """
        self.cancel_event = cancel_event or threading.Event()

    def search_by_filename(self, folder_paths, filename_keywords,
                          start_date=None, end_date=None,
                          exclude_keywords=None, case_sensitive=False,
                          supported_extensions=None,
                          status_callback=None):
        """
        Search for files matching given criteria.

        Args:
            folder_paths: Root folder(s) to search in (string or list)
            filename_keywords: List of keywords to find in filenames
            start_date: Earliest modified date to include
            end_date: Latest modified date to include
            exclude_keywords: Keywords to exclude from results
            case_sensitive: Whether to perform case-sensitive search
            supported_extensions: Tuple of file extensions to include (None = all files)
            status_callback: Function to call with status updates

        Returns:
            list: List of matching files with metadata (name, path, modified_date)
        """
        # If None, search ALL file types (no extension filter)
        filter_by_extension = supported_extensions is not None and len(supported_extensions) > 0

        if exclude_keywords is None:
            exclude_keywords = []

        # Convert folder_paths to list if a string was provided
        if isinstance(folder_paths, str):
            folder_paths = [folder_paths]

        # Log the folder paths to help with debugging
        logging.info(f"Searching in folder paths: {folder_paths}")
        logging.info(f"Extension filter: {supported_extensions if filter_by_extension else 'ALL FILES'}")

        found_files = []
        processed_dirs = 0
        processed_files = 0
        last_update_time = time.time()
        UPDATE_INTERVAL = 0.3  # Update UI every 300ms

        try:
            # Iterate through each provided folder
            for folder_idx, folder_path in enumerate(folder_paths):
                # Check cancellation at folder level - EARLY RETURN
                if self.cancel_event.is_set():
                    logging.info("Search cancelled at folder level.")
                    return found_files

                if not os.path.isdir(folder_path):
                    logging.warning(f"Skipping non-existent folder: {folder_path}")
                    continue

                if status_callback:
                    status_callback(f"Searching folder {folder_idx + 1}/{len(folder_paths)}: {os.path.basename(folder_path)}...")

                for root_dir, dirs, files in os.walk(folder_path):
                    # Check cancellation at directory level - EARLY RETURN
                    if self.cancel_event.is_set():
                        logging.info("Search cancelled during directory walk.")
                        return found_files

                    processed_dirs += 1
                    current_time = time.time()

                    # Update status every 50 directories OR every 300ms
                    if status_callback and (processed_dirs % 50 == 0 or current_time - last_update_time > UPDATE_INTERVAL):
                        status_callback(f"Scanning: {processed_dirs} dirs, {processed_files} files, {len(found_files)} matches")
                        last_update_time = current_time

                    # Filter out excluded directories (only if we have exclusions)
                    if exclude_keywords:
                        if not case_sensitive:
                            dirs[:] = [d for d in dirs if not any(ex.lower() in d.lower() for ex in exclude_keywords)]
                        else:
                            dirs[:] = [d for d in dirs if not any(ex in d for ex in exclude_keywords)]

                    for file in files:
                        # Check cancellation at file level - EARLY RETURN
                        if self.cancel_event.is_set():
                            logging.info("Search cancelled during file processing.")
                            return found_files

                        processed_files += 1

                        file_lower = file.lower()

                        # Extension filter - only apply if we have extensions to filter by
                        if filter_by_extension:
                            if not file_lower.endswith(supported_extensions):
                                continue

                        filename_to_check = file if case_sensitive else file_lower

                        # Check if filename contains any of the keywords
                        if filename_keywords:
                            match_found = False
                            for kw in filename_keywords:
                                kw_to_check = kw if case_sensitive else kw.lower()
                                if kw_to_check in filename_to_check:
                                    match_found = True
                                    break
                            if not match_found:
                                continue

                        file_path = os.path.join(root_dir, file)

                        # Check date range if specified
                        if start_date or end_date:
                            try:
                                mod_timestamp = os.path.getmtime(file_path)
                                mod_date = datetime.date.fromtimestamp(mod_timestamp)
                                if start_date and mod_date < start_date:
                                    continue
                                if end_date and mod_date > end_date:
                                    continue
                            except OSError as e:
                                logging.warning(f"Could not getmtime for {file_path}: {e}")
                                continue

                        # Get formatted modified time
                        try:
                            mod_time_dt = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                            formatted_time = mod_time_dt.strftime('%Y-%m-%d %H:%M:%S')
                        except OSError:
                            formatted_time = "Unknown"

                        # Add to results
                        found_files.append({
                            "filename": file,
                            "path": file_path,
                            "modified": formatted_time,
                            "type": file_path.split('.')[-1] if '.' in file_path else 'unknown'
                        })

                        # Update status when files are found (every 10 files)
                        if len(found_files) % 10 == 0 and status_callback:
                            status_callback(f"Found {len(found_files)} files...")

        except Exception as e:
            logging.error(f"Error during filename search: {e}", exc_info=True)
            raise

        # Final status update
        if status_callback:
            if self.cancel_event.is_set():
                status_callback(f"Search cancelled: {len(found_files)} files found.")
            else:
                status_callback(f"Search completed: {len(found_files)} files found.")

        return found_files

    def cancel(self):
        """
        Cancel an ongoing search.
        """
        self.cancel_event.set()
