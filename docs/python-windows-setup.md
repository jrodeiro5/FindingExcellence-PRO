# Python Windows Setup Guide - Direct CMD Approach

## Overview

This document provides setup instructions for Python development on Windows systems using direct Windows CMD commands. This approach bypasses Python Launcher issues and uses exact Python paths for reliable environment setup in the FindingExcellence PRO project.

## Direct CMD Setup Approach

### Why Use Direct CMD Approach?

The direct CMD approach uses exact Python paths instead of relying on the Python Launcher (`py`). This method:
- Eliminates Python Launcher dependency issues
- Uses exact Python executable paths for reliability
- Works consistently across different Windows environments
- Bypasses Windows Store Python alias conflicts

### Project-Specific Direct Setup

#### Direct Setup Script

The project includes a direct setup script that uses exact Python paths:
```cmd
REM Run direct setup (recommended)
setup-cmd.bat
```

This script:
- Uses exact Python path: `C:\Users\jrodeiro\AppData\Local\Programs\Python\Python313\python.exe`
- Creates virtual environment directly
- Installs all dependencies
- Sets up security tools

#### Manual Direct Commands

If you prefer manual setup, use these direct commands:
```cmd
REM 1. Create virtual environment using exact Python path
C:\Users\jrodeiro\AppData\Local\Programs\Python\Python313\python.exe -m venv venv

REM 2. Activate environment
venv\Scripts\activate.bat

REM 3. Install dependencies
pip install -r backend\requirements.txt

REM 4. Install security tools
pip install pip-audit safety
```

#### Quick Activation

After setup, use the quick activation script:
```cmd
activate.bat
```

Or manual activation:
```cmd
venv\Scripts\activate.bat
```

### Common Issues and Solutions

#### Issue: "El sistema no puede encontrar la ruta especificada"

This error typically indicates:
- Terminal is not Windows CMD (using PowerShell, Git Bash, etc.)
- Python Launcher conflicts with Windows Store Python alias
- Environment variables not properly set

#### Solution: Use Direct CMD Approach
1. **Open Windows Command Prompt** (not PowerShell, not Git Bash)
2. **Use direct setup**: `setup-cmd.bat`
3. **Or use manual commands** with exact Python paths
4. **Verify environment**: Should show `(venv)` prefix when activated

### Verification Steps

After setup, verify your environment:
```cmd
REM Check virtual environment activation
echo %VIRTUAL_ENV%

REM Check Python version
python --version

REM Check installed packages
pip list

REM Run security audit
venv-manage.bat audit
```

```

## Windows CMD Best Practices

### Always Use Windows CMD

- Use **Windows Command Prompt** for all Python operations
- Avoid PowerShell, Git Bash, or other shells for batch scripts
- Batch files (`.bat`) require Windows CMD environment
- Direct Python path approach works consistently in CMD

### Project Scripts Available

- `setup-cmd.bat` - Direct environment setup (recommended)
- `activate.bat` - Quick environment activation
- `venv-manage.bat` - Environment management and security
- `test\*.bat` - Test and debug utilities

### Security Commands

```cmd
REM Security audit
venv-manage.bat audit

REM Update dependencies
venv-manage.bat update

REM Clean environment
venv-manage.bat clean
```

## Troubleshooting

### Terminal Environment Issues

If scripts fail with path errors:
1. **Verify you're in Windows CMD** (not PowerShell)
2. **Check current directory**: `echo %CD%`
3. **Use direct setup**: `setup-cmd.bat`
4. **Manual fallback**: Use exact Python path commands

### Python Path Conflicts

If `python` command redirects to Windows Store:
- Use `py` command instead
- Or use exact Python path: `C:\Users\jrodeiro\AppData\Local\Programs\Python\Python313\python.exe`
- The direct setup script handles this automatically

### Virtual Environment Activation

If virtual environment doesn't activate:
- Verify `(venv)` appears in command prompt
- Check `echo %VIRTUAL_ENV%` shows path
- Use `venv\Scripts\activate.bat` directly
- Ensure no Python processes are running that might conflict

## Quick Reference

### Daily Development Workflow

```cmd
REM Start development session
activate.bat

REM Run backend server
python backend\main.py

REM Run security check
venv-manage.bat audit

REM End session
deactivate
```

### Direct Commands Summary

```cmd
REM Setup (one-time)
setup-cmd.bat

REM Daily use
activate.bat
python backend\main.py

REM Security
venv-manage.bat audit
venv-manage.bat update
```

### Daily Usage

```cmd
REM Quick activation
activate.bat

REM Manual activation
venv\Scripts\activate.bat

REM Deactivate when finished
deactivate
```

### Security and Maintenance

```cmd
REM Run security audit
venv-manage.bat audit

REM Update dependencies
venv-manage.bat update

REM Clean environment
venv-manage.bat clean
```

## Common Error Messages

| Error Message | Cause | Solution |
|---------------|-------|----------|
| "py is not recognized" | Python Launcher not installed | Install Python from python.org |
| "El sistema no puede encontrar la ruta especificada" | PATH issue or Python not installed | Verify Python installation and PATH |
| "No module named venv" | Python installed without venv module | Reinstall Python with all features |
| Virtual environment not activating | Activation script issues | Use full path: `call venv\Scripts\activate.bat` |

## Best Practices

1. **Always use virtual environments** for project isolation
2. **Pin dependency versions** in `requirements.txt`
3. **Regular security audits** with `venv-manage.bat audit`
4. **Keep Python updated** to latest stable version
5. **Use Python Launcher** (`py`) for version management

## Support

If issues persist:
1. Check the project's `README.md` for additional setup instructions
2. Verify Python installation from Command Prompt
3. Contact the development team with specific error messages

---

**Last Updated**: October 2025  
**Compatible Python Versions**: 3.11, 3.12, 3.13+
