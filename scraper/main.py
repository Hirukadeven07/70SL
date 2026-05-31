"""
Scraper entrypoint — Cloud Run Job or standalone script.

Usage:
  python -m scraper.main [--source ikman|riyasewana|sarathiads]

When no --source is given all registered scrapers run sequentially.
Cloud Scheduler triggers this job on a cron schedule in production.
"""
import argparse
import asyncio
import logging

from dotenv import load_dotenv

load_dotenv()

from db.firestore_client import get_db  # noqa: E402
from scraper.pipeline.dedup import doc_id_from_url, upsert_listing
from scraper.pipeline.image_store import store_images
from scraper.pipeline.normalise import normalise_listing
from scraper.workers.ikman import IkmanScraper
from scraper.workers.riyasewana import RiyasewanaScraper
from scraper.workers.sarathiads import SarathiadsScraper

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger(__name__)

_SCRAPERS = {
    "ikman": IkmanScraper,
    "riyasewana": RiyasewanaScraper,
    "sarathiads": SarathiadsScraper,
}


async def run_scraper(source: str) -> None:
    db = get_db()
    scraper_cls = _SCRAPERS[source]
    log.info("Starting %s scraper", source)

    async with scraper_cls() as scraper:
        urls = await scraper.fetch_listing_urls()
        log.info("%s: found %d listing URLs", source, len(urls))

        for url in urls:
            try:
                raw = await scraper.parse_listing(url, "")
                if raw is None:
                    log.debug("skip (not relevant): %s", url)
                    continue

                normalised = normalise_listing(raw)

                if normalised.get("image_urls"):
                    listing_id = doc_id_from_url(url)
                    normalised["image_urls"] = await store_images(
                        normalised["image_urls"], listing_id
                    )

                status = await upsert_listing(db, normalised)
                log.info("%s [%s] %s", source, status, url)

            except Exception:
                log.exception("Error processing %s", url)


async def main() -> None:
    parser = argparse.ArgumentParser(description="Run Sri Lanka 4x4 scrapers")
    parser.add_argument("--source", choices=list(_SCRAPERS), default=None)
    args = parser.parse_args()

    sources = [args.source] if args.source else list(_SCRAPERS)
    for source in sources:
        await run_scraper(source)


if __name__ == "__main__":
    asyncio.run(main())
