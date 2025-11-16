# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FindingExcellence PRO is a desktop application for intelligent file and content search with AI-powered analytics. It combines:
- **Backend**: FastAPI Python server with local Ollama AI (100% privacy)
- **Frontend**: React + Electron desktop application
- **Core Features**: Excel/PDF search, natural language queries, document analysis, OCR with Qwen2.5-VL
- **Privacy**: All AI inference runs locally - zero external API calls

## Development Commands

### Environment Setup
```cmd
# Initial setup (Windows CMD required, not PowerShell)
setup-cmd.bat                    # Recommended: Direct CMD setup
# OR
venv-manage.bat install          # Alternative: Automated setup with Python launcher

# Daily activation
activate.bat                     # Activates venv and shows status
```

### Service Management
```cmd
start-all.bat                    # Start backend (port 8000) + frontend (port 5173)
stop-all.bat                     # Stop all services cleanly
start-simple.bat                 # Background startup (frontend in current window)
```

### Backend Development
```cmd
# Run backend server
activate.bat
python backend\main.py           # Runs on http://localhost:8000

# Run tests
pytest                           # All tests
pytest backend/tests/test_core.py -v              # Core unit tests
pytest backend/tests/test_integration.py -v       # Integration tests
pytest -m unit                   # Only unit tests
pytest -m integration            # Only integration tests
pytest --cov=backend --cov-report=html           # With coverage

# Security audit
venv-manage.bat audit            # Run pip-audit for vulnerabilities
```

### Frontend Development
```cmd
cd frontend
pnpm install                     # Install dependencies
pnpm run dev                     # Development server (port 5173)
pnpm run build                   # Production build
pnpm run build-electron          # Build Electron app
```

### Testing
- Test files: `backend/tests/test_core.py`, `backend/tests/test_integration.py`
- Pytest markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.slow`
- See `backend/tests/README.md` for detailed testing guide

### Ollama Setup (Local AI - 100% Privacy)

**One-time Installation:**
1. Download Ollama from https://ollama.com
2. Run the installer and follow prompts
3. Pull required models (run in Command Prompt):
   ```cmd
   ollama pull llama3.1:8b         # Primary text model (~4.7GB)
   ollama pull qwen2.5-vl:7b       # Vision/OCR model (~4.4GB)
   ollama pull deepseek-r1:1.5b    # Fast fallback model (~1GB)
   ```
4. Verify installation: `ollama list`

**Daily Usage:**
- Ollama runs as a background service after installation
- Accessible at `http://localhost:11434`
- No API keys needed - completely local and private

**Performance:**
- CPU-only: 10-20 tokens/sec (varies by hardware)
- GPU-enabled: 40-100 tokens/sec (requires NVIDIA/AMD GPU)
- OCR: 15-30 sec per image (CPU), 5-10 sec (GPU)

**Troubleshooting:**
- If Ollama not running: Start manually from Windows Start Menu
- If models not found: Check `C:\Users\[USERNAME]\.ollama\models\`
- Backend will gracefully fall back to traditional search if Ollama unavailable

## Architecture

### Backend Structure
```
backend/
├── main.py              # FastAPI app entry point, all API endpoints defined here
├── ai/
│   ├── ollama_client.py        # Local Ollama client (llama3.1:8b, qwen2.5-vl:7b)
│   └── ai_services.py          # High-level AI features (NL search, analysis, OCR)
├── core/
│   ├── file_search.py          # Filename-based search with threading support
│   ├── content_search.py       # Multi-threaded content search in files
│   ├── excel_processor.py      # Excel file reading (pandas, openpyxl)
│   ├── pdf_processor.py        # PDF text extraction (pdfplumber, PyMuPDF)
│   └── config_manager.py       # Configuration persistence
└── utils/
    ├── logging_setup.py        # Centralized logging configuration
    └── export.py               # Data export utilities
```

### Frontend Structure
```
frontend/
├── src/
│   ├── App.jsx                 # Main app component with tab management
│   ├── components/
│   │   ├── SearchPanel.jsx     # File/content search UI
│   │   ├── AISearchPanel.jsx   # Natural language search UI
│   │   └── ResultsTable.jsx    # Search results display
│   └── api/
│       └── backendClient.js    # Backend API client
├── electron/
│   ├── main.js                 # Electron main process
│   └── preload.js              # Preload scripts for security
└── vite.config.js              # Vite bundler configuration
```

### Key Architectural Patterns

1. **AI Integration via Local Ollama (100% Privacy)**
   - Client in `backend/ai/ollama_client.py` with model fallback chains
   - Primary model: `llama3.1:8b` (best reasoning, 105M downloads)
   - Vision model: `qwen2.5-vl:7b` (state-of-the-art OCR, 75% accuracy vs GPT-4o)
   - Fallback models: `deepseek-r1:1.5b` (ultra-fast), `llava:7b` (alternative vision)
   - Latency tracking built-in: `latency_ms`, `total_requests`, `total_tokens`
   - Usage stats endpoint: `GET /api/usage/stats` (shows latency instead of cost)
   - Zero external API calls - all processing on local machine

2. **Search Pipeline**
   - Filename search (`file_search.py`) → Content search (`content_search.py`)
   - Natural language queries → AI parses to structured params → Traditional search
   - Multi-threaded processing with configurable worker pools

3. **FastAPI Endpoints** (all in `main.py`)
   - `POST /api/search/filename` - Filename-based search
   - `POST /api/search/natural-language` - AI-powered natural language search (NL → structured params)
   - `POST /api/search/content` - Content search in Excel/PDF files
   - `POST /api/analyze` - AI document analysis (summary, trends, anomalies, insights)
   - `POST /api/ocr` - OCR text extraction from images (Qwen2.5-VL 7B)
   - `GET /api/usage/stats` - AI usage statistics (latency metrics)
   - `GET /health` - Health check

4. **Threading & Concurrency**
   - `ContentSearch` uses `concurrent.futures.ThreadPoolExecutor`
   - Default workers: `max(1, os.cpu_count() // 2)`
   - `cancel_event` threading for search cancellation
   - Executor cleanup to prevent resource leaks

5. **PDF Processing Strategy**
   - Tries `pdfplumber` first (better for structured content)
   - Falls back to `PyMuPDF` (fitz) for scanned/complex PDFs
   - OCR support via `paddleocr` and `pytesseract` for scanned documents

## Environment Variables

Required in `.env` (never commit):
```env
# Ollama Local AI Configuration (100% privacy - no external API calls)
# Install Ollama from https://ollama.com
# Download models: ollama pull llama3.1:8b && ollama pull qwen2.5-vl:7b
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
OLLAMA_VISION_MODEL=qwen2.5-vl:7b
OLLAMA_TEMPERATURE=0.3
OLLAMA_MAX_TOKENS=2000

# App Configuration
APP_NAME=FindingExcellence_PRO
APP_VERSION=2.0.0

# Search Settings
DEFAULT_SEARCH_FOLDERS=C:\Users\Desktop,C:\Users\Downloads
MAX_WORKERS=4
LOG_LEVEL=INFO
```

## Windows-Specific Considerations

1. **Batch Scripts are Windows CMD only**
   - Do NOT run in PowerShell, Git Bash, or WSL
   - Use Windows Command Prompt exclusively
   - Path separators: Use backslashes (`\`) in batch files

2. **Python Virtual Environment**
   - Located at `venv/` (gitignored)
   - Activated via `venv\Scripts\activate.bat`
   - Managed by `venv-manage.bat` for clean operations

3. **Service Management**
   - `start-all.bat` opens separate CMD windows for each service
   - `stop-all.bat` uses `taskkill` to clean up processes
   - Ports: Backend 8000, Frontend 5173

## Security & Best Practices

1. **Virtual Environment Isolation**
   - All Python deps in isolated `venv/`
   - Regular security audits with `pip-audit` via `venv-manage.bat audit`
   - Never commit `.env` files or `venv/` directory

2. **Complete Data Privacy (Local AI)**
   - No external API calls - all AI processing on local machine
   - File paths and content never leave the device
   - Ollama host configured via `OLLAMA_HOST` environment variable
   - Models downloaded locally (~10GB total for text + vision)

3. **Input Validation**
   - Pydantic models for all API requests
   - File path validation in processors
   - Case-sensitive search optional

## Common Development Workflows

### Adding a New AI Feature
1. Add model/prompt logic to `backend/ai/ai_services.py`
2. Create endpoint in `backend/main.py` with Pydantic request model
3. Update `backendClient.js` in frontend
4. Add UI component in `frontend/src/components/`
5. Wire up in `App.jsx`

### Adding a New File Type Processor
1. Create processor in `backend/core/` (e.g., `word_processor.py`)
2. Define `SUPPORTED_EXTENSIONS` tuple
3. Implement `extract_text()` and `search_content()` methods
4. Update `file_search.py` and `content_search.py` to use new processor
5. Add to `FileSearchRequest.file_types` in `main.py`

### Debugging Search Issues
1. Check logs: `finding_excellence.log` in project root
2. Verify backend running: `http://localhost:8000/health`
3. Test API directly: `http://localhost:8000/docs` (FastAPI auto-docs)
4. Check worker threads: Adjust `MAX_WORKERS` in `.env`

## Build & Deployment

### Backend Packaging
```cmd
# Build with PyInstaller (spec file: backend.spec)
pyinstaller backend.spec

# Output: dist/FindingExcellence_Backend/
```

### Frontend Packaging
```cmd
cd frontend
pnpm run build-electron

# Output: dist/ (NSIS installer + portable exe)
# Config: electron-builder.json
```

### Distribution
- Electron app includes bundled backend executable
- Resources in `resources/` directory (icons, assets)
- Installer options: NSIS (installable) or portable

## API Documentation

When backend is running, visit:
- **Interactive docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative docs**: http://localhost:8000/redoc (ReDoc)

## Dependencies

### Backend (Python 3.8+)
- FastAPI, uvicorn - Web framework
- pandas, openpyxl, xlrd - Excel processing
- pdfplumber, PyMuPDF, camelot - PDF processing
- paddleocr, pytesseract - OCR for scanned PDFs
- openai (for OpenRouter), httpx - AI integration

### Frontend (Node.js 18+)
- React 18, React DOM
- Electron 27 - Desktop wrapper
- Vite 5 - Build tool
- Tailwind CSS - Styling
- axios - HTTP client
- pnpm - Package manager
