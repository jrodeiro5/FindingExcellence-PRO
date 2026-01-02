# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in FindingExcellence PRO, please **do not** open a public GitHub issue. Instead, please follow our responsible disclosure process:

### How to Report

**Email**: security@ayesa.com

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Your contact information (optional but helpful)

We will acknowledge your report within **48 hours** and provide an update within **7 days**.

---

## Security Principles

### Privacy First

FindingExcellence PRO is designed with privacy as the core principle:

- ✅ **100% Local Processing** – All AI runs locally via Ollama
- ✅ **No External APIs** – Zero cloud services or external dependencies
- ✅ **No Data Collection** – No telemetry, analytics, or usage tracking
- ✅ **No Credentials in Code** – All secrets in `.env` (never committed)
- ✅ **Open Source** – Code is auditable; security through transparency

### What We Don't Do

- ❌ Send your files to external servers
- ❌ Collect or store your data
- ❌ Use third-party analytics services
- ❌ Require API keys for core functionality
- ❌ Log sensitive file paths or content

---

## Security Features

### 1. Local-Only AI Processing

All AI models run on your machine via Ollama:
- **phi4-mini** – General analysis (~2.5GB)
- **deepseek-ocr** – Vision/OCR (~3GB)
- **qwen3:4b-instruct** – Fallback model

**No data leaves your system.**

### 2. File Access Control

- Files are accessed only when explicitly searched/analyzed
- No automatic scanning or indexing of sensitive directories
- Cache is local-only in `.cache/` directory
- No network transmission of file content

### 3. Configuration Security

- **`.env` file** – Never committed to git, contains only local settings
- **API keys/tokens** – `.mcp.json` is gitignored, local only
- **Secrets management** – All tools (Supabase, Neo4j, etc.) are local development tools
- **Example configs** – `.env.example` provided without sensitive values

### 4. Database Security

- **SQLite cache** – Stored locally in `.cache/file_index.db`
- **TTL-based invalidation** – Cache expires after 1 hour by default
- **Smart invalidation** – Refreshes if folder modification times change
- **No persistence across machines** – Cache is machine-specific

### 5. Input Validation

- File paths validated before access
- File sizes checked before processing
- Encoding detection with fallbacks (UTF-8 → Latin-1 → CP1252)
- Network requests timeout after 30 seconds

### 6. Error Handling

- Errors logged locally, not sent externally
- Stack traces don't expose file paths
- Graceful degradation if Ollama unavailable
- No secrets in error messages

---

## Dependency Security

### Core Dependencies

All dependencies are open-source and vetted:

| Dependency | Purpose | Notes |
|-----------|---------|-------|
| **FastAPI** | Backend framework | Industry standard, well-maintained |
| **CustomTkinter** | Desktop UI | Modern Python GUI framework |
| **Ollama** | Local AI | 100% local, no external calls |
| **Pandas/Polars** | Data processing | Standard data science tools |
| **pdfplumber** | PDF extraction | No external API calls |

### No Risky Dependencies

- ❌ No cloud SDKs in production code
- ❌ No tracking/analytics libraries
- ❌ No ad networks or marketing tools
- ❌ No experimental or unmaintained packages

### Vulnerability Scanning

We monitor dependencies for known vulnerabilities. If critical issues are found:
1. We patch immediately
2. Release a security update
3. Notify users with instructions

---

## Code Security

### Input Validation

```python
# File paths validated
file_path = Path(user_input)
if not file_path.exists():
    return "", "File not found"
if file_path.is_dir():
    return "", "Expected file, got directory"
```

### Error Messages

```python
# ✅ GOOD - No sensitive info
logger.error(f"Failed to process file: {e}")

# ❌ BAD - Exposes paths
logger.error(f"Failed to process {file_path}: {e}")
```

### Threading Safety

All UI updates happen on the main thread:
```python
# ✅ CORRECT - Safe
def _run_search():
    results = search()
    self.after(0, lambda: self._update_ui(results))

# ❌ WRONG - Can crash
def _run_search():
    self.label.configure(text="...")  # CRASH!
```

---

## Configuration Best Practices

### `.env` File (Not Committed)

```env
# These are safe defaults - customize as needed
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=phi4-mini
DEFAULT_SEARCH_FOLDERS=C:\Users\YourName\Desktop
```

### Sensitive Files (Gitignored)

```
.env              # Local config (NEVER commit)
.mcp.json         # Development tool configs (NEVER commit)
*.log             # Runtime logs with file paths
.cache/           # Local cache
temp_uploads/     # Uploaded files
```

### Verify Your Setup

```cmd
# Check nothing sensitive is tracked
git ls-files | grep -E "(\.env|\.mcp\.json|\.log|\.db)"

# Should return nothing if properly configured

# Check .gitignore is working
git check-ignore .env        # Should say "matched by pattern .env"
git check-ignore .mcp.json   # Should say "matched by pattern .mcp.json"
```

---

## Ollama Security

Ollama runs locally on `http://localhost:11434` by default.

### Access Control

- **Local access only** – Not exposed to internet by default
- **No authentication** – Ollama assumes trusted local network
- **Firewall protection** – Port 11434 is local-only

### Model Safety

- Models are open-source and auditable
- phi4-mini is from Microsoft Research (safe)
- deepseek-ocr is from Deepseek (safe)
- All models run sandboxed on your machine

### Configuration

```env
# Secure defaults
OLLAMA_HOST=http://localhost:11434     # Local only
OLLAMA_KEEP_ALIVE=-1                   # Keep loaded
OLLAMA_TEMPERATURE=0.3                 # Deterministic
```

**⚠️ WARNING**: Never set `OLLAMA_HOST=0.0.0.0:11434` – this exposes Ollama to the network!

---

## Data Security

### What Data Is Stored?

| Data | Location | Retention | Access |
|------|----------|-----------|--------|
| File index cache | `.cache/file_index.db` | 1 hour (TTL) | Local only |
| Configuration | `.env` | Until deleted | Local only |
| Logs | `*.log` files | Until rotated | Local only |
| Uploaded files | `temp_uploads/` | Until deleted | Local only |

### What Data Is NOT Stored?

- ❌ File contents (except during analysis)
- ❌ Analysis results (except in temporary memory)
- ❌ User activity/telemetry
- ❌ Network traffic logs

### Cleanup

```cmd
# Remove cache (will rebuild on next search)
rmdir /s .cache

# Clear logs
del *.log

# Clear uploads
rmdir /s temp_uploads
```

---

## Updating & Patching

### How to Stay Secure

1. **Check for updates regularly**
   ```cmd
   git pull origin main
   ```

2. **Update dependencies**
   ```cmd
   .venv\Scripts\activate.bat
   uv pip install --upgrade -e .
   ```

3. **Update Ollama models**
   ```cmd
   ollama pull phi4-mini      # Get latest version
   ollama pull deepseek-ocr
   ```

### Security Updates

When we release security patches:
- Announcement in GitHub Releases
- Clear description of vulnerability and fix
- Upgrade instructions provided
- Backports if needed

---

## Penetration Testing & Audits

We welcome security researchers and penetration testers to review our code. Please:

1. **Report vulnerabilities responsibly** – Use security@ayesa.com
2. **Don't access other users' data** – Only test on your own files
3. **Don't perform DoS attacks** – Testing is allowed within reason
4. **Disclose responsibly** – Give us time to patch before public disclosure

### What's In Scope

- ✅ File search implementation
- ✅ AI integration with Ollama
- ✅ API endpoints
- ✅ Desktop UI threading
- ✅ Configuration handling
- ✅ Cache invalidation

### What's Out of Scope

- ❌ Ollama security (test with Ollama team)
- ❌ Operating system vulnerabilities
- ❌ Third-party dependency vulnerabilities (report to maintainers)

---

## Compliance & Standards

### Privacy Standards

- **GDPR-Compatible** – No data collection, all local
- **CCPA-Compatible** – No personal data sharing
- **No Analytics** – No tracking, no compliance needed

### Development Standards

- **OWASP Top 10** – We avoid known vulnerabilities
- **Python Security** – Follow PEP 623, PEP 647 guidelines
- **Code Review** – All changes reviewed for security

---

## Known Issues & Limitations

### Windows-Only

FindingExcellence PRO is developed for Windows. Linux/macOS support is not tested and not guaranteed.

### Ollama Requirements

- Ollama must be running for AI features to work
- Models must be pre-downloaded (takes 5-10GB total)
- First request is slow (~30s) as models warm up

### Performance Trade-offs

- File search doesn't use Windows Search Index (to avoid indexing every file)
- We use SQLite cache instead (local, privacy-respecting alternative)
- Slightly slower than Windows Search but much more private

---

## Security Checklist for Contributors

When contributing, ensure:

- [ ] No hardcoded secrets (API keys, passwords)
- [ ] No user paths hardcoded (use `C:\Users\TestUser\...` for tests)
- [ ] No external API calls (use local alternatives)
- [ ] Input validation on all user data
- [ ] Error messages don't leak sensitive info
- [ ] Tests don't create security issues
- [ ] Dependencies are vetted
- [ ] Comments don't reveal security details

See [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

---

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/) – Common vulnerabilities
- [CWE/SANS](https://cwe.mitre.org/top25/) – Software weaknesses
- [Python Security](https://python.readthedocs.io/en/latest/library/security_warnings.html)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

---

## Changelog

### v2.0.0 (Current)
- Initial security audit
- LocalAI through Ollama
- File search with SQLite caching
- Privacy-first design

---

**Last Updated**: January 2, 2026

**Questions about security?** Contact security@ayesa.com
