import hashlib
from datetime import datetime, timezone

from google.cloud.firestore_v1.async_client import AsyncClient


def compute_content_hash(title: str, price_lkr: int | None, mileage_km: int | None) -> str:
    raw = title + str(price_lkr or "") + str(mileage_km or "")
    return hashlib.sha256(raw.encode()).hexdigest()


def doc_id_from_url(url: str) -> str:
    """Stable Firestore document ID derived from the listing's source URL."""
    return hashlib.md5(url.encode()).hexdigest()


async def upsert_listing(db: AsyncClient, data: dict) -> str:
    """
    Insert or update a listing document in Firestore.
    Returns 'inserted', 'updated', or 'skipped'.
    """
    content_hash = compute_content_hash(
        data["title"], data.get("price_lkr"), data.get("mileage_km")
    )
    data = {**data, "content_hash": content_hash}

    doc_id = doc_id_from_url(data["source_url"])
    doc_ref = db.collection("listings").document(doc_id)
    doc = await doc_ref.get()

    now = datetime.now(timezone.utc)

    if not doc.exists:
        await doc_ref.set({**data, "scraped_at": now, "updated_at": now, "is_active": True})
        return "inserted"

    existing = doc.to_dict() or {}
    if existing.get("content_hash") == content_hash:
        return "skipped"

    await doc_ref.update({**data, "updated_at": now})
    return "updated"
