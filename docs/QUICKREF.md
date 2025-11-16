# FindingExcellence PRO 2.0 - Quick Reference

## Project Structure

```
FindingExcellence_PRO/
├── backend/              # Python FastAPI server
│   ├── core/            # Search modules
│   ├── ai/              # AI integration
│   ├── utils/           # Utilities
│   ├── tests/           # Unit + integration tests
│   ├── main.py          # FastAPI app
│   └── requirements.txt
├── frontend/            # React + Electron app
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── api/         # HTTP client
│   │   └── index.css    # Styles
│   ├── electron/        # Electron main process
│   ├── index.html
│   └── package.json
├── README.md            # Main documentation
├── DEVELOPMENT.md       # Dev guide
├── DEPLOYMENT.md        # Build guide
├── build.ps1            # Windows build script
└── build.sh             # Linux/macOS build script
```

## Essential Commands

### Backend
```bash
# Install
pip install -r backend/requirements.txt

# Run
python backend/main.py

# Test
pytest backend/tests/ -v

# View API docs
# http://localhost:8000/docs
```

### Frontend
```bash
cd frontend

# Install
npm install

# Dev server
npm run dev

# Build
npm run build

# Electron
npm run electron

# Package
npm run electron-build
```

## Key Files

### Backend Entry Points
- main.py - FastAPI application
- openrouter_client.py - AI client
- ai_services.py - AI features

### Frontend Entry Points
- App.jsx - Main component
- index.jsx - React entry
- electron/main.js - Electron process

### Configuration
- backend/.env - Backend config
- frontend/.env - Frontend config

## API Endpoints

- GET /health - Health check
- POST /api/search/filename - File search
- POST /api/search/natural-language - AI search
- POST /api/search/content - Content search
- POST /api/analyze - Document analysis
- POST /api/ocr - Image OCR
- GET /api/usage/stats - Usage stats

API Documentation: http://localhost:8000/docs

## Environment Setup

### Backend .env
```
OPENROUTER_API_KEY=your-key
COST_LIMIT_MONTHLY=10.00
LOG_LEVEL=INFO
```

### Frontend .env
```
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
```

## Development Workflow

1. Start backend: `python backend/main.py`
2. Start frontend: `cd frontend && npm run dev`
3. Open browser: `http://localhost:5173`
4. Make changes - hot reload enabled
5. Run tests: `pytest backend/tests/`
6. Test Electron: `npm run electron`

## Building for Release

### Windows
```powershell
.\build.ps1
```

### Linux/macOS
```bash
./build.sh
```

Outputs to dist/ directory

## Testing

### Unit Tests
```bash
pytest backend/tests/test_core.py -v
```

### Integration Tests
```bash
pytest backend/tests/test_integration.py -v
```

### With Coverage
```bash
pytest backend/tests/ --cov=backend --cov-report=html
```

## Troubleshooting

### Backend won't start
- Check Python 3.9+ installed
- Run: `pip install -r backend/requirements.txt`
- Check port 8000 is available

### Frontend not connecting
- Ensure backend running on :8000
- Check browser console for errors
- Verify .env file configured

### Tests failing
- Check .env files exist
- Ensure all dependencies installed
- Run `pytest backend/tests/ -v` for details

## Performance Tips

- Use specific search folders when possible
- Filter by file type to reduce scope
- Disable OCR if not needed
- Close other applications for faster analysis

## Cost Optimization

Monthly budget default: $10
Free models: DeepSeek R1, Gemini 2.0 Flash
Paid model: DeepSeek V3.1 ($0.20/$0.80 per 1M tokens)

## Version

Current: 2.0.0
Python: 3.9+
Node: 18+

## Documentation

See detailed guides:
- README.md - Overview
- DEVELOPMENT.md - Development
- DEPLOYMENT.md - Deployment
- PROJECT_SUMMARY.md - Project details
