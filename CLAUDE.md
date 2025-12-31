# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FindingExcellence PRO v2.0 is a privacy-first desktop application for intelligent file search with local AI analytics. All AI runs locally via Ollama—zero external APIs or cloud services.

- **Backend**: FastAPI (Python 3.12) on port 8000
- **Frontend**: CustomTkinter desktop UI (dark theme)
- **AI Models**: phi4-mini (general, primary), qwen3:4b-instruct (fallback), deepseek-ocr (vision) via Ollama

## Quick Start

```cmd
# One-time setup
uv-setup.bat

# Daily development (two terminals)
.venv\Scripts\activate.bat && python backend\main.py     # Terminal 1 - Backend
.venv\Scripts\python.exe frontend_desktop\main.py        # Terminal 2 - Desktop

# Or use convenience scripts
start.bat      # Start both backend + desktop frontend
stop.bat       # Stop all services
```

**Access Points:**
- Desktop UI: CustomTkinter window (launches automatically)
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Development Commands

```cmd
# Activate environment first
.venv\Scripts\activate.bat

# Run tests
pytest                                    # All tests
pytest backend/tests/test_core.py -v     # Single test file
pytest -k "test_file_search"             # Single test by name
pytest -m unit                           # Only unit tests
pytest -m integration                    # Only integration tests
pytest --cov=backend --cov-report=html   # With coverage report

# Lint & format
ruff check backend/                       # Check for issues
ruff check backend/ --fix                # Auto-fix issues
ruff format backend/                     # Format code

# Type checking
basedpyright backend/                    # Type check

# View logs
type finding_excellence.log              # Backend log
type finding_excellence_desktop.log      # Desktop log
```

## Architecture

### Backend Structure

**Entry Point:** `backend/main.py` - FastAPI with all endpoints defined

**Request Flow:**
```
Desktop UI → api_client.py → HTTP → FastAPI (main.py) → Services
```

**AI Services** (`backend/ai/`):
- `ollama_client.py` - Ollama integration (model management, warmup, fallback chains)
- `ai_services.py` - High-level AI features (text analysis, OCR, search)
- `data_analyzer.py` - Hybrid analysis (stats + LLM interpretation)
- Optional: `pii_service.py` (PII detection), `ner_service.py` (entities), `chunking_service.py` (semantic chunks)

**File Handlers** (`backend/core/`):
- `file_search.py` - Multi-threaded filename search with cancellation support
- `content_search.py` - Content search orchestrator
- `csv_handler.py`, `excel_handler.py`, `pdf_processor.py`, `text_handler.py` - Format-specific handlers
- `polars_handler.py` - Fast CSV processing for large files (>50MB)
- `search_progress.py` - Async search progress tracking

**Key Architectural Patterns:**

1. **Graceful Degradation:**
   - Every optional service has `is_available()` method
   - Application runs without AI if Ollama unavailable
   - Missing dependencies don't crash the app

2. **Hybrid Analysis for Tabular Data:**
   - Extract statistics with Polars/Pandas (fast, accurate)
   - Send condensed summary to LLM for interpretation
   - Much faster than sending raw data to LLM

3. **Async Search with Progress Polling:**
   - Client POSTs to `/api/search/filename` → returns `search_id` immediately
   - Backend starts search in background thread
   - Client polls `/api/search/progress/{search_id}` for updates
   - Client retrieves results from `/api/search/results/{search_id}` when complete

4. **Model Warmup Pattern:**
   - Models preloaded in background thread on startup
   - Eliminates cold-start delay for first request
   - Configurable with `OLLAMA_KEEP_ALIVE` environment variable

5. **File Handler Interface:**
   - All handlers return `(content, error)` tuples
   - Encoding fallback: UTF-8 → Latin-1 → CP1252 → ISO-8859-1
   - Supports cancellation via `threading.Event`

### Frontend Desktop Structure

**Entry Point:** `frontend_desktop/main.py` → `ui/main_window.py` (ExcelFinderApp)

**UI Components:**
```
ExcelFinderApp (main window)
├── SearchPanel (File Search tab)
│   ├── Keyword entry
│   ├── Date range filters
│   ├── Folder selection
│   └── Search/Cancel buttons
├── AnalysisPanel (AI Analysis tab)
│   ├── File upload
│   ├── Progress indicator
│   └── Analyze button
└── ResultsPanel (shared)
    └── Results display
```

**Key Patterns:**

1. **UI Threading (Thread-Safe):**
   - Main thread: UI rendering only
   - Background threads: File search, AI analysis
   - Thread safety: All UI updates via `self.after(0, callback)`
   - Never block main thread

2. **Direct File Search (No API):**
   - `core/file_search.py` runs directly in frontend
   - No HTTP overhead, works without backend
   - Supports cancellation and real-time progress

3. **Component Communication:**
   - Callback-based architecture
   - Parent passes callbacks to child components
   - Child components call parent methods for actions

4. **Health Polling:**
   - Frontend checks backend health on startup
   - Gracefully handles backend offline scenario

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/search/filename` | Async file search (returns search_id) |
| POST | `/api/search/progress/{id}` | Poll search progress |
| POST | `/api/search/results/{id}` | Get completed search results |
| POST | `/api/search/content` | Search file contents |
| POST | `/api/analyze` | Upload & analyze document |
| POST | `/api/pii/mask` | Mask PII (optional) |
| POST | `/api/pii/detect` | Detect PII (optional) |
| POST | `/api/entities/extract` | Extract entities (optional) |
| POST | `/api/ocr` | OCR from images |
| GET | `/api/health` | Health check + service status |
| GET | `/api/usage/stats` | Usage statistics |

## Optional Features

Install after setup as needed:

```cmd
uv pip install -e .[privacy]      # PII masking (Presidio)
uv pip install -e .[ner]          # Entity extraction (GliNER)
uv pip install -e .[chunking]     # Semantic chunking (Chonkie)
uv pip install -e .[performance]  # Fast CSV (Polars)
uv pip install -e .[all]          # Everything
```

## Environment Variables

Create `.env` file (never commit):

```env
# Ollama Configuration (100% privacy - no external APIs)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=phi4-mini                    # Primary model (fast CPU inference)
OLLAMA_VISION_MODEL=deepseek-ocr
OLLAMA_TEMPERATURE=0.3
OLLAMA_MAX_TOKENS=500
OLLAMA_CONTEXT_SIZE=1024
OLLAMA_KEEP_ALIVE=-1                      # -1: Keep loaded forever, 0: unload immediately, "5m": 5 minutes

# Application Settings
DEFAULT_SEARCH_FOLDERS=C:\Users\jrodeiro\Desktop,C:\Users\jrodeiro\Downloads
MAX_WORKERS=4
BACKEND_PORT=8000
LOG_LEVEL=INFO
```

## Ollama Setup

```cmd
# After installing Ollama from https://ollama.com
ollama pull phi4-mini         # Primary model (~2.5GB, fast CPU inference)
ollama pull deepseek-ocr      # Vision/OCR (~3GB, 97% accuracy)

# Total: ~5.5GB
```

Ollama runs as Windows background service. Backend gracefully degrades if unavailable.

## Adding New Features

### New File Type Processor

**1. Create handler** (`backend/core/new_handler.py`):
```python
class NewHandler:
    SUPPORTED_EXTENSIONS = ('.newext',)

    @staticmethod
    def read_new_format(file_path: str) -> tuple[str, str | None]:
        """Extract text from new format.

        Returns:
            (content, error) - content is str, error is None on success
        """
        try:
            # Extract text logic here
            content = extract_text(file_path)
            return content, None
        except Exception as e:
            return "", str(e)
```

**2. Register in** `backend/main.py` (in `/api/analyze` endpoint):
```python
file_ext = Path(file.filename).suffix.lower()

if file_ext == '.newext':
    extracted_text, error = NewHandler.read_new_format(str(temp_path))
    if error:
        raise HTTPException(status_code=400, detail=f"Error: {error}")
```

**3. Add test** in `backend/tests/test_core.py`

### New API Endpoint

**1. Add endpoint in** `backend/main.py`:
```python
class MyRequest(BaseModel):
    data: str

@app.post("/api/my-feature")
async def my_feature(request: MyRequest):
    try:
        result = do_something(request.data)
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

**2. Add client method in** `frontend_desktop/api_client.py`:
```python
def my_feature(self, data: str) -> Dict[str, Any]:
    """Call my feature endpoint."""
    try:
        response = self.session.post(
            urljoin(self.host, "/api/my-feature"),
            json={"data": data},
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"API call failed: {e}")
        return {"success": False, "error": str(e)}
```

**3. Call from UI component** (e.g., `frontend_desktop/ui/my_panel.py`):
```python
def _on_button_click(self):
    # Run in background thread to avoid blocking UI
    self.my_thread = threading.Thread(
        target=self._run_my_feature,
        daemon=True
    )
    self.my_thread.start()

def _run_my_feature(self):
    result = self.app.api_client.my_feature("input_data")
    self.after(0, lambda: self._display_result(result))

def _display_result(self, result):
    """Update UI with result (runs on main thread)"""
    if result.get("success"):
        self.result_label.configure(text=result["result"])
```

### New Desktop Tab

**1. Create panel** (`frontend_desktop/ui/my_panel.py`):
```python
import customtkinter as ctk
from typing import Callable

class MyPanel(ctk.CTkFrame):
    def __init__(self, parent, on_action_callback: Callable, on_status_callback: Callable):
        super().__init__(parent)
        self.on_action = on_action_callback
        self.on_status = on_status_callback
        self._build_ui()

    def _build_ui(self):
        # Create widgets
        button = ctk.CTkButton(self, text="Action", command=self._on_button_click)
        button.pack(padx=10, pady=10)

    def _on_button_click(self):
        self.on_action()  # Call parent callback
        self.on_status("Processing...")  # Update status
```

**2. Add tab in** `frontend_desktop/ui/main_window.py`:
```python
# In _build_ui() method
my_tab = self.tabview.add("My Tab")
self.my_panel = MyPanel(
    my_tab,
    on_action_callback=self._on_my_action,
    on_status_callback=self._update_status
)
self.my_panel.pack(fill="both", expand=True)

# Add callback in main window
def _on_my_action(self):
    # Start background work
    self.my_thread = threading.Thread(target=self._run_my_work, daemon=True)
    self.my_thread.start()

def _run_my_work(self):
    # Background work here
    result = do_work()
    self.after(0, lambda: self._on_my_work_complete(result))

def _on_my_work_complete(self, result):
    self.results_panel.display_results(result)
```

## Important Notes

- **Windows CMD only** - .bat scripts don't work in PowerShell/Git Bash
- **Backend must run first** - Frontend checks health on startup
- **Port 8000** - Backend runs on 8000 (not 8001)
- **Python 3.12 minimum** - Required for all dependencies
- **All local** - No external API keys or cloud services needed
- **Models**: phi4-mini is primary (faster), qwen3:4b-instruct is fallback
- **Model warmup**: First request to backend triggers model warmup (~30s), subsequent requests are fast
