# Contributing to FindingExcellence PRO

Thank you for your interest in contributing! We welcome bug reports, feature requests, and code contributions.

---

## Ways to Contribute

### Report a Bug
If you found a bug:
1. Check if it's already reported in [Issues](https://github.com/jrodeiro5/FindingExcellence-PRO/issues)
2. Create a new issue with:
   - Clear title describing the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment (Python version, OS, Windows build)
   - Relevant logs from `finding_excellence.log` or `finding_excellence_desktop.log`

### Suggest a Feature
Feature requests are tracked in [Issues](https://github.com/jrodeiro5/FindingExcellence-PRO/issues). Before suggesting:
1. Check existing feature requests
2. Describe the use case and expected behavior
3. Explain why it would be valuable
4. Consider privacy implications (we prioritize privacy-first design)

### Submit Code

#### Prerequisites
- Python 3.12+
- Windows 10+ (development is Windows-focused)
- Ollama installed (for AI features)

#### Setup

```cmd
# Clone your fork
git clone https://github.com/YOUR_USERNAME/FindingExcellence-PRO.git
cd FindingExcellence-PRO

# Setup environment
uv-setup.bat

# Activate
.venv\Scripts\activate.bat
```

#### Development Workflow

1. **Create a feature branch**
   ```cmd
   git checkout -b feature/your-feature-name
   ```

2. **Make changes**
   - Follow the code standards below
   - Keep changes focused and minimal
   - Update tests if needed

3. **Test your changes**
   ```cmd
   # Run all tests
   pytest

   # Run specific test
   pytest backend/tests/test_core.py::test_function_name -v

   # Check coverage
   pytest --cov=backend --cov-report=html
   ```

4. **Lint and format**
   ```cmd
   # Check for issues
   ruff check backend/ --fix

   # Format code
   ruff format backend/

   # Type checking
   basedpyright backend/
   ```

5. **Commit with clear messages**
   ```cmd
   git add .
   git commit -m "feat: add new feature" -m "Brief description of changes"
   ```

   Use conventional commits:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation
   - `test:` for test changes
   - `refactor:` for code refactoring
   - `perf:` for performance improvements

6. **Push and open a Pull Request**
   ```cmd
   git push origin feature/your-feature-name
   ```
   Then open a PR on GitHub with:
   - Clear title and description
   - Reference to related issues (fixes #123)
   - Screenshots if UI changes
   - Test results

#### Pull Request Guidelines

- **One feature per PR** – keep changes focused
- **Tests required** – add tests for new functionality
- **Documentation** – update docs if changing behavior
- **No breaking changes** – unless discussed in an issue
- **Respect privacy** – no cloud APIs, no telemetry, no external calls

---

## Code Standards

### Style

We use `ruff` for formatting and linting. Configuration in `pyproject.toml`:
- Line length: 100 characters
- Python 3.12+ syntax
- Double quotes for strings
- Space indentation (4 spaces)

### Structure

Follow existing patterns in the codebase:

**Backend services** (`backend/ai/`, `backend/core/`):
```python
class MyService:
    """Brief description."""

    def __init__(self):
        """Initialize service."""
        self.state = None

    def process(self, data: str) -> tuple[str, str | None]:
        """Process data.

        Args:
            data: Input string

        Returns:
            (result, error) - result is str, error is None on success
        """
        try:
            result = do_something(data)
            return result, None
        except Exception as e:
            return "", str(e)
```

**Frontend components** (`frontend_desktop/ui/`):
```python
import customtkinter as ctk
from typing import Callable

class MyPanel(ctk.CTkFrame):
    """Panel description."""

    def __init__(self, parent, on_action_callback: Callable):
        super().__init__(parent)
        self.on_action = on_action_callback
        self._build_ui()

    def _build_ui(self):
        """Build UI components."""
        button = ctk.CTkButton(self, text="Action", command=self._on_click)
        button.pack(padx=10, pady=10)

    def _on_click(self):
        """Handle button click."""
        # Run in background thread to avoid blocking UI
        import threading
        thread = threading.Thread(target=self._run_action, daemon=True)
        thread.start()

    def _run_action(self):
        """Background work (don't update UI here!)."""
        result = self.on_action()
        # Schedule UI update on main thread
        self.after(0, lambda: self._display_result(result))

    def _display_result(self, result):
        """Update UI with result (runs on main thread)."""
        pass
```

**API endpoints** (`backend/main.py`):
```python
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException

class MyRequest(BaseModel):
    """Request model."""
    data: str

app = FastAPI()

@app.post("/api/my-endpoint")
async def my_endpoint(request: MyRequest):
    """Brief description of endpoint.

    Args:
        request: Request data

    Returns:
        JSON response with success status
    """
    try:
        result = do_something(request.data)
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

### Testing

- Write tests for new features
- Use `pytest` for unit and integration tests
- Place tests in `backend/tests/`
- Mark tests with `@pytest.mark.unit` or `@pytest.mark.integration`

```python
import pytest

@pytest.mark.unit
def test_feature():
    """Test description."""
    result = my_function("input")
    assert result == "expected"

@pytest.mark.integration
def test_feature_with_ollama():
    """Integration test requiring Ollama."""
    service = AIService()
    assert service.is_available()
```

---

## Documentation

- **CLAUDE.md** – Architecture, patterns, debugging for developers
- **README.md** – User-facing overview and quick start
- **SECURITY.md** – Security policy and vulnerability reporting
- **docs/** – Detailed documentation

When changing behavior:
1. Update relevant documentation
2. Add docstrings to new functions
3. Include examples if complex

---

## Architecture Overview

**Backend** → **Frontend** communication:
```
Desktop UI (.py files in frontend_desktop/ui/)
    ↓
API Client (frontend_desktop/api_client.py)
    ↓ HTTP
FastAPI (backend/main.py)
    ↓
Services (backend/ai/, backend/core/)
    ↓
Ollama / File System
```

**Key patterns**:
- **Threading**: All long operations happen in background threads
- **UI Updates**: Use `self.after(0, callback)` to safely update UI from background threads
- **Error Handling**: Return `(result, error)` tuples; let caller decide how to handle
- **Graceful Degradation**: Services have `is_available()` methods; app works without Ollama

See [CLAUDE.md](CLAUDE.md) for detailed architecture and patterns.

---

## Setting Up IDE

### VS Code
```json
{
    "python.linting.ruffEnabled": true,
    "python.linting.ruffArgs": ["--line-length=100"],
    "[python]": {
        "editor.formatOnSave": true,
        "editor.defaultFormatter": "charliermarsh.ruff"
    }
}
```

### PyCharm
- Settings → Project → Python Code Style → Ruff
- Enable "Run ruff on file save"
- Code style: PEP 8 with line length 100

---

## Debugging

### Backend
```cmd
# Check logs
type finding_excellence.log | tail -50

# Run with verbose output
python -u backend/main.py

# Check health endpoint
curl http://localhost:8000/health
```

### Frontend
```cmd
# Check logs
type finding_excellence_desktop.log | tail -50

# Run with output
.venv\Scripts\python.exe -u frontend_desktop/main.py
```

### Tests
```cmd
# Run with output capture disabled
pytest -s

# Run specific test with full output
pytest backend/tests/test_core.py::test_search -vv
```

---

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new feature
fix: resolve bug in search
docs: update README
test: add tests for file search
refactor: simplify UI threading
perf: optimize cache performance
```

Format:
```
<type>: <subject>

<body>

<footer>
```

Example:
```
feat: add semantic chunking for documents

Implement semantic chunking using Chonkie library to break
large documents into meaningful chunks for better analysis.

Fixes #123
```

---

## Release Process

(Maintained by project owners)

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create git tag: `v2.0.1`
4. Create GitHub release with notes

---

## Questions?

- Check [CLAUDE.md](CLAUDE.md) for architecture details
- Check [Issues](https://github.com/jrodeiro5/FindingExcellence-PRO/issues) for similar questions
- Ask in a GitHub Discussion

---

## Code of Conduct

This project is committed to providing a welcoming and inclusive environment for all contributors. Please be respectful, inclusive, and constructive.

---

Thank you for contributing to FindingExcellence PRO! 🎉
