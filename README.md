# FindingExcellence PRO

AI-powered Excel and PDF search application with advanced document processing capabilities.

## 🚀 Quick Service Management

### Start All Services
```cmd
start-all.bat
```
- Starts backend API (port 8000) and frontend (port 5173) in separate windows
- Shows service status and URLs
- Includes health checks

### Simple Startup
```cmd
start-simple.bat
```
- Starts all services in background
- Frontend runs in current window
- Quick and clean

### Stop All Services
```cmd
stop-all.bat
```
- Stops all backend and frontend processes
- Cleans up ports and processes
- Safe shutdown

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** (Recommended: Python 3.13)
- **Node.js 18+** (with pnpm package manager)
- **Windows CMD** (Command Prompt) - Required for batch scripts

### Installation

#### 1. Clone and Setup
```cmd
git clone <repository-url>
cd FindingExcellence_PRO
```

#### 2. Python Backend Setup
```cmd
REM Option A: Direct CMD setup (recommended)
setup-cmd.bat

REM Option B: Use automated setup
venv-manage.bat install

REM Option C: Manual setup with Python Launcher
py -3.13 -m venv venv
venv\Scripts\activate.bat
pip install -r backend\requirements.txt
```

#### 3. Frontend Setup
```cmd
cd frontend
pnpm install
cd ..
```

#### 4. Quick Activation (Daily Use)
```cmd
activate.bat
```

#### 5. Service Management (Recommended)
```cmd
start-all.bat        # Start all services
stop-all.bat         # Stop all services
```

## 🛡️ Security Architecture

### Virtual Environment Strategy
- All Python dependencies are isolated in `venv/` directory
- Environment automatically excluded from version control
- Regular security audits with `pip-audit`

### Security Commands
```cmd
# Run security audit
venv-manage.bat audit

# Update dependencies securely
venv-manage.bat update

# Clean environment
venv-manage.bat clean
```

### Environment Variables
Create `.env` file in project root (never commit to version control):
```env
# Backend Configuration
OPENROUTER_API_KEY=your_openrouter_key_here
SECRET_KEY=generated_secure_random_key
DATABASE_URL=postgresql://user:pass@localhost/dbname

# Frontend Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_ENV=development
```

## 📁 Project Structure

```
FindingExcellence_PRO/
├── backend/                 # Python FastAPI backend
│   ├── ai/                 # AI integration modules
│   ├── api/                # API endpoints
│   ├── core/               # Core business logic
│   ├── utils/              # Utility functions
│   ├── tests/              # Test suite
│   └── main.py             # Application entry point
├── frontend/               # React/Electron frontend
│   ├── src/               # React source code
│   ├── electron/          # Electron main process
│   └── package.json       # Node.js dependencies
├── docs/                  # Documentation
│   ├── security-coherence.md
│   ├── setup.md
│   └── architecture.md
├── test/                  # Test and debug scripts
│   ├── test.bat
│   ├── debug.bat
│   └── debug.py
├── resources/             # Application resources
├── venv/                 # Python virtual environment (gitignored)
├── activate.bat          # Quick environment activation
├── venv-manage.bat       # Virtual environment management
└── README.md            # This file
```

## 🎯 Usage

### Development Mode

#### Backend (FastAPI)
```cmd
activate.bat
python backend\main.py
```
Server runs at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

#### Frontend (React + Electron)
```cmd
cd frontend
pnpm run dev
```

### Production Build
```cmd
REM Build frontend
cd frontend
pnpm run build-electron

REM Start backend in production
activate.bat
python backend\main.py
```

## 🔧 Development Tools

### Batch Scripts
- `activate.bat` - Quick environment activation
- `venv-manage.bat` - Virtual environment management
- `start-all.bat` - Start all services (recommended)
- `start-simple.bat` - Simple service startup
- `stop-all.bat` - Stop all services
- `test\test.bat` - Run test suite
- `test\debug.bat` - Debug utilities

### Security Features
- Input validation and sanitization
- Secure file processing
- API authentication
- Dependency vulnerability scanning
- Environment variable protection

## 📚 Documentation

- **Security & Coherence**: `docs\security-coherence.md`
- **Architecture**: `docs\architecture.md` 
- **Setup Guide**: `docs\setup.md`
- **API Documentation**: Available at `/docs` when backend is running

## 🐛 Troubleshooting

### Common Issues

**Python Launcher Not Available ("py is not recognized")**
```cmd
REM Use direct CMD setup (recommended):
setup-cmd.bat

REM Or use direct Python commands:
python -m venv venv
python -m pip install -r backend\requirements.txt
REM See docs\python-windows-setup.md for detailed troubleshooting
```

**Virtual Environment Not Activating**
```cmd
REM Recreate environment
venv-manage.bat clean
venv-manage.bat install

REM Manual activation
venv\Scripts\activate.bat
```

**Dependency Conflicts**
```cmd
venv-manage.bat audit
venv-manage.bat update
```

**Frontend Build Issues**
```cmd
cd frontend
pnpm install --force
pnpm run build
```

**"El sistema no puede encontrar la ruta especificada"**
- Terminal is not Windows CMD (use Command Prompt, not PowerShell/Git Bash)
- Use direct CMD setup: setup-cmd.bat
- Or use exact Python path: C:\Users\jrodeiro\AppData\Local\Programs\Python\Python313\python.exe -m venv venv

**Services Not Starting**
- Use `start-all.bat` for automatic service management
- Check ports 8000 and 5173 are not in use
- Run `stop-all.bat` first to clean up any stuck processes

### Security Issues
- Run `venv-manage.bat audit` regularly
- Check `docs\security-coherence.md` for security guidelines
- Never commit `.env` files or API keys

## 🤝 Contributing

1. Ensure virtual environment is active: `activate.bat`
2. Run security audit: `venv-manage.bat audit`
3. Test service startup: `start-all.bat` and `stop-all.bat`
4. Follow security guidelines in `docs\security-coherence.md`
5. Test changes thoroughly
6. Update documentation as needed

## 📄 License

[Your License Here]

## 🔒 Security Contact

Report security vulnerabilities to: security@yourapp.com

---

**Last Updated**: $(date)  
**Python Version**: 3.13+  
**Node.js Package Manager**: pnpm  
**Security Status**: Monitored with pip-audit
