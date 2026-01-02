<div align="center">

[![Ayesa Header](.github/Cabecera-Ayesa%20v2.jpg)](https://www.ayesa.com)

</div>

# FindingExcellence PRO v2.0

**Privacy-first intelligent file search with local AI** – 100% local, zero external APIs.

Modern desktop application combining fast file search with local AI analytics powered by Ollama.

<div align="center">

Built by **[Ayesa](https://www.ayesa.com)** – Finding Excellence

![Status](https://img.shields.io/badge/status-stable-brightgreen?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-0000D0?style=flat-square)
![Python](https://img.shields.io/badge/python-3.12%2B-0000D0?style=flat-square)
![Privacy](https://img.shields.io/badge/privacy-100%25%20local-FF3184?style=flat-square)
![Ayesa](https://img.shields.io/badge/by-Ayesa-0000D0?style=flat-square)

</div>

---

---

## Features

✨ **Blazingly Fast File Search**
- Search across 1M+ files in seconds
- SQLite-based caching for instant repeated searches
- Real-time progress updates
- Works offline, no external services

🤖 **Local AI Analysis**
- Document summarization
- Entity extraction
- Optical Character Recognition (OCR)
- PII detection and masking
- 100% private – all processing happens locally via Ollama

🎨 **Modern Desktop Interface**
- CustomTkinter dark theme
- Intuitive tabbed interface
- Sortable results
- Copy paths, open files directly

🔒 **Privacy First**
- No cloud services
- No external API calls
- No data collection or tracking
- Complete control over your files

---

## Quick Start

### Prerequisites

- **Windows 10+** (Windows CMD, not PowerShell)
- **Python 3.12+**
- **Ollama** (for AI features): https://ollama.com

### Installation

```cmd
# Clone the repository
git clone https://github.com/jrodeiro5/FindingExcellence-PRO.git
cd FindingExcellence-PRO

# One-time setup
uv-setup.bat
```

### Run

```cmd
# Start backend + desktop UI
start.bat

# Or in separate terminals:
# Terminal 1:
.venv\Scripts\activate.bat && python backend\main.py

# Terminal 2:
.venv\Scripts\python.exe frontend_desktop\main.py
```

The desktop application opens automatically.

### Stop

```cmd
stop.bat
```

---

## How to Use

### File Search

1. Click **File Search** tab
2. Enter folder path: `C:\Users\YourName\Desktop`
3. Enter keywords: `report`, `test`, `data`, etc.
4. Click **Search**
5. Watch real-time progress and results

### AI Analysis

1. Click **AI Analysis** tab
2. Upload a document (PDF, Excel, Word, image, etc.)
3. Choose analysis type (summarize, extract entities, OCR, etc.)
4. Click **Analyze**
5. View results instantly

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python 3.12 + FastAPI |
| **Frontend** | CustomTkinter (modern Python desktop) |
| **AI Engine** | Local Ollama (100% private) |
| **Search** | Pure Python + SQLite caching |
| **Data Processing** | Pandas + Polars |

---

## Ollama Setup (for AI features)

```cmd
# After installing Ollama from https://ollama.com
ollama pull phi4-mini         # Main model (~2.5GB)
ollama pull deepseek-ocr      # Vision/OCR (~3GB)

# Ollama runs as Windows background service automatically
```

**Total size**: ~5.5GB. All processing is **100% local**.

---

## Project Structure

```
FindingExcellence_PRO/
├── backend/                 # FastAPI server (Python)
│   ├── main.py             # API endpoints
│   ├── ai/                 # AI services (Ollama integration)
│   ├── core/               # File search, handlers, indexing
│   └── tests/              # Unit + integration tests
├── frontend_desktop/        # CustomTkinter UI
│   ├── main.py             # Entry point
│   ├── api_client.py       # HTTP client for backend
│   ├── ui/                 # UI components (search, analysis, results)
│   └── core/               # Local file search
├── docs/                    # Comprehensive documentation
├── start.bat               # Start both services
├── stop.bat                # Stop all services
└── uv-setup.bat            # Initial setup
```

---

## Development

### Commands

```cmd
# Activate environment
.venv\Scripts\activate.bat

# Run tests
pytest                                    # All tests
pytest backend/tests/test_core.py -v     # Single file
pytest -k "test_search"                  # By name

# Lint & format
ruff check backend/                      # Check issues
ruff format backend/                     # Auto-format

# Type checking
basedpyright backend/                    # Type check

# View logs
type finding_excellence.log              # Backend log
type finding_excellence_desktop.log      # Desktop log
```

### Documentation

See [CLAUDE.md](CLAUDE.md) for:
- Architecture overview
- API endpoints
- Threading & UI patterns
- Debugging troubleshooting
- Adding new features
- Performance optimization details

---

## Configuration

Create `.env` file in root directory (optional, has sensible defaults):

```env
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=phi4-mini
OLLAMA_VISION_MODEL=deepseek-ocr
OLLAMA_TEMPERATURE=0.3
OLLAMA_MAX_TOKENS=500

# Application
DEFAULT_SEARCH_FOLDERS=C:\Users\YourName\Desktop,C:\Users\YourName\Downloads
MAX_WORKERS=4
BACKEND_PORT=8000
LOG_LEVEL=INFO
```

Copy `.env.example` for reference.

---

## Performance

Real-world results on 854,567 files:

| Scenario | Time | Status |
|----------|------|--------|
| Initial search (no cache) | 20-24s | ✅ Acceptable |
| Repeated search (cached) | <10ms | ⚡ Instant |
| Cache speedup | 3,945x - 17,087x | 🚀 Extreme |

**Optimizations**:
- Phase 1: `os.scandir()` instead of `os.walk()` (3-5x faster)
- Phase 2: SQLite caching with TTL (100x-17,000x faster for repeated searches)
- Zero overhead: sqlite3 is built-in to Python

See [docs/PERFORMANCE_RESULTS.md](docs/PERFORMANCE_RESULTS.md) for detailed benchmarks.

---

## Optional Features

Install additional features as needed:

```cmd
uv pip install -e .[privacy]      # PII detection/masking (Presidio)
uv pip install -e .[ner]          # Named entity extraction (GliNER)
uv pip install -e .[chunking]     # Semantic chunking (Chonkie)
uv pip install -e .[performance]  # Fast CSV processing (Polars)
uv pip install -e .[all]          # Everything
```

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- How to report bugs
- How to suggest features
- Development workflow
- Code standards

---

## Security

**Questions about security or found a vulnerability?** See [SECURITY.md](SECURITY.md)

**Key highlights**:
- No external API calls – all processing is local
- No credentials stored in code
- No telemetry or analytics
- SQLite cache is local only
- Open source – code is auditable

---

## Troubleshooting

### Backend won't start
```cmd
python --version              # Must be 3.12+
netstat -ano | findstr 8000   # Check port 8000 is free
type finding_excellence.log   # Check logs
```

### Frontend shows "Backend Offline"
- Ensure backend started first: `python backend\main.py`
- Check: http://localhost:8000/health

### Ollama connection issues
```cmd
ollama list                    # Check models installed
ollama serve                   # Start Ollama if needed
```

### UI freezes or doesn't appear
- Check `finding_excellence_desktop.log` for errors
- Ensure CustomTkinter installed: `pip list | findstr customtkinter`
- Run frontend alone: `.venv\Scripts\python.exe frontend_desktop\main.py`

**More help?** Check [CLAUDE.md](CLAUDE.md) debugging section.

---

## License

MIT License – see [LICENSE](LICENSE) file

Built by Ayesa – **Finding Excellence**

---

## Made with ❤️

A privacy-first alternative to cloud-based search and AI services. Keep your data local. Keep it yours.

**Questions?** Open an issue on GitHub.
