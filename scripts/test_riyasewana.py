"""Quick local test — fetches a few URLs and parses one listing."""
import asyncio
import json
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)


async def main() -> None:
    from scraper.workers.riyasewana import RiyasewanaScraper

    async with RiyasewanaScraper() as scraper:
        log.info("Fetching listing URLs (first page only)…")
        urls = await scraper.fetch_listing_urls()
        log.info("Found %d URLs", len(urls))
        for u in urls[:5]:
            print(" ", u)

        if not urls:
            log.warning("No URLs found — check selectors in fetch_listing_urls()")
            return

        log.info("\nParsing first listing: %s", urls[0])
        result = await scraper.parse_listing(urls[0], "")
        if result is None:
            log.warning("parse_listing returned None — listing filtered out by _is_relevant()")
        else:
            print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
