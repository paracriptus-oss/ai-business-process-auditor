# Architecture

## Overview

AI Business Process Auditor uses a multi-stage pipeline:

```text
OFFLINE passport
↓
Phase 1 — Diagnosis (API)
↓
Phase 2 — Final report (API)
↓
Phase 3 — Reviewer pass
↓
Normalized audit report
```

## Main components

- OFFLINE layer
  - process passport extraction
  - deterministic formatting

- API layer
  - diagnosis generation
  - final report generation

- Reviewer layer
  - style normalization
  - heading normalization
  - artifact removal
  - retry if output is broken

## UI

Streamlit interface:

- left column — OFFLINE passport
- right column — API audit report
- fixed-height containers
- markdown rendering
- report export (.md)
