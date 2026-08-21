---
title: Backend Server
topics: [architecture, backend]
sources:
  - {id: main-py, type: file, path: backend/main.py}
  - {id: file-search-optimized, type: file, path: backend/core/file_search_optimized.py}
  - {id: file-index, type: file, path: backend/core/file_index.py}
  - {id: search-history, type: file, path: backend/core/search_history.py}
  - {id: logging-setup, type: file, path: backend/utils/logging_setup.py}
  - {id: config-manager, type: file, path: backend/core/config_manager.py}
  - {id: content-search, type: file, path: backend/core/content_search.py}
---

# Backend Server

The backend is a FastAPI application running on `127.0.0.1:8000` that exposes
file search, content search, AI analysis, and OCR endpoints. It runs as a
long-lived process started by `start.bat` or launched independently.

## Entry Point and Lifecycle

`backend/main.py` creates a single `FastAPI` instance and registers all API
routes. At module import time it:

1. Loads `.env` via `python-dotenv`.
2. Sets up structured logging through `logging_setup.setup_logging()`
   ([@logging-setup]). Loguru handles both console and rotating file output
   (10 MB rotation, 5 day retention, compressed).
3. Instantiates `FileSearch`, `ContentSearch`, and `SearchHistory` as module-level
   singletons.
4. Attempts to initialize `AISearchService`; if Ollama is unavailable the
   application starts anyway with AI features disabled ([@main-py]).

The server runs via `uvicorn.run(app, host="127.0.0.1", port=8000)` when
executed directly. The health endpoint at `/health` returns `{"status":
"healthy"}` and is used by the desktop frontend to verify the backend is
reachable.

## Request Flow

All endpoints follow the same pattern:

1. Parse the request body with a `pydantic.BaseModel`.
2. Call into a core service class.
3. Return a JSON response or raise `HTTPException` on failure.

The backend exposes two categories of endpoints:

- **Search endpoints** (`/api/search/*`) — filename search, content search,
  natural language search, and search history. These run entirely within the
  backend process.
- **AI endpoints** (`/api/analyze`, `/api/analyze/batch`, `/api/ocr`) — require
  a running Ollama instance. They return `503` when AI is unavailable.

The frontend desktop application communicates with the backend through
`frontend_desktop/api_client.py`, which wraps `requests` with timeout handling
and user-friendly error messages.

## Search Subsystem

The search subsystem lives in `backend/core/` and has three layers:

**Filename search** ([@file-search-optimized]) uses `os.scandir()` instead of
`os.walk()` for faster I/O. It compiles regex patterns once per search, scans
directories recursively, and supports cancellation via `threading.Event`. The
class is named `OptimizedFileSearch` with `FileSearch` as a backward-compatible
alias.

**SQLite caching** ([@file-index]) stores file metadata in `.cache/file_index.db`
with a 1-hour TTL. Cache hits skip filesystem scanning entirely. The cache is
indexed by folder, filename (case-insensitive), and extension. Cache entries
expire based on `indexed_at` timestamps.

**Content search** ([@content-search]) searches text within file contents using a
`ThreadPoolExecutor`. It processes files concurrently and supports cancellation.

## Search History

`SearchHistory` ([@search-history]) persists recent searches in
`.cache/search_history.db`. It deduplicates by keywords + folders, tracks
`search_count`, and trims to `max_history` (default 20) entries by
`last_used_at`.

## Logging

The logging layer ([@logging-setup]) uses Loguru with:

- Colorized console output with module/function/line context.
- Rotating file logs at `finding_excellence.log` (10 MB rotation, 5 day
  retention, ZIP compression).
- An `InterceptHandler` that redirects stdlib logging (FastAPI, uvicorn) into
  Loguru so all output uses the same format.

## Configuration

`ConfigManager` ([@config-manager]) loads and saves `finding_excellence_config.json`
as a simple key-value store. The primary configuration comes from environment
variables loaded via `python-dotenv` (see [Setup](../guides/setup)).
