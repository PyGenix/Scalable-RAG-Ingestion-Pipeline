from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.ingestion.pipeline import enqueue_document, get_job_status, list_recent_jobs

router = APIRouter()


class IngestResponse(BaseModel):
    job_id: str
    status: str
    filename: str


class JobStatus(BaseModel):
    job_id: str
    status: str
    filename: str
    chunks: int = 0
    detail: str = ""


@router.get("/health")
def health():
    return {"status": "ok", "service": "scalable-rag-ingestion"}


@router.post("/ingest", response_model=IngestResponse)
async def ingest(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="filename required")
    payload = await file.read()
    if not payload:
        raise HTTPException(status_code=400, detail="empty file")
    job = enqueue_document(file.filename, payload)
    return IngestResponse(job_id=job["job_id"], status=job["status"], filename=job["filename"])


@router.get("/jobs/{job_id}", response_model=JobStatus)
def job_status(job_id: str):
    job = get_job_status(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    return JobStatus(**job)


@router.get("/jobs", response_model=list[JobStatus])
def jobs(limit: int = Field(default=20, ge=1, le=100)):
    return [JobStatus(**j) for j in list_recent_jobs(limit)]
