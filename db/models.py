from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
import uuid


class Listing(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
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
    image_urls: list[str] = Field(default_factory=list)
    content_hash: str = ""
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class Alert(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    filters: dict
    created_at: datetime = Field(default_factory=datetime.utcnow)
