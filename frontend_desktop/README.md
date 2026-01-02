# FindingExcellence PRO v2.0 - Desktop Frontend

Modern desktop application built with **CustomTkinter** (Python Tkinter wrapper).

## Quick Start

### Option 1: Using start-all.bat (Recommended)
```batch
cd C:\Users\jrodeiro\Desktop\FindingExcellence_PRO
start-all.bat
# Then select option 1 for Desktop
```

### Option 2: Manual Start

**Terminal 1 - Backend:**
```cmd
.venv\Scripts\activate.bat
python backend\main.py
```

**Terminal 2 - Desktop Frontend:**
```cmd
.venv\Scripts\python.exe frontend_desktop\main.py
```

## Architecture

### Components

**`main_window.py`** - Main application window
- Tab interface (File Search, AI Analysis)
- Progress bar for long operations
- Status bar with connection indicator
- Threading for background operations
- Polling logic for real-time progress

**`search_panel.py`** - File search tab
- Keyword input with Enter key support
- Folder selection (Browse, Clear All)
- Case sensitive checkbox
- Real-time status updates

**`analysis_panel.py`** - AI document analysis tab
- File picker (PDF, CSV, XLSX)
- Upload button with file validation
- Analysis button (disabled until file selected)
- Results display

**`results_panel.py`** - Shared results display
- File search results (filename, path, modified date)
- Analysis results (text output)
- Scrollable text area
- File count display

**`../api_client.py`** - Backend HTTP client
- Health check
- Async file search
- Search progress polling
- File upload and analysis
- Analysis progress polling
- Proper error handling

## Features

### File Search
1. Enter keywords
2. Select folders to search
3. Click "Search"
4. Real-time progress display
5. Results shown with file paths and dates
6. Click any result to copy path

### AI Document Analysis
1. Select PDF, CSV, or Excel file
2. Click "Analyze"
3. Real-time progress (elapsed time)
4. Results displayed in text area
5. Can copy/save results

### Backend Integration
- **Async Search**: Returns immediately with search_id, polls progress
- **Real-time Progress**: Every 1 second, displays current directory and file count
- **Polling**: Handles long operations (10+ minute timeout per operation)
- **Error Handling**: User-friendly error messages
- **Connection Status**: Header shows "✅ Backend Connected" or "❌ Backend Offline"

## Styling

- **Dark Mode**: By default (customtkinter dark theme)
- **Colors**:
  - Active: Blue
  - Success: #52CC52 (green)
  - Warning: #FFB347 (orange)
  - Error: #FF6B6B (red)
- **Fonts**: Arial for UI, Courier for results

## Dependencies

```
customtkinter==5.2.2     # Modern Tkinter wrapper with dark mode
requests==2.31.0          # HTTP client for backend communication
Pillow==10.0.0            # Image support
python-dotenv==1.0.0      # Environment variable loading
```

Install with:
```cmd
pip install -r requirements.txt
```

## Configuration

**.env file** (in project root):
```env
DEFAULT_SEARCH_FOLDERS=C:\Users\jrodeiro\Desktop,C:\Users\jrodeiro\Downloads
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=deepseek-r1:1.5b
OLLAMA_VISION_MODEL=qwen2.5-vl:7b
```

## Troubleshooting

### "Backend Offline"
- Ensure backend is running on port 8001
- Check: `python backend\main.py`
- Verify `.env` file exists with correct configuration

### File Search Returning 0 Results
- Verify DEFAULT_SEARCH_FOLDERS in `.env`
- Check folder permissions
- Try smaller folder (Desktop instead of entire drive)

### Analysis Takes Too Long
- Large files (100+ MB) may take several minutes
- Ollama inference is CPU-heavy (10-30 sec per document)
- Check backend logs: `finding_excellence.log`

### Application Crashes
- Check log file: `finding_excellence_desktop.log`
- Ensure dependencies installed: `pip install -r requirements.txt`
- Try restarting backend

## Logs

- **Desktop App Log**: `finding_excellence_desktop.log` (root directory)
- **Backend Log**: `finding_excellence.log` (root directory)

## Development

### Adding New Features

1. **New Tab**:
   - Create new component in `ui/` (e.g., `my_panel.py`)
   - Add to tabview in `main_window.py`
   - Add callback method for user actions

2. **New API Endpoint**:
   - Add method to `api_client.py`
   - Call from component callback
   - Implement polling if async operation

3. **UI Styling**:
   - Modify colors in component `__init__`
   - Use customtkinter widgets
   - Follow existing color scheme

### File Structure
```
frontend_desktop/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── api_client.py          # Backend HTTP client
├── ui/
│   ├── __init__.py
│   ├── main_window.py     # Main app window + tabs
│   ├── search_panel.py    # File search tab
│   ├── analysis_panel.py  # AI analysis tab
│   └── results_panel.py   # Results display
└── README.md              # This file
```

## Performance

**Memory Usage**:
- Idle: ~50-100 MB
- During search: +10-20 MB
- During analysis: +20-50 MB (depends on file size)

**Startup Time**:
- App launch: 2-3 seconds
- Backend connection check: 1 second
- Total time to interactive: ~4 seconds

**Search Performance**:
- Desktop folder (50 files): 1-2 seconds
- Large folder tree (1000+ files): 10-30 seconds
- Very large (10000+ files): 1-3 minutes

**Analysis Performance**:
- Small file (PDF < 5MB): 10-30 seconds
- Medium file (CSV < 50MB): 30-60 seconds
- Large file (100+ MB): 2-5 minutes

## Deployment

To create standalone executable:
```cmd
.venv\Scripts\pip install pyinstaller
.venv\Scripts\pyinstaller --onefile --windowed --name "FindingExcellence_PRO_Desktop" frontend_desktop\main.py
```

Output: `dist/FindingExcellence_PRO_Desktop.exe` (~20 MB)

## Comparison: Desktop vs Web

| Feature | Desktop | Web |
|---------|---------|-----|
| **Framework** | CustomTkinter | React/Vite |
| **Size** | 15-20 MB | 150-200 MB |
| **Memory Idle** | 50-100 MB | 300+ MB |
| **Dev Speed** | 3-5 days | 2-3 days (mature) |
| **Maintenance** | Simple Python | Complex JS ecosystem |
| **Real-time Progress** | Threading + UI | Polling + State |
| **Desktop Feel** | Native | Browser-based |
| **Installation** | pip + Python 3.12 | npm + Node.js |

## Notes

- All AI inference runs locally via Ollama (100% private)
- No external API calls or cloud dependencies
- Pure Python implementation (no Electron complexity)
- Modular architecture allows easy feature additions
- Uses same backend as web version (FastAPI)
