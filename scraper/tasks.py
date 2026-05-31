"""
Celery task stubs — not used in the Firebase/Cloud Run architecture.

Scheduling is handled by Cloud Scheduler triggering the Cloud Run Job
defined in scraper/Dockerfile (entry point: python -m scraper.main).

To run a scrape manually:
    python -m scraper.main --source ikman
    python -m scraper.main --source riyasewana
    python -m scraper.main --source sarathiads
    python -m scraper.main            # all sources
"""
