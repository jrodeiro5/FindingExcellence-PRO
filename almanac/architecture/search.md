---
title: Search Subsystem
topics: [architecture, search]
sources:
  - {id: file-search-optimized, type: file, path: backend/core/file_search_optimized.py}
  - {id: file-index, type: file, path: backend/core/file_index.py}
  - {id: content-search, type: file, path: backend/core/content_search.py}
  - {id: file-search-legacy, type: file, path: backend/core/file_search.py}
  - {id: search-progress, type: file, path: backend/core/search_progress.py}
  - {id: search-history, type: file, path: backend/core/search_history.py}
  - {id: ai-services, type: file, path: backend/ai/ai_services.py}
  - {id: filename-fallback, type: file, path: backend/main.py}
---

# Search Subsystem

The search subsystem provides three search modes: filename search, content
search, and natural language search. All modes support cancellation and
progress reporting.

## Filename Search

`OptimizedFileSearch` ([@file-search-optimized]) is the primary search engine.
It replaced the original `FileSearch` implementation ([@file-search-legacy]),
which simply re-exports the optimized class for backward compatibility.

### Algorithm

1. Pre-compile regex patterns from user-supplied keywords (case-sensitive or
   case-insensitive).
2. Recursively scan directories using `os.scandir()` instead of `os.walk()`
   for 3-5x faster I/O.
3. For each file, check: extension filter, keyword match, date range filter.
4. Format modification time as `YYYY-MM-DD HH:MM:SS`.

### Cancellation

A `threading.Event` (`cancel_event`) is checked at each directory scan and
file match. Setting the event stops the search and returns results found so
far.

### Progress Reporting

`SearchProgress` ([@search-progress]) tracks the state of ongoing searches,
including directories scanned, files found, current directory, and elapsed
time. The frontend polls this state to display real-time progress. Callbacks
(`status_callback`, `result_callback`) are invoked during search:

- `status_callback` reports folder progress and running result counts.
- `result_callback` is called for each matching file (enables progressive
  UI updates).

### Caching

When `use_cache=True` and `FileIndex` is importable, the search checks the
SQLite cache first. Cache entries expire after 1 hour (configurable via
`cache_ttl`). Cache hits skip filesystem scanning entirely.

## File Index (SQLite Cache)

`FileIndex` ([@file-index]) stores file metadata in `.cache/file_index.db`:

```sql
CREATE TABLE files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    folder TEXT NOT NULL,
    filename TEXT NOT NULL,
    path TEXT UNIQUE NOT NULL,
    modified_time INTEGER,
    extension TEXT,
    indexed_at INTEGER NOT NULL
);
```

Indexes on `folder`, `filename` (case-insensitive COLLATE NOCASE),
`extension`, and `indexed_at` enable fast keyword searches via SQL LIKE
queries. The `is_cache_valid()` method checks both existence and age before
serving cached results.

## Content Search

`ContentSearch` ([@content-search]) searches text within file contents using
a `ThreadPoolExecutor`. It processes files concurrently with configurable
worker count (default: `cpu_count // 2`). Each file is processed by
`ExcelProcessor.search_content()` for Excel files or `PDFProcessor.search_content()`
for PDFs.

The executor supports cancellation via `cancel_event` and proper shutdown
with `cancel_futures=True` (Python 3.9+).

## Natural Language Search

Natural language search ([@ai-services]) converts user queries into structured
search parameters using the LLM. The system:

1. Sends the query to the LLM with a strict JSON-parsing prompt.
2. Extracts specific keywords, excluded keywords, and date ranges.
3. Filters out generic keywords (file, document, data, report, etc.).
4. Runs a standard filename search with the parsed parameters.

The natural-language parsing is implemented in [AI Integration](ai-integration),
and these endpoints are documented in [API Endpoints](../reference/api-endpoints).

## Search History

`SearchHistory` ([@search-history]) persists recent searches in
`.cache/search_history.db`. It deduplicates by keywords + folders, tracks
`search_count`, and trims to `max_history` (default 20) entries. The history
supports CRUD operations: add, get, rerun, delete, and clear.

## Supported File Types

Filename search matches Excel extensions only (`.xlsx`, `.xls`, `.xlsm`) — the
endpoint filters out other types ([@filename-fallback]). Content search and AI
analysis support:
`.pdf`, `.xlsx`, `.xls`, `.xlsm`, `.csv`, `.txt`, `.docx`, `.pptx`, `.json`,
`.md`, `.markdown`, `.mdown`, `.mkd`, `.mkdn`.
