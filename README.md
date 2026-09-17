# Galaxy Autonomous Stateful Troubleshooting Engine (GASTE)

## Overview
GASTE is a local-first, deterministic, stateful troubleshooting engine designed for the Samsung PRISM GenAI Hackathon 3.0. It transforms unstructured customer complaints into machine-actionable troubleshooting plans with exact in-app Bixby deeplinks.

## Features
- **Semantic Retrieval**: Uses SentenceTransformers and FAISS for fast and accurate context retrieval.
- **Stateful Interactive Troubleshooting**: Tracks user progress and provides targeted steps based on failure reports.
- **Zero-LLM Extractive Synthesizer**: Uses deterministic logic instead of costly API calls to generate validated troubleshooting responses.
- **Deterministic Safety Sequencing**: Always suggests safe configuration steps before recommending manual or critical actions.
- **Guardrails**: Ensures all output complies with the strict Pydantic schemas, strips unwanted URLs, and accurately matches titles, goals, and descriptions.
- **Multimodal Intake**: Built-in support for OCR to parse troubleshooting texts from screenshots.
- **Fast-Path Semantic Caching**: Achieves sub-300ms latency on repeated queries.

## Architecture
- **Language**: Python 3.10+
- **Framework**: FastAPI
- **Validation**: Pydantic v2
- **Embeddings**: sentence-transformers
- **Vector Search**: FAISS
- **Database**: SQLite (for catalog & cache)

## How to Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the API server:
   ```bash
   uvicorn main:app --reload
   ```
3. Test endpoints:
   - `/health`
   - `/v1/troubleshoot`
   - `/v1/troubleshoot/interactive`
