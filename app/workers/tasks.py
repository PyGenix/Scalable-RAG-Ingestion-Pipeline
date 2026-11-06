"""Celery task stubs for distributed ingestion."""
from app.ingestion.pipeline import process_job


def ingest_document_task(job_id: str) -> dict:
    return process_job(job_id)
