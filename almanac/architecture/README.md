---
title: Architecture
topics: [architecture]
---

# Architecture

This cluster documents FindingExcellence PRO's system boundaries: the FastAPI
backend, the desktop frontend, and the two backend subsystems they expose —
search and local AI. Read it to see which component owns which responsibility
and how the pieces fit together.

## How the pieces relate

The application is two processes communicating over HTTP on the loopback
interface:

- The **backend** ([Backend Server](backend)) is a FastAPI server bound to
  `127.0.0.1:8000`. It owns all search and AI endpoints and runs as a
  long-lived process.
- The **frontend** ([Frontend Desktop](frontend)) is a CustomTkinter desktop
  app. It talks to the backend through `frontend_desktop/api_client.py` for AI
  features and natural-language search, but can also run filename search
  locally without the backend.

The backend exposes two subsystems:

- **Search** ([Search Subsystem](search)) — filename, content, and
  natural-language search, plus SQLite caching and search history.
- **AI Integration** ([AI Integration](ai-integration)) — 100% local Ollama
  inference for document analysis, OCR, and natural-language parsing, plus
  optional PII/NER/chunking services.

The local-first decision ([Local-First Privacy](../decisions/local-first))
constrains this shape: the backend binds to the loopback interface only, all
caching is local SQLite, and no external API calls are made.

## Suggested reading order

1. [Backend Server](backend) — the core process and request flow.
2. [Search Subsystem](search) and [AI Integration](ai-integration) — the two
   subsystems the backend hosts.
