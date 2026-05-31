from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ListingOut(BaseModel):
    id: str
    source: str
    source_url: str
    title: str
    body_type: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    price_lkr: Optional[int] = None
    mileage_km: Optional[int] = None
    fuel_type: Optional[str] = None
    transmission: Optional[str] = None
    district: Optional[str] = None
    description: Optional[str] = None
    image_urls: list[str] = []
    scraped_at: datetime
    updated_at: datetime
    is_active: bool


class ListingsPage(BaseModel):
    items: list[ListingOut]
    total: int
    page: int
    page_size: int
    pages: int


class AlertCreate(BaseModel):
    email: EmailStr
    filters: dict


class AlertOut(BaseModel):
    id: str
    email: str
    filters: dict
    created_at: datetime
