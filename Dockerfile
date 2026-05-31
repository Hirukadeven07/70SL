FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONPATH=/app

WORKDIR /app

RUN pip install --no-cache-dir \
    "firebase-admin>=6.5" \
    "google-cloud-storage>=2.16" \
    "fastapi>=0.111" \
    "uvicorn[standard]>=0.30" \
    "pydantic[email]>=2.7" \
    "slowapi>=0.1.9" \
    "httpx>=0.27" \
    "beautifulsoup4>=4.12" \
    "lxml>=5.2" \
    "python-dotenv>=1.0" \
    "tenacity>=8.3"

COPY . .
