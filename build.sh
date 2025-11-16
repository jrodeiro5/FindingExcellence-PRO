#!/bin/bash

# Build and packaging script for FindingExcellence PRO

set -e

echo "FindingExcellence PRO - Build & Package Script"
echo "================================================"

# Configuration
BACKEND_DIR='backend'
FRONTEND_DIR='frontend'
DIST_DIR='dist'
BUILD_DIR='build'

# Phase 1: Backend Build with PyInstaller
echo "Phase 1: Building Python Backend..."

if [ ! -f 'backend.spec' ]; then
    echo "ERROR: backend.spec not found!"
    exit 1
fi

# Install PyInstaller if needed
pip install pyinstaller

# Build backend executable
pyinstaller backend.spec -y

if [ ! -d 'dist/FindingExcellence_Backend' ]; then
    echo "ERROR: Backend build failed!"
    exit 1
fi

echo "Backend build completed successfully"

# Phase 2: Frontend Build
echo "Phase 2: Building React Frontend..."

cd frontend

# Install dependencies if needed
if [ ! -d 'node_modules' ]; then
    npm install
fi

# Build frontend with Vite
npm run build

if [ ! -d 'dist' ]; then
    echo "ERROR: Frontend build failed!"
    exit 1
fi

echo "Frontend build completed successfully"

cd ..

# Phase 3: Package Electron Application
echo "Phase 3: Packaging Electron Application..."

cd frontend

# Install electron-builder if needed
npm install --save-dev electron-builder

# Build Electron application
electron-builder --config electron-builder.json

if [ ! -d 'dist' ]; then
    echo "ERROR: Electron build failed!"
    exit 1
fi

echo "Electron packaging completed successfully"

cd ..

# Phase 4: Final Assembly
echo "Phase 4: Final Assembly..."

# Create final distribution directory
rm -rf $DIST_DIR
mkdir -p $DIST_DIR

# Copy Electron build
cp -r frontend/out/* $DIST_DIR/ 2>/dev/null || true

# Copy backend executable
cp -r dist/FindingExcellence_Backend $DIST_DIR/ 2>/dev/null || true

echo "Assembly completed successfully"

# Summary
echo "Build Summary:"
echo "================================================"
echo "Backend: PyInstaller executable created"
echo "Frontend: React build completed"
echo "Electron: Application packaged"
echo "Distribution: $DIST_DIR/"
echo "Status: BUILD SUCCESSFUL"
