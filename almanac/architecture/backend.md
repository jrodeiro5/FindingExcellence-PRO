---
title: Backend Server
topics: [architecture, backend]
sources:
  - {id: main-py, type: file, path: backend/main.py}
  - {id: logging-setup, type: file, path: backend/utils/logging_setup.py}
  - {id: config-manager, type: file, path: backend/core/config_manager.py}
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
"healthy", "version": "2.0.0"}` and is used by the desktop frontend to verify the backend is
reachable.

## Request Flow

All endpoints follow the same pattern:

1. Parse the request body with a `pydantic.BaseModel`.
2. Call into a core service class.
3. Return a JSON response or raise `HTTPException` on failure.

The backend exposes two categories of endpoints:

- **Search endpoints** (`/api/search/*`) — filename search, content search,
  natural language search, and search history. These run entirely within the
  backend process; the algorithms are covered in [Search Subsystem](search).
- **AI endpoints** (`/api/analyze`, `/api/analyze/batch`, `/api/ocr`) — require
  a running Ollama instance. They return `503` when AI is unavailable; the
  Ollama client, model warmup, and optional PII/NER/chunking services are
  covered in [AI Integration](ai-integration).

The frontend desktop application communicates with the backend through
`frontend_desktop/api_client.py`, which wraps `requests` with timeout handling
and user-friendly error messages.

## Search and AI Details

The search internals (filename, content, and natural-language search, SQLite
caching, and search history) live on [Search Subsystem](search), and the Ollama
client, model warmup, fallback chains, and usage tracking live on
[AI Integration](ai-integration). This page documents the request lifecycle,
logging, and configuration shared across all endpoints.

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
