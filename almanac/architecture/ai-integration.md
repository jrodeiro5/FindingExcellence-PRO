---
title: AI Integration
topics: [architecture, ai-integration]
sources:
  - {id: ollama-client, type: file, path: backend/ai/ollama_client.py}
  - {id: ai-services, type: file, path: backend/ai/ai_services.py}
  - {id: data-analyzer, type: file, path: backend/ai/data_analyzer.py}
  - {id: batch-analyzer, type: file, path: backend/ai/batch_analyzer.py}
  - {id: pii-service, type: file, path: backend/ai/pii_service.py}
  - {id: ner-service, type: file, path: backend/ai/ner_service.py}
  - {id: chunking-service, type: file, path: backend/ai/chunking_service.py}
---

# AI Integration

AI features run 100% locally via Ollama. No external API calls, no cloud
services, no data leaves the machine. The AI layer sits above the Ollama
HTTP API and provides document analysis, OCR, natural language search, and
optional PII/NER/chunking services.

## Ollama Client

`OllamaClient` ([@ollama-client]) manages the connection to a local Ollama
instance at `http://localhost:11434` (configurable via `OLLAMA_HOST`).

### Model Configuration

Three models serve different purposes:

| Model | Purpose | Size | Notes |
|-------|---------|------|-------|
| `phi4-mini` | General text analysis | ~2.5 GB | Fast CPU inference |
| `qwen3:4b-instruct` | Fallback general model | ~4 GB | Used when phi4-mini fails |
| `deepseek-ocr` | Vision/OCR | ~3 GB | 97% OCR accuracy |

The client maintains fallback chains: general requests try `phi4-mini` first,
then `qwen3:4b-instruct`, then `qwen3:4b`. Vision requests use `deepseek-ocr`
only (no fallback).

### Model Warmup

On initialization, the client warms up models in a background daemon thread.
Warmup sends a minimal `"Hi"` prompt to load the model into memory,
eliminating cold-start latency for the first real request. The warmup can
be synchronous (blocking) or asynchronous (non-blocking).

### Inference Parameters

Default parameters are tuned for CPU speed:

- `OLLAMA_CONTEXT_SIZE=512` (smaller context = faster)
- `OLLAMA_TEMPERATURE=0.2` (lower = more deterministic)
- `OLLAMA_MAX_TOKENS=256` (reduced for CPU speed)
- `OLLAMA_KEEP_ALIVE="5m"` (keep model in memory 5 minutes after last use)

The `think` option is disabled for faster inference on Qwen3 and DeepSeek-R1
models.

### Usage Tracking

`UsageStats` records `prompt_tokens`, `completion_tokens`, `total_tokens`,
`latency_ms`, and `model` per request. Aggregated stats are available via
`get_usage_summary()`. Cost is always $0.00 since all inference is local.

## AI Services Layer

`AISearchService` ([@ai-services]) wraps `OllamaClient` and provides high-level
features:

- **`natural_language_search(query)`** — converts natural language (e.g.,
  "Find budget files from last month") into structured search parameters
  (keywords, date ranges). Uses a strict JSON-parsing prompt with generic
  keyword filtering.
- **`analyze_document(content, analysis_type)`** — runs document analysis
  (summary, key_points, anomalies, insights, trends). Content is truncated
  to 1500 characters before sending to the LLM.
- **`ocr_from_image(image_url, extract_tables)`** — extracts text or tables
  from images using vision models. Image URLs are converted to base64.
- **`semantic_search(content, query)`** — finds semantically relevant sections
  by meaning rather than keyword matching.

## Hybrid Data Analysis

For tabular data (CSV, Excel), the system uses a two-step approach
([@data-analyzer]):

1. Extract statistics with Polars (preferred) or Pandas: row counts, column
   types, numeric min/max/mean, categorical top values, null percentages.
2. Send the condensed statistical summary to the LLM for interpretation.

This is much faster and more accurate than sending raw data to the LLM.
The `DataAnalyzer` class handles both CSV and Excel formats, reading up to
10,000 rows for CSV and 5,000 rows per sheet for Excel.

## Optional Services

Three optional services extend AI capabilities:

- **PII detection/masking** ([@pii-service]) — uses Microsoft Presidio with
  spaCy for detection and anonymization. Installed via `[privacy]` extras.
- **Named entity recognition** ([@ner-service]) — uses GliNER for entity
  extraction. Installed via `[ner]` extras.
- **Semantic chunking** ([@chunking-service]) — splits documents into
  semantically coherent chunks. Installed via `[chunking]` extras.

Each optional service has an `is_available()` check and degrades gracefully
when the dependency is missing.

## Batch Analysis

`BatchAnalyzer` ([@batch-analyzer]) processes 2-100 files in a single request.
Each file is extracted and analyzed independently; failed files are recorded
with errors. A consolidated summary across all files is generated at the end.
Temp files are cleaned up in a `finally` block.
