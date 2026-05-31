from db.firestore_client import get_db
from google.cloud.firestore_v1.async_client import AsyncClient


def get_firestore() -> AsyncClient:
    return get_db()
