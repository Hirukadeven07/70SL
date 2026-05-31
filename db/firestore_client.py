import os
from functools import lru_cache
import firebase_admin
from firebase_admin import credentials, firestore_async
from google.cloud.firestore_v1.async_client import AsyncClient


@lru_cache(maxsize=1)
def _init_app() -> firebase_admin.App:
    import base64
    import json

    cred_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    if cred_json:
        cred_dict = json.loads(base64.b64decode(cred_json))
        return firebase_admin.initialize_app(credentials.Certificate(cred_dict))

    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if cred_path:
        return firebase_admin.initialize_app(credentials.Certificate(cred_path))

    return firebase_admin.initialize_app()


def get_db() -> AsyncClient:
    _init_app()
    return firestore_async.client()
