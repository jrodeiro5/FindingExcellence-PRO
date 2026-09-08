---
title: Setup and Configuration
topics: [guides]
sources:
  - {id: readme, type: file, path: README.md}
  - {id: claudem, type: file, path: CLAUDE.md}
  - {id: pyproject, type: file, path: pyproject.toml}
  - {id: env-example, type: file, path: .env.example}
  - {id: start-bat, type: file, path: start.bat}
  - {id: stop-bat, type: file, path: stop.bat}
---

# Setup and Configuration

This guide covers installing dependencies, configuring the application, and
running both the backend and desktop frontend.

## Prerequisites

- **Windows 10+** (use Windows CMD, not PowerShell — `.bat` scripts do not
  work in PowerShell/Git Bash).
- **Python 3.12+** (required by `pyproject.toml` ([@pyproject])).
- **Ollama** (for AI features): install from https://ollama.com. The models this
  app uses and how they are managed are covered in [AI Integration](../architecture/ai-integration).

## One-Time Setup

Clone and run the setup script ([@readme]):

```cmd
git clone https://github.com/jrodeiro5/FindingExcellence-PRO.git
cd FindingExcellence-PRO
uv-setup.bat
```

The `uv-setup.bat` script creates a virtual environment and installs core
dependencies from `pyproject.toml` ([@pyproject]). Optional features install
separately:

```cmd
uv pip install -e .[privacy]      # PII detection/masking (Presidio)
uv pip install -e .[ner]          # Entity extraction (GliNER)
uv pip install -e .[chunking]     # Semantic chunking (Chonkie)
uv pip install -e .[performance]  # Fast CSV (Polars)
uv pip install -e .[documents]    # Word/PowerPoint support
uv pip install -e .[all]          # Everything
```

## Ollama Models

For AI features, pull the required models:

```cmd
ollama pull phi4-mini         # Primary model (~2.5 GB, fast CPU)
ollama pull deepseek-ocr      # Vision/OCR (~3 GB, 97% accuracy)
```

The backend selects models from a hardcoded list in `OllamaClient.MODELS`
rather than from `OLLAMA_MODEL`: phi4-mini is the primary general model,
qwen3:4b-instruct is the fallback, and deepseek-ocr handles vision. Only
phi4-mini and deepseek-ocr are warmed on startup, so those two must be pulled.

Total model storage: ~5.5 GB. Ollama runs as a Windows background service
automatically after installation. See CLAUDE.md ([@claudem]) for model
selection rationale. All processing stays on the user's machine, per the
[Local-First Privacy](../decisions/local-first) decision: no data leaves the
computer.

## Configuration

Copy `.env.example` ([@env-example]) to `.env` and customize:

```env
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen3:4b
OLLAMA_VISION_MODEL=deepseek-ocr
OLLAMA_FAST_MODEL=deepseek-r1:1.5b
OLLAMA_TEMPERATURE=0.3
OLLAMA_MAX_TOKENS=2000
OLLAMA_CONTEXT_SIZE=2048
OLLAMA_TIMEOUT=120
OLLAMA_KEEP_ALIVE=-1

DEFAULT_SEARCH_FOLDERS=C:\Users\YourName\Desktop,C:\Users\YourName\Downloads
MAX_WORKERS=4
BACKEND_PORT=8000
LOG_LEVEL=INFO
LOG_FILE=finding_excellence.log
```

Key variables:

- `OLLAMA_KEEP_ALIVE` — `-1` keeps model loaded forever, `0` unloads
  immediately, `"5m"` keeps for 5 minutes.
- `OLLAMA_CONTEXT_SIZE` — context window size sent to Ollama (code default
  `512`; `.env.example` sets `2048`).
- `OLLAMA_MAX_TOKENS` — max completion tokens (code default `256`;
  `.env.example` sets `2000`).
- `OLLAMA_TIMEOUT` — per-request timeout in seconds (`120`).
- `BACKEND_PORT` — FastAPI listens here. Default: `8000`.
- `DEFAULT_SEARCH_FOLDERS` — comma-separated list of default search
  directories.

Never commit `.env` — it contains local paths and is machine-specific.

## Running the Application

### Start Both Services

Run `start.bat` ([@start-bat]) to launch the backend and desktop frontend:

```cmd
start.bat
```

This starts the backend on port 8000 and then launches the desktop UI.

### Run Separately

```cmd
# Terminal 1 — Backend
.venv\Scripts\activate.bat
python backend\main.py

# Terminal 2 — Desktop frontend
.venv\Scripts\python.exe frontend_desktop\main.py
```

The frontend checks backend health on startup. If the backend is offline,
the frontend still works for local file search (no API needed).

### Stop

Run `stop.bat` ([@stop-bat]) to terminate all running services:

```cmd
stop.bat
```

## Verification

- Backend API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health
- Backend log: `finding_excellence.log`
- Desktop log: `finding_excellence_desktop.log`

## Troubleshooting

**Backend won't start:**

```cmd
python --version              # Must be 3.12+
netstat -ano | findstr 8000   # Check port 8000 is free
type finding_excellence.log   # Check logs
```

**Frontend shows "Backend Offline":**

- Ensure backend started first.
- Check http://localhost:8000/health.
- Verify `BACKEND_PORT=8000` in `.env`.

**Ollama connection issues:**

```cmd
ollama list                    # Check models installed
ollama serve                   # Start Ollama if not running as service
```

**UI freezes or doesn't appear:**

- Check `finding_excellence_desktop.log` for errors.
- Ensure CustomTkinter is installed: `pip list | findstr customtkinter`.
- Run frontend alone: `.venv\Scripts\python.exe frontend_desktop\main.py`.
