# FindingExcellence PRO 2.0 - Frontend

React + Electron frontend for the intelligent file and content search application.

## Directory Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── SearchPanel.jsx          # File search interface
│   │   ├── ResultsTable.jsx         # Results display with sorting/filtering
│   │   └── AISearchPanel.jsx        # AI analysis and semantic search
│   ├── api/
│   │   └── backendClient.js         # HTTP client for backend API
│   ├── App.jsx                      # Main application component
│   ├── index.jsx                    # React entry point
│   └── index.css                    # Tailwind CSS styles
├── electron/
│   ├── main.js                      # Electron main process
│   └── preload.js                   # Electron security context
├── public/                          # Static assets
├── index.html                       # HTML entry point
├── package.json                     # Dependencies and scripts
├── vite.config.js                   # Vite build configuration
├── tailwind.config.js               # Tailwind CSS configuration
└── postcss.config.js                # PostCSS configuration
```

## Features

- **File Search**: Search by filename with filtering, date ranges, and file types
- **Natural Language Search**: AI-powered semantic search for files
- **Document Analysis**: Summarize, analyze trends, detect anomalies, and extract insights
- **Semantic Search**: Find relevant content within documents
- **Results Management**: Sort, filter, and copy file paths from results

## Technology Stack

- **React 18**: UI framework
- **Electron 27**: Desktop application framework
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client library

## Setup

### Prerequisites
- Node.js 18+ and npm or pnpm
- Python 3.9+ (for backend, must be running)

### Installation

1. Install dependencies:
```bash
npm install
# or
pnpm install
```

2. Create .env file from .env.example:
```bash
cp .env.example .env
```

### Development

Start the development server:
```bash
npm run dev
```

Run Electron in development mode (requires backend running):
```bash
npm run electron
```

Start both frontend dev server and Electron together:
```bash
npm start
```

### Build

Build for production:
```bash
npm run build
```

Build Electron application:
```bash
npm run electron-build
```

## Components

### SearchPanel
Main search interface with two modes:
- **File Search**: Filename-based with advanced filters
- **AI Search**: Natural language queries processed by backend AI

### ResultsTable
Displays search results with:
- Column sorting (click headers to sort)
- Result filtering (search within results)
- Copy-to-clipboard functionality for file paths

### AISearchPanel
Advanced document analysis:
- Summary generation
- Trend analysis
- Anomaly detection
- Key insights extraction
- Semantic search within documents

### App
Main application wrapper handling:
- Tab navigation
- State management
- Backend health checks
- Usage statistics display

## API Communication

All backend communication goes through `src/api/backendClient.js`:

```javascript
// File search
await backendClient.searchByFilename(keywords, folders, options);

// Natural language search
await backendClient.naturalLanguageSearch(query, folders);

// Content search
await backendClient.searchContent(filePaths, keywords, options);

// Document analysis
await backendClient.analyzeDocument(content, analysisType);

// Semantic search
await backendClient.semanticSearch(content, query);

// OCR
await backendClient.ocrImage(imageUrl, extractTables);

// Usage stats
await backendClient.getUsageStats();

// Health check
await backendClient.healthCheck();
```

## Backend Integration

The Electron main process automatically:
1. Spawns the Python FastAPI backend as a subprocess
2. Waits for backend to be ready (2 second delay)
3. Loads the React app (Vite dev server or built files)
4. Terminates the backend when the app closes

Backend must be present at: `../../backend/main.py`

## Troubleshooting

### Backend not connecting
- Ensure Python backend is running on port 8000
- Check that backend process was spawned correctly
- Look at Electron console output for backend errors

### Hot reload not working
- Verify Vite dev server is running on port 5173
- Check browser console for connection errors

### Styling issues
- Tailwind CSS must be properly configured
- Run `npm install` to ensure all dependencies are installed
- Check that postcss.config.js is present

## Build for Distribution

The application can be packaged with electron-builder for distribution:

```bash
npm run build
npm run electron-build
```

This creates standalone executables for Windows, macOS, and Linux.
