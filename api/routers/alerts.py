import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from google.cloud.firestore_v1.async_client import AsyncClient
from starlette.requests import Request

from api.db import get_firestore
from api.limiter import limiter
from api.schemas import AlertCreate, AlertOut

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.post("", response_model=AlertOut, status_code=201)
@limiter.limit("5/minute")
async def create_alert(
    request: Request,
    body: AlertCreate,
    db: AsyncClient = Depends(get_firestore),
) -> AlertOut:
    alert_id = str(uuid.uuid4())
    created_at = datetime.utcnow()
    await db.collection("alerts").document(alert_id).set(
        {"email": body.email, "filters": body.filters, "created_at": created_at}
    )
    return AlertOut(id=alert_id, email=body.email, filters=body.filters, created_at=created_at)


@router.delete("/{alert_id}", status_code=204)
@limiter.limit("10/minute")
async def delete_alert(
    request: Request,
    alert_id: str,
    db: AsyncClient = Depends(get_firestore),
) -> None:
    doc_ref = db.collection("alerts").document(alert_id)
    doc = await doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Alert not found")
    await doc_ref.delete()
