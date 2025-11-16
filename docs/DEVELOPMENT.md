# Development Guide

## Prerequisites

- Python 3.9+
- Node.js 18+
- Git
- Code editor (VS Code recommended)

## Project Setup

### 1. Clone and Install

```bash
git clone <repo-url>
cd FindingExcellence_PRO
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend
npm install
cd ..
```

### 4. Environment Configuration

```bash
# Backend
cp backend/.env.example backend/.env
# Edit backend/.env and add OPENROUTER_API_KEY

# Frontend
cp frontend/.env.example frontend/.env
```

## Running in Development

### Terminal 1: Start Backend

```bash
python backend/main.py
```

Backend will run on http://localhost:8000

### Terminal 2: Start Frontend Dev Server

```bash
cd frontend
npm run dev
```

Frontend dev server will run on http://localhost:5173

### Terminal 3: Start Electron (Optional)

```bash
cd frontend
npm run electron
```

## Project Structure

### Backend Modules

- **core/** - Core search functionality
  - file_search.py - Filename-based search
  - content_search.py - File content search
  - excel_processor.py - Excel file handling
  - pdf_processor.py - PDF text extraction
  - config_manager.py - Configuration management

- **ai/** - AI integration
  - openrouter_client.py - OpenRouter API client
  - ai_services.py - High-level AI features

- **utils/** - Utilities
  - export.py - Data export functionality
  - logging_setup.py - Logging configuration

- **main.py** - FastAPI application

### Frontend Components

- **SearchPanel.jsx** - File search interface
- **ResultsTable.jsx** - Results display with sorting
- **AISearchPanel.jsx** - AI analysis and semantic search
- **App.jsx** - Main application layout
- **api/backendClient.js** - Backend HTTP client

### Tests

- **tests/test_core.py** - Unit tests for core modules
- **tests/test_integration.py** - API integration tests
- **tests/conftest.py** - Pytest configuration

## Adding New Features

### Backend Feature

1. Create new module in appropriate subdirectory
2. Implement functionality
3. Add unit tests in tests/
4. Add API endpoint in main.py if needed
5. Update documentation

### Frontend Component

1. Create new .jsx file in src/components/
2. Implement React component
3. Add to App.jsx or relevant parent
4. Style with Tailwind CSS classes
5. Test with dev server

## Testing

### Run Backend Tests

```bash
pytest backend/tests/ -v
pytest backend/tests/ --cov=backend
```

### Run Frontend Tests

```bash
cd frontend
npm run test
```

## Code Style

### Python

- Follow PEP 8 guidelines
- Use type hints
- Docstrings for functions
- Black formatting (optional)

### JavaScript/React

- Use ES6+ syntax
- Functional components preferred
- PropTypes or TypeScript for props
- ESLint for linting

## Debugging

### Backend

View logs:
```bash
python backend/main.py  # Shows console output
```

Check API docs:
```
http://localhost:8000/docs
```

### Frontend

Open DevTools in browser:
- F12 or Ctrl+Shift+I
- Check Console for errors
- Use React DevTools extension

## Common Tasks

### Adding a New Search Filter

1. Update SearchPanel.jsx state
2. Add UI element for filter
3. Pass to backendClient method
4. Update backend endpoint to accept parameter
5. Test with sample data

### Adding AI Analysis Type

1. Add case in AISearchPanel.jsx
2. Update backend ai_services.py
3. Add API endpoint or modify existing
4. Test with sample document

### Adding Export Format

1. Create new export function in backend/utils/export.py
2. Add API endpoint in main.py
3. Add UI button in frontend
4. Test with sample results

## Building for Distribution

See build.ps1 or build.sh scripts

## Deployment

See DEPLOYMENT.md for detailed instructions

## Environment Variables

### Backend (.env)

```
OPENROUTER_API_KEY=your-key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
COST_LIMIT_MONTHLY=10.00
LOG_LEVEL=INFO
DEFAULT_MODEL=deepseek/deepseek-chat-v3.1
VISION_MODEL=google/gemini-2.0-flash-exp:free
```

### Frontend (.env)

```
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
VITE_APP_TITLE=FindingExcellence PRO 2.0
```

## Useful Commands

```bash
# Backend
python backend/main.py              # Run server
pytest backend/tests/              # Run tests
pip list                           # Check dependencies

# Frontend
npm run dev                        # Dev server
npm run build                      # Production build
npm run electron                   # Run Electron
npm run electron-build             # Package app

# General
git status                         # Check changes
git add .                          # Stage changes
git commit -m 'message'            # Commit changes
git push                           # Push to remote
```

## Getting Help

1. Check README files in each module
2. Review API documentation at http://localhost:8000/docs
3. Check test files for usage examples
4. Review git history for similar changes
