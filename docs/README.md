# FindingExcellence PRO 2.0

Intelligent file and content search with AI-powered analytics. A modern desktop application combining Electron frontend, FastAPI backend, and OpenRouter AI integration.

## Quick Start

### From Source

1. Clone repository
2. Install backend dependencies: pip install -r backend/requirements.txt
3. Install frontend dependencies: cd frontend && npm install
4. Set up .env files with OpenRouter API key
5. Start backend: python backend/main.py
6. Start frontend: cd frontend && npm run dev

### Features

- Filename search with advanced filtering
- AI-powered natural language search
- Document analysis and insights
- PDF text extraction and OCR
- Excel and CSV processing
- Cost-effective OpenRouter integration (95-99% savings)

## Technology

- Frontend: React 18, Electron, Vite, Tailwind CSS
- Backend: FastAPI, Python 3.9+, OpenRouter AI
- Testing: pytest with unit and integration tests
- Packaging: PyInstaller (backend), electron-builder (frontend)

## Directory Structure

- backend/ - FastAPI server with AI integration
- frontend/ - React + Electron desktop app
- backend/tests/ - Unit and integration tests
- DEPLOYMENT.md - Build and deployment guide

## For Detailed Information

See individual README files:
- backend/README.md - Backend documentation
- frontend/README.md - Frontend documentation
- backend/tests/README.md - Testing guide
- DEPLOYMENT.md - Build and packaging

## API Documentation

Run backend and visit http://localhost:8000/docs

## Version

Current: 2.0.0
