# FindingExcellence PRO 2.0 - Deployment Guide

## Building the Application

### Prerequisites

- Python 3.9+
- Node.js 18+
- npm or pnpm
- PyInstaller
- Electron

### Windows Build

#### Using PowerShell Script

```powershell
# Make sure you're in the project root directory
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.\build.ps1
```

#### Manual Build Steps

1. **Build Backend with PyInstaller**:
   ```bash
   pip install pyinstaller
   pyinstaller backend.spec -y
   ```

2. **Build Frontend**:
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```

3. **Package Electron Application**:
   ```bash
   cd frontend
   npm install --save-dev electron-builder
   electron-builder --config electron-builder.json
   cd ..
   ```

### Linux / macOS Build

#### Using Bash Script

```bash
chmod +x build.sh
./build.sh
```

#### Manual Build Steps

Same as Windows, but use bash instead of PowerShell.

## Output

After successful build, you'll find:

- **Windows**: 
  - Installer: `frontend/dist/FindingExcellence PRO 2.0 Setup.exe`
  - Portable: `frontend/dist/FindingExcellence PRO 2.0.exe`

- **Linux**:
  - AppImage: `frontend/dist/FindingExcellence_PRO-*.AppImage`
  - DEB: `frontend/dist/findingexcellence-pro-*.deb`

- **macOS**:
  - DMG: `frontend/dist/FindingExcellence PRO.dmg`
  - ZIP: `frontend/dist/FindingExcellence PRO.zip`

## Installation

### Windows

1. Download the installer or portable executable
2. Run the installer or executable
3. Follow the installation prompts
4. The application will automatically start the Python backend

### Linux

#### AppImage

```bash
chmod +x FindingExcellence_PRO-*.AppImage
./FindingExcellence_PRO-*.AppImage
```

#### DEB Package

```bash
sudo dpkg -i findingexcellence-pro-*.deb
findingexcellence-pro
```

### macOS

1. Mount the DMG file
2. Drag the application to Applications folder
3. Run from Applications or Launchpad

## Configuration

### Environment Setup

Create a `.env` file in the application directory:

```
OPENROUTER_API_KEY=your-api-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
COST_LIMIT_MONTHLY=10.00
LOG_LEVEL=INFO
```

### API Key Configuration

1. Get your OpenRouter API key from https://openrouter.ai
2. Set the `OPENROUTER_API_KEY` environment variable
3. Or configure it through the application settings UI

## Troubleshooting

### Backend Not Starting

1. Check if Python 3.9+ is installed
2. Verify all dependencies are installed: `pip install -r requirements.txt`
3. Check the application logs for errors
4. Ensure port 8000 is available

### Frontend Connection Issues

1. Verify the backend is running on port 8000
2. Check the browser console for network errors
3. Ensure firewall isn't blocking localhost connections

### PDF Processing Issues

1. For scanned PDFs, ensure OCR models are available
2. Check system RAM (OCR models need ~2GB)
3. Verify image files are readable

## Updating

### From Previous Version

1. Backup your configuration and data
2. Uninstall the old version (if using installer)
3. Install the new version
4. Configuration will be migrated automatically

## System Requirements

### Minimum

- CPU: 2 GHz dual-core
- RAM: 4 GB
- Storage: 500 MB available
- OS: Windows 7+, macOS 10.13+, Ubuntu 18.04+

### Recommended

- CPU: 2.4 GHz quad-core
- RAM: 8 GB
- Storage: 1 GB SSD
- OS: Windows 10+, macOS 11+, Ubuntu 20.04+

## Performance Tips

1. **Disable OCR** if you don't need scanned PDF processing
2. **Limit search folders** to specific directories
3. **Use file type filters** to reduce search scope
4. **Close other applications** when analyzing large documents

## Support

For issues or questions:
1. Check the application logs in `%APPDATA%/FindingExcellence/logs/` (Windows)
2. Review the README files in each module
3. Check backend error output on startup

## License

FindingExcellence PRO 2.0 - See LICENSE file for details

## Version

Current Version: 2.0.0
Last Updated: 2024
