# FindingExcellence PRO - Setup Guide

## Overview

This guide provides complete setup instructions for the FindingExcellence PRO application, including environment configuration, dependencies, and development workflow.

## Prerequisites

### System Requirements
- **Operating System**: Windows 10/11 (CMD)
- **Python**: 3.13+ (recommended) or 3.8+
- **Node.js**: 18+ with pnpm package manager
- **Git**: For version control

### Required Accounts
- **OpenRouter**: [https://openrouter.ai/](https://openrouter.ai/) - For AI API access

## Quick Setup

### 1. Clone and Navigate
```cmd
git clone <repository-url>
cd FindingExcellence_PRO
```

### 2. Automated Setup (Recommended)
```cmd
setup-cmd.bat
```

### 3. Manual Setup
```cmd
REM Python Backend
py -3.13 -m venv venv
venv\Scripts\activate.bat
pip install -r backend\requirements.txt

REM Frontend
cd frontend
pnpm install
cd ..
```

## Environment Configuration

### 1. Create Environment File
Create `.env` file in the project root:

```env
# OpenRouter API Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Backend Security
SECRET_KEY=generate_a_secure_random_key_here

# Database Configuration
DATABASE_URL=sqlite:///./findingexcellence.db

# Frontend Configuration
VITE_API_BASE_URL=http://localhost:8000

# Optional Settings
DEBUG=true
LOG_LEVEL=INFO
```

### 2. Get OpenRouter API Key
1. Visit [OpenRouter Keys](https://openrouter.ai/keys)
2. Sign up or log in
3. Create a new API key
4. Copy the key to your `.env` file

### 3. Generate Secure Secret Key
```cmd
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
Copy the output to `SECRET_KEY` in your `.env` file.

## Development Workflow

### Daily Development
```cmd
REM Activate environment
activate.bat

REM Start backend server
python backend\main.py

REM In separate terminal - Start frontend
cd frontend
pnpm run dev
```

### Application URLs
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Frontend App**: http://localhost:5173

## Security Setup

### Environment Security
- Never commit `.env` file to version control
- Use different API keys for development and production
- Rotate keys regularly

### Security Commands
```cmd
REM Run security audit
venv-manage.bat audit

REM Update dependencies
venv-manage.bat update

REM Clean environment
venv-manage.bat clean
```

## Troubleshooting

### Common Issues

#### Python Launcher Not Available
```cmd
REM Use direct Python
python -m venv venv
python -m pip install -r backend\requirements.txt
```

#### Frontend Build Issues
```cmd
cd frontend
pnpm install --force
pnpm run dev
```

#### Environment Variables Not Loading
- Ensure `.env` file is in project root
- Restart backend server after modifying `.env`
- Check for typos in variable names

### Dependency Conflicts
```cmd
venv-manage.bat audit
venv-manage.bat update
```

## Production Deployment

### Desktop Application
```cmd
cd frontend
pnpm run build-electron
```

### Web Application
- Deploy backend to cloud (AWS, Heroku, etc.)
- Deploy frontend to static hosting (Vercel, Netlify, etc.)

## File Structure

```
FindingExcellence_PRO/
├── backend/                 # Python FastAPI
│   ├── ai/                 # AI integration
│   ├── api/                # API endpoints
│   ├── core/               # Business logic
│   ├── main.py             # Application entry
│   └── requirements.txt    # Python dependencies
├── frontend/               # React + Electron
│   ├── src/               # React components
│   ├── electron/          # Electron main process
│   └── package.json       # Node.js dependencies
├── docs/                  # Documentation
├── test/                  # Test scripts
├── venv/                  # Python virtual environment
├── .env                   # Environment variables (create this)
├── activate.bat           # Quick activation
├── setup-cmd.bat          # Direct setup
└── venv-manage.bat        # Environment management
```

## Support

If you encounter issues:
1. Check this documentation
2. Run `venv-manage.bat audit` for dependency issues
3. Verify environment variables are set correctly
4. Check the project's GitHub issues

---

**Last Updated**: October 2025  
**Python Version**: 3.13+  
**Node.js Package Manager**: pnpm  
**Security Status**: Monitored with pip-audit
