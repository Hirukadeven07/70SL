import os
from urllib.parse import urlparse

import httpx

_gcs_client = None


def _get_client():
    global _gcs_client
    if _gcs_client is None:
        from google.cloud import storage as gcs
        _gcs_client = gcs.Client()
    return _gcs_client


async def store_images(image_urls: list[str], listing_id: str) -> list[str]:
    """
    Download source images and upload to Firebase/GCS Storage.
    Falls back to the original URL if FIREBASE_STORAGE_BUCKET is not configured
    or if an individual upload fails.
    """
    bucket_name = os.getenv("FIREBASE_STORAGE_BUCKET")
    if not bucket_name:
        return image_urls

    try:
        bucket = _get_client().bucket(bucket_name)
    except Exception:
        return image_urls

    stored: list[str] = []
    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as http:
        for i, url in enumerate(image_urls):
            try:
                resp = await http.get(url)
                resp.raise_for_status()
                ext = _ext_from_url(url)
                blob = bucket.blob(f"listings/{listing_id}/{i}{ext}")
                blob.upload_from_string(
                    resp.content,
                    content_type=resp.headers.get("content-type", "image/jpeg"),
                )
                blob.make_public()
                stored.append(blob.public_url)
            except Exception:
                stored.append(url)

    return stored


def _ext_from_url(url: str) -> str:
    path = urlparse(url).path.lower()
    for ext in (".jpg", ".jpeg", ".png", ".webp"):
        if path.endswith(ext):
            return ext
    return ".jpg"
