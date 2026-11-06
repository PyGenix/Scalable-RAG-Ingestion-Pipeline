# Scalable RAG Ingestion Pipeline

Python FastAPI service focused on reliable document ingestion for Retrieval-Augmented Generation (RAG).

Accepts documents over REST, extracts text, chunks content, tracks job status, and is structured for Celery workers + Qdrant vector storage in distributed deployments.

## Stack

- **API:** Python 3.11+, FastAPI, Uvicorn
- **Processing:** PyMuPDF text extraction, configurable chunking
- **Async path:** Celery + RabbitMQ (optional)
- **Vector store target:** Qdrant
- **Metadata DB target:** PostgreSQL

## Features

- `POST /ingest` multipart document upload
- Job status endpoints for observability
- Idempotent checksum tracking per upload
- Local in-process mode for quick demos without the full broker stack

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

## Author

Pooja Sharma — [Pooja101117](https://github.com/Pooja101117)
