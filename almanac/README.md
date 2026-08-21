---
title: FindingExcellence PRO Wiki
topics: [concepts, architecture]
---

# FindingExcellence PRO Wiki

This wiki documents the durable knowledge of FindingExcellence PRO: a privacy-first desktop application for intelligent file search with local AI analytics.

## System Overview

FindingExcellence PRO is a Python application (3.12+) that combines fast file search with local AI-powered analysis. All AI processing happens locally via Ollama—zero external API calls.

**Key subsystems:**

- **Backend** ([Backend Server](architecture/backend)) — FastAPI server on port 8000, exposing search and analysis endpoints
- **Frontend** ([Frontend Desktop](architecture/frontend)) — CustomTkinter desktop UI with dark theme
- **AI Integration** ([AI Integration](architecture/ai-integration)) — Ollama client with model warmup, fallback chains, and usage tracking
- **Search Engine** ([Search Subsystem](architecture/search)) — Multi-threaded filename search with SQLite caching, content search across file formats

## Wiki Structure

| Category | Purpose |
|----------|---------|
| [Architecture](architecture/backend) | System boundaries, flows, and constraints |
| [Decisions](decisions/local-first) | Architectural choices and rationale |
| [Guides](guides/setup) | Operational task instructions |
| [Reference](reference/api-endpoints) | Exact contracts and configurations |

## Quick Navigation

- New to the codebase? Start with [Backend Server](architecture/backend)
- Need to run the app? See [Setup Guide](guides/setup)
- Working with AI features? See [AI Integration](architecture/ai-integration)
- Building API changes? See [Backend Architecture](architecture/backend) and [API Reference](reference/api-endpoints)
