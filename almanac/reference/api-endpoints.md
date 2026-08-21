---
title: API Endpoints
topics: [reference]
sources:
  - {id: main-py, type: file, path: backend/main.py}
  - {id: api-client, type: file, path: frontend_desktop/api_client.py}
---

# API Endpoints

All endpoints are under the `/api/` prefix. The backend runs on
`127.0.0.1:8000` by default. Interactive API docs are available at
`http://localhost:8000/docs`.

The backend defines all endpoints in `backend/main.py` ([@main-py]) using
FastAPI route decorators. The desktop frontend communicates through
`frontend_desktop/api_client.py` ([@api-client]), which wraps `requests` with
timeout handling and user-friendly error mapping.

## Health

```
GET /health
```

Returns `{"status": "healthy", "version": "2.0.0"}`. Used by the desktop
frontend to verify the backend is reachable.

```
GET /
```

Returns `{"app": "FindingExcellence_PRO", "version": "2.0.0", "ai_enabled":
<bool>}`.

## Filename Search

```
POST /api/search/filename
```

**Request body** (`FileSearchRequest`):

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `keywords` | `List[str]` | Yes | — |
| `folders` | `List[str]` | Yes | — |
| `exclude_keywords` | `List[str]` | No | `[]` |
| `start_date` | `str` (YYYY-MM-DD) | No | `null` |
| `end_date` | `str` (YYYY-MM-DD) | No | `null` |
| `file_types` | `List[str]` | No | `[.xlsx, .xls, .xlsm, .pdf]` |

**Response:**

```json
{
  "success": true,
  "count": 42,
  "results": [
    {"filename": "report.xlsx", "path": "C:\\...\\report.xlsx",
     "modified": "2025-08-15 14:30:00", "type": "xlsx"}
  ]
}
```

Returns 500 on search failure.

## Natural Language Search

```
POST /api/search/natural-language
```

**Request body** (`NaturalLanguageSearchRequest`):

| Field | Type | Required |
|-------|------|----------|
| `query` | `str` | Yes |
| `folders` | `List[str]` | Yes |

Returns the parsed search parameters, AI cost, and filename search results.
Returns 503 when AI service is unavailable.

## Content Search

```
POST /api/search/content
```

**Request body** (`ContentSearchRequest`):

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `file_paths` | `List[str]` | Yes | — |
| `keywords` | `List[str]` | Yes | — |
| `case_sensitive` | `bool` | No | `false` |
| `search_type` | `str` | No | `"excel"` |

Returns file paths mapped to their search results.

## Search History

```
GET  /api/search/history?limit=20
POST /api/search/history
POST /api/search/history/{search_id}    # rerun
DELETE /api/search/history/{search_id}
```

History is stored in `.cache/search_history.db`. Maximum 20 entries. Each
entry tracks keywords, folders, date range, case sensitivity, extensions,
search count, and timestamps.

## Document Analysis

```
POST /api/analyze
```

Uploads a file and returns AI analysis. Supported types: PDF, XLSX, XLS,
XLSM, CSV, TXT, DOCX, PPTX, JSON, MD.

For tabular data (CSV, Excel), the backend uses a hybrid approach:
statistics are extracted with Polars/Pandas, then sent to the LLM for
interpretation.

**Request:** `multipart/form-data` with `file` (UploadFile) and
`analysis_type` (summary, key_points, anomalies, insights, trends).

**Response:**

```json
{
  "success": true,
  "filename": "report.pdf",
  "file_type": ".pdf",
  "extracted_chars": 15234,
  "analysis": "Document provides..."
}
```

Returns 400 for unsupported types or empty extractions. Returns 503 when
AI is unavailable.

### Batch Analysis

```
POST /api/analyze/batch
```

Analyzes 2-100 files in a single request. Returns individual analyses plus
a consolidated summary. Temp files are cleaned up in a `finally` block.

## OCR

```
POST /api/ocr
```

**Request body** (`OCRRequest`):

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `image_url` | `str` | Yes | — |
| `extract_tables` | `bool` | No | `false` |

Uses the vision model (`deepseek-ocr`) to extract text or structured tables
from images. Image URLs are converted to base64 internally.

## Usage Statistics

```
GET /api/usage/stats
```

Returns total requests, tokens, latency, and warmed models. Cost is always
$0.00 for local inference.

## Error Handling

The backend returns `HTTPException` with status codes:

| Code | Meaning |
|------|---------|
| 400 | Bad request (unsupported type, empty extraction) |
| 403 | Forbidden |
| 409 | Conflict |
| 422 | Validation error |
| 500 | Internal server error |
| 503 | Service unavailable (AI not running) |

Error responses include a `detail` field with a human-readable message.
The frontend client ([@api-client]) maps `error_code` fields from the
backend to user-friendly messages.
