---
title: Frontend Desktop
topics: [architecture, frontend]
sources:
  - {id: frontend-main, type: file, path: frontend_desktop/main.py}
  - {id: main-window, type: file, path: frontend_desktop/ui/main_window.py}
  - {id: api-client, type: file, path: frontend_desktop/api_client.py}
  - {id: branding, type: file, path: frontend_desktop/branding.py}
  - {id: search-panel, type: file, path: frontend_desktop/ui/search_panel.py}
  - {id: analysis-panel, type: file, path: frontend_desktop/ui/analysis_panel.py}
  - {id: results-panel, type: file, path: frontend_desktop/ui/results_panel.py}
  - {id: treeview-results, type: file, path: frontend_desktop/ui/treeview_results.py}
  - {id: interactive-results, type: file, path: frontend_desktop/ui/interactive_results.py}
  - {id: organizer-panel, type: file, path: frontend_desktop/ui/organizer_panel.py}
  - {id: analysis-results-panel, type: file, path: frontend_desktop/ui/analysis_results_panel.py}
---

# Frontend Desktop

The desktop frontend is a CustomTkinter application that provides the user
interface for FindingExcellence PRO. It runs as a separate process from the
backend and communicates over HTTP for AI features.

## Architecture

The frontend has two execution paths for file search:

1. **Local file search** — runs entirely within the desktop process via
   `frontend_desktop/core/file_search.py`. No backend required. This path
   uses `os.scandir()` with regex keyword matching and SQLite caching,
   importing the same `OptimizedFileSearch` from the backend.
2. **Backend-assisted search** — when the backend is running, the desktop
   can use the backend's search endpoints for features like natural language
   search.

The frontend checks backend health on startup via `BackendClient.health_check()`
and degrades gracefully if the backend is offline.

## UI Structure

The main window ([@main-window]) is `ExcelFinderApp`, a `ctk.CTk` subclass
with a tabbed interface:

- **File Search tab** — `SearchPanel` ([@search-panel]) handles keyword entry,
  folder selection, date range filters, and search/cancel buttons.
- **AI Analysis tab** — `AnalysisPanel` ([@analysis-panel]) handles file upload,
  analysis type selection, and progress indication. Results display through
  `AnalysisResultsPanel` ([@analysis-results-panel]).
- **File Organizer tab** — `OrganizerPanel` ([@organizer-panel]) for file
  organization tasks.
- **Results** — `ResultsPanel` ([@results-panel]) and `TreeviewResultsPanel`
  ([@treeview-results]) display search results. `InteractiveResultsPanel`
  ([@interactive-results]) provides detailed view of individual results.

The window is 900x700 pixels with an Ayesa branding header. The color scheme
and fonts come from `branding.COLORS` and `branding.FONTS` ([@branding]).

## Threading Model

All UI work runs on the main thread. Long-running operations (file search,
AI analysis, file organization) run in background `threading.Thread` instances.
UI updates from background threads use `self.after(0, callback)` to schedule
updates on the main thread. Direct widget access from background threads
causes crashes.

Three thread types exist:

- `self.search_thread` — filename search (local or backend-assisted).
- `self.analysis_thread` — AI document analysis.
- `self.organizer_thread` — file organization operations.

Each thread sets `self.cancel_event` to support cancellation.

## API Client

`BackendClient` ([@api-client]) wraps `requests.Session` and provides typed
methods for all backend endpoints:

- `health_check()` — verifies backend is reachable.
- `search_files_async()` — starts async filename search, returns `search_id`.
- `get_search_progress()` — polls search progress by ID.
- `analyze_file()` — uploads and analyzes a single file (180s timeout).
- `analyze_batch()` — uploads and analyzes 2-100 files (360s timeout).
- `ocr_from_image()` — extracts text from images via vision models.
- Search history CRUD: `get_search_history()`, `rerun_search()`,
  `delete_search_history()`.

Error responses from the backend include `error_code` fields that the client
maps to user-friendly messages.

## Entry Point

`frontend_desktop/main.py` ([@frontend-main]) is the desktop entry point.
It loads `.env` via `python-dotenv`, creates the `ExcelFinderApp`, and calls
`mainloop()`. Import errors exit with a helpful message directing the user
to run the setup script.

## Configuration

The frontend reads `OLLAMA_HOST` and `BACKEND_PORT` from `.env` (when present)
to locate the backend. The default backend URL is `http://localhost:8000`.
