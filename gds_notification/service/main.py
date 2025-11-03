from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
import hashlib
import uuid

app = FastAPI(title="GDS Notification Ingest (PoC)")


class IngestAlert(BaseModel):
    message_id: Optional[str] = None
    alert_name: str
    db_instance_id: Optional[int] = None
    subject: Optional[str] = None
    body_text: Optional[str] = None
    body_html: Optional[str] = None


def compute_idempotency_id(payload: IngestAlert) -> str:
    if payload.message_id:
        return payload.message_id
    hash_input = (payload.alert_name or "") + (payload.subject or "") + (payload.body_text or "")
    return hashlib.sha256(hash_input.encode('utf-8')).hexdigest()


@app.post('/ingest')
async def ingest(alert: IngestAlert, request: Request):
    idempotency_id = compute_idempotency_id(alert)
    # For PoC we don't persist yet. In a real implementation, persist the alert and enqueue a job.
    job_id = str(uuid.uuid4())
    return {"status": "accepted", "job_id": job_id, "idempotency_id": idempotency_id}


@app.get('/health')
async def health():
    return {"status": "ok"}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
