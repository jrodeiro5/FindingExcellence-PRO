# FindingExcellence_PRO v2.0

Privacy-first intelligent file search with local AI (100% local, zero external APIs)

Modern desktop application built with CustomTkinter

## Quick Start

### Start
```bash
start.bat
```

This starts:
- Backend (FastAPI on port 8001)
- Desktop Frontend (CustomTkinter window)

### Stop
```bash
stop.bat
```

## How to Use

1. Click **File Search** tab
2. Enter folder path: `C:\Users\jrodeiro\Desktop`
3. Enter keywords: `report`, `test`, `data`, etc.
4. Click **Search**
5. Watch real-time progress: "Scanning directory 45..." "Found 12 files..."

## Setup (One-Time)

```bash
# Windows Command Prompt only (not PowerShell)
cd FindingExcellence_PRO
uv-setup.bat
```

## Features

✅ **File Search**
- Fast filename matching
- Date filtering
- Real-time progress
- Works on any folder size

✅ **AI Analysis** (requires Ollama)
- Document summarization
- Entity extraction
- OCR from images
- PII detection

✅ **Privacy**
- 100% local processing
- No external APIs
- No cloud services

## Technology

- **Backend**: Python 3.12 + FastAPI
- **Frontend**: CustomTkinter (modern Python desktop)
- **AI**: Local Ollama (100% private)
- **Search**: Pure Python (proven reliable)

## Documentation

See **[docs/README.md](docs/README.md)** for:
- Architecture overview
- Troubleshooting
- Development setup
- API reference
- Performance tips

## Files

- `start.bat` - Start backend + desktop frontend
- `stop.bat` - Stop all services
- `uv-setup.bat` - Initial setup (one-time)
- `docs/` - Full documentation
- `backend/` - FastAPI server (Python)
- `frontend_desktop/` - CustomTkinter desktop app

## Performance

- Small searches (100 files): ~1 second
- Medium searches (1,000 files): ~5 seconds
- Large searches (10,000 files): ~30 seconds
- Shows real-time progress for all searches

## Version

- **v2.0.0** - December 2025
- Python 3.12 + FastAPI backend
- CustomTkinter desktop frontend
- Local Ollama AI (100% private)

---

**Start with**: `start.bat`
