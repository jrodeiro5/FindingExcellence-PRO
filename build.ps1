# Build and packaging script for FindingExcellence PRO

$ErrorActionPreference = 'Stop'

Write-Host 'FindingExcellence PRO - Build & Package Script' -ForegroundColor Cyan
Write-Host '=' * 50

# Configuration
$BACKEND_DIR = 'backend'
$FRONTEND_DIR = 'frontend'
$DIST_DIR = 'dist'
$BUILD_DIR = 'build'

# Phase 1: Backend Build with PyInstaller
Write-Host 'Phase 1: Building Python Backend...' -ForegroundColor Yellow

if (-not (Test-Path 'backend.spec')) {
    Write-Host 'ERROR: backend.spec not found!' -ForegroundColor Red
    exit 1
}

# Install PyInstaller if needed
pip install pyinstaller

# Build backend executable
pyinstaller backend.spec -y

if (-not (Test-Path 'dist/FindingExcellence_Backend')) {
    Write-Host 'ERROR: Backend build failed!' -ForegroundColor Red
    exit 1
}

Write-Host 'Backend build completed successfully' -ForegroundColor Green

# Phase 2: Frontend Build
Write-Host 'Phase 2: Building React Frontend...' -ForegroundColor Yellow

Set-Location frontend

# Install dependencies if needed
if (-not (Test-Path 'node_modules')) {
    npm install
}

# Build frontend with Vite
npm run build

if (-not (Test-Path 'dist')) {
    Write-Host 'ERROR: Frontend build failed!' -ForegroundColor Red
    exit 1
}

Write-Host 'Frontend build completed successfully' -ForegroundColor Green

Set-Location ..

# Phase 3: Package Electron Application
Write-Host 'Phase 3: Packaging Electron Application...' -ForegroundColor Yellow

Set-Location frontend

# Install electron-builder if needed
npm install --save-dev electron-builder

# Build Electron application
electron-builder --config electron-builder.json

if (-not (Test-Path 'dist')) {
    Write-Host 'ERROR: Electron build failed!' -ForegroundColor Red
    exit 1
}

Write-Host 'Electron packaging completed successfully' -ForegroundColor Green

Set-Location ..

# Phase 4: Final Assembly
Write-Host 'Phase 4: Final Assembly...' -ForegroundColor Yellow

# Create final distribution directory
if (Test-Path $DIST_DIR) {
    Remove-Item $DIST_DIR -Recurse -Force
}
New-Item -ItemType Directory -Path $DIST_DIR | Out-Null

# Copy Electron build
Copy-Item -Path 'frontend/out/*' -Destination $DIST_DIR -Recurse -ErrorAction SilentlyContinue

# Copy backend executable
Copy-Item -Path 'dist/FindingExcellence_Backend' -Destination $DIST_DIR -Recurse -ErrorAction SilentlyContinue

Write-Host 'Assembly completed successfully' -ForegroundColor Green

# Summary
Write-Host 'Build Summary:' -ForegroundColor Cyan
Write-Host '=' * 50
Write-Host 'Backend: PyInstaller executable created'
Write-Host 'Frontend: React build completed'
Write-Host 'Electron: Application packaged'
Write-Host "Distribution: $DIST_DIR/"
Write-Host 'Status: BUILD SUCCESSFUL' -ForegroundColor Green
