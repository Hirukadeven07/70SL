import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from google.cloud.firestore_v1 import Query as FSQuery
from google.cloud.firestore_v1.async_client import AsyncClient
from starlette.requests import Request

from api.db import get_firestore
from api.limiter import limiter
from api.schemas import ListingOut, ListingsPage

log = logging.getLogger(__name__)

router = APIRouter(prefix="/listings", tags=["listings"])

_SORT: dict[str, tuple[str, str]] = {
    "price_asc": ("price_lkr", FSQuery.ASCENDING),
    "price_desc": ("price_lkr", FSQuery.DESCENDING),
    "newest": ("scraped_at", FSQuery.DESCENDING),
}


def _doc_to_listing(doc) -> ListingOut:  # noqa: ANN001
    data = doc.to_dict() or {}
    data["id"] = doc.id
    return ListingOut.model_validate(data)


@router.get("", response_model=ListingsPage)
@limiter.limit("60/minute")
async def list_listings(
    request: Request,
    body_type: Optional[str] = None,
    make: Optional[str] = None,
    model: Optional[str] = None,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    price_min: Optional[int] = None,
    price_max: Optional[int] = None,
    district: Optional[str] = None,
    fuel_type: Optional[str] = None,
    transmission: Optional[str] = None,
    sort: str = Query("newest", pattern="^(price_asc|price_desc|newest)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: AsyncClient = Depends(get_firestore),
) -> ListingsPage:
    if (price_min is not None or price_max is not None) and (year_min is not None or year_max is not None):
        raise HTTPException(
            status_code=400,
            detail="Cannot filter by both price range and year range simultaneously; use one at a time.",
        )

    q = db.collection("listings").where("is_active", "==", True)

    if body_type:
        q = q.where("body_type", "==", body_type)
    if make:
        q = q.where("make", "==", make.lower())
    if model:
        q = q.where("model", "==", model.lower())
    if district:
        q = q.where("district", "==", district.lower())
    if fuel_type:
        q = q.where("fuel_type", "==", fuel_type)
    if transmission:
        q = q.where("transmission", "==", transmission)
    if price_min is not None:
        q = q.where("price_lkr", ">=", price_min)
    if price_max is not None:
        q = q.where("price_lkr", "<=", price_max)
    if year_min is not None:
        q = q.where("year", ">=", year_min)
    if year_max is not None:
        q = q.where("year", "<=", year_max)

    sort_field, sort_dir = _SORT[sort]
    q = q.order_by(sort_field, direction=sort_dir)

    try:
        count_result = await q.count().get()
        total: int = count_result[0][0].value

        docs = await q.offset((page - 1) * page_size).limit(page_size).get()
        items = [_doc_to_listing(d) for d in docs]
    except Exception as exc:
        log.exception("Firestore query failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Database error: {exc}") from exc

    return ListingsPage(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=-(-total // page_size),
    )


@router.get("/{listing_id}", response_model=ListingOut)
@limiter.limit("120/minute")
async def get_listing(
    request: Request,
    listing_id: str,
    db: AsyncClient = Depends(get_firestore),
) -> ListingOut:
    doc = await db.collection("listings").document(listing_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Listing not found")
    data = doc.to_dict() or {}
    if not data.get("is_active"):
        raise HTTPException(status_code=404, detail="Listing not found")
    return _doc_to_listing(doc)


@router.get("/{listing_id}/similar", response_model=list[ListingOut])
@limiter.limit("60/minute")
async def get_similar(
    request: Request,
    listing_id: str,
    db: AsyncClient = Depends(get_firestore),
) -> list[ListingOut]:
    doc = await db.collection("listings").document(listing_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Listing not found")

    data = doc.to_dict() or {}
    q = db.collection("listings").where("is_active", "==", True)

    if data.get("body_type"):
        q = q.where("body_type", "==", data["body_type"])
    if data.get("make"):
        q = q.where("make", "==", data["make"])

    q = q.order_by("scraped_at", direction=FSQuery.DESCENDING).limit(6)
    docs = await q.get()

    return [_doc_to_listing(d) for d in docs if d.id != listing_id][:5]
