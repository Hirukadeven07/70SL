FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

WORKDIR /app

RUN pip install --no-cache-dir \
    "firebase-admin>=6.5" \
    "google-cloud-storage>=2.16" \
    "httpx>=0.27" \
    "beautifulsoup4>=4.12" \
    "lxml>=5.2" \
    "python-dotenv>=1.0" \
    "tenacity>=8.3"

RUN playwright install chromium --with-deps

COPY scraper/ scraper/
COPY db/ db/
COPY api/ api/

ENV PYTHONPATH=/app

ENTRYPOINT ["python", "-m", "scraper.main"]
