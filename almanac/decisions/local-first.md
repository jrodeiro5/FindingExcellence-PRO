---
title: Local-First Privacy
topics: [decisions]
sources:
  - {id: readme, type: file, path: README.md}
  - {id: claudem, type: file, path: CLAUDE.md}
  - {id: main-py, type: file, path: backend/main.py}
  - {id: ollama-client, type: file, path: backend/ai/ollama_client.py}
---

# Local-First Privacy

**Status:** Active
**Context:** Cloud-based search and AI services require uploading user data
to external servers, creating privacy risks for sensitive documents.

## Decision

All processing happens locally on the user's machine. The application uses:

- **Ollama** for local LLM inference (phi4-mini, qwen3:4b-instruct,
  deepseek-ocr). The `OllamaClient` ([@ollama-client]) manages connections
  to a local Ollama instance with model warmup, fallback chains, and usage
  tracking.
- **FastAPI** running on `127.0.0.1` (loopback only, not exposed to network).
  The backend at `backend/main.py` ([@main-py]) binds to `127.0.0.1:8000`
  and returns `503` when AI features are unavailable.
- **SQLite** for all caching and history (local files, no cloud sync).
- **CustomTkinter** for the desktop UI (no web browser, no network).

The README ([@readme]) and CLAUDE.md ([@claudem]) both emphasize the
"100% local, zero external APIs" positioning as a core product identity.

No external API calls are made. No data is collected, tracked, or transmitted.
No API keys are stored in code. The codebase is open source for audit.

## Consequences

**Easier:**

- Users with sensitive documents can use the application without privacy
  concerns.
- The application works fully offline once Ollama models are downloaded.
- No account creation, authentication, or subscription required.
- Code is auditable — users can verify no data exfiltration.

**Harder:**

- Users must install and configure Ollama locally (~5.5 GB of models).
- CPU inference is slower than cloud APIs, especially for large documents.
- The application cannot leverage cloud-based model improvements.
- Users with limited disk space or older hardware may struggle with model
  downloads and inference times.

**Required:**

- Ollama must be installed and running for AI features. The application
  degrades gracefully when Ollama is unavailable — file search still works.
- Users must manage their own Ollama models (pull, update, remove).

**Forbidden:**

- No external API calls for AI inference.
- No telemetry, analytics, or data collection.
- No cloud storage or sync.
- No credentials stored in code.

## Related

See [AI Integration](../architecture/ai-integration) for implementation
details. See [Setup](../guides/setup) for Ollama installation instructions.
