from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="Scalable RAG Ingestion Pipeline",
    description="Async document ingest API for Retrieval-Augmented Generation systems.",
    version="0.1.0",
)
app.include_router(router)
