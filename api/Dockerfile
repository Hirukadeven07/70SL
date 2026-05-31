FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    "firebase-admin>=6.5" \
    "fastapi>=0.111" \
    "uvicorn[standard]>=0.30" \
    "pydantic[email]>=2.7" \
    "slowapi>=0.1.9" \
    "python-dotenv>=1.0"

COPY api/ api/
COPY db/ db/

EXPOSE 8000
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
