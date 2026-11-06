"""Local-first ingestion pipeline with in-memory job tracking.

Designed so the FastAPI surface works without RabbitMQ/Qdrant for demos,
while remaining structured for Celery/Qdrant wiring in production.
"""
from __future__ import annotations

import hashlib
import io
import uuid
from datetime import datetime, timezone
from typing import Any

from app.config import settings

_JOBS: dict[str, dict[str, Any]] = {}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _extract_text(filename: str, payload: bytes) -> str:
    lower = filename.lower()
    if lower.endswith(".txt") or lower.endswith(".md") or lower.endswith(".html") or lower.endswith(".csv"):
        return payload.decode("utf-8", errors="ignore")
    if lower.endswith(".pdf"):
        try:
            import fitz  # PyMuPDF

            doc = fitz.open(stream=payload, filetype="pdf")
            return "\n".join(page.get_text() for page in doc)
        except Exception:
            return payload.decode("utf-8", errors="ignore")
    return payload.decode("utf-8", errors="ignore")


def _chunk_text(text: str) -> list[str]:
    size = settings.chunk_size
    overlap = settings.chunk_overlap
    text = " ".join(text.split())
    if not text:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + size)
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks


def enqueue_document(filename: str, payload: bytes) -> dict[str, Any]:
    job_id = str(uuid.uuid4())
    digest = hashlib.sha256(payload).hexdigest()
    job = {
        "job_id": job_id,
        "status": "queued",
        "filename": filename,
        "chunks": 0,
        "detail": "",
        "checksum": digest,
        "created_at": _now(),
        "updated_at": _now(),
        "_payload": payload,
    }
    _JOBS[job_id] = job
    # Process inline for local demos; swap to Celery task in distributed mode.
    process_job(job_id)
    return {k: v for k, v in job.items() if not k.startswith("_")}


def process_job(job_id: str) -> dict[str, Any]:
    job = _JOBS[job_id]
    job["status"] = "processing"
    job["updated_at"] = _now()
    try:
        text = _extract_text(job["filename"], job["_payload"])
        chunks = _chunk_text(text)
        job["chunks"] = len(chunks)
        job["status"] = "completed"
        job["detail"] = f"ingested {len(chunks)} chunks"
        job["chunk_preview"] = chunks[:3]
    except Exception as exc:  # noqa: BLE001 - surface failure on job record
        job["status"] = "failed"
        job["detail"] = str(exc)
    job["updated_at"] = _now()
    job.pop("_payload", None)
    return {k: v for k, v in job.items() if not k.startswith("_")}


def get_job_status(job_id: str) -> dict[str, Any] | None:
    job = _JOBS.get(job_id)
    if not job:
        return None
    return {k: v for k, v in job.items() if not k.startswith("_") and k != "chunk_preview"}


def list_recent_jobs(limit: int = 20) -> list[dict[str, Any]]:
    jobs = sorted(_JOBS.values(), key=lambda j: j.get("created_at", ""), reverse=True)
    return [
        {k: v for k, v in j.items() if not k.startswith("_") and k != "chunk_preview"}
        for j in jobs[:limit]
    ]
