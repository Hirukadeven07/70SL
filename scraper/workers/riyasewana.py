import asyncio
import re

from scraper.workers.base import BaseScraper

# Category pages for 4x4 / double-cab / SUV vehicles
_SEARCH_URLS = [
    "https://riyasewana.com/search/jeep",
    "https://riyasewana.com/search/suvs",
    "https://riyasewana.com/search/pickups",
]

_KEYWORDS = frozenset([
    "4x4", "4wd", "awd", "double cab", "double-cab", "pickup",
    "hilux", "ranger", "d-max", "triton", "navara",
    "fortuner", "prado", "landcruiser", "pajero", "montero", "surf",
    "jeep", "suv",
])


class RiyasewanaScraper(BaseScraper):
    source = "riyasewana"
    base_url = "https://riyasewana.com"

    async def fetch_listing_urls(self) -> list[str]:
        urls: list[str] = []

        for search_url in _SEARCH_URLS:
            page_num = 1
            page = await self._new_page()
            try:
                while True:
                    await asyncio.sleep(self.delay_s)
                    paginated = f"{search_url}?page={page_num}" if page_num > 1 else search_url
                    await page.goto(paginated, wait_until="domcontentloaded")

                    # Detect rate-limit ban page
                    body_text = await page.evaluate("() => document.body.innerText")
                    if "Rate limit exceeded" in body_text or "Temporary ban" in body_text:
                        import logging
                        logging.getLogger(__name__).warning(
                            "riyasewana rate-limited on %s — skipping remaining pages", paginated
                        )
                        break

                    # Wait for listing cards to load
                    try:
                        await page.wait_for_selector("a[href*='/buy/']", timeout=8_000)
                    except Exception:
                        pass

                    # Collect listing links — all /buy/ anchors
                    links = await page.query_selector_all("a[href*='/buy/']")
                    hrefs_raw = [await lnk.get_attribute("href") for lnk in links]

                    hrefs = []
                    for h in hrefs_raw:
                        if not h:
                            continue
                        if h.startswith("//"):
                            h = "https:" + h
                        elif not h.startswith("http"):
                            h = self.base_url + h
                        if "/buy/" in h and h not in hrefs:
                            hrefs.append(h)

                    if not hrefs:
                        break

                    urls.extend(hrefs)
                    page_num += 1
            finally:
                await page.close()

        return list(dict.fromkeys(urls))

    async def parse_listing(self, url: str, html: str) -> dict | None:
        page = await self._new_page()
        try:
            await asyncio.sleep(self.delay_s)
            await page.goto(url, wait_until="domcontentloaded")

            title_el = await page.query_selector("h1")
            title = (await title_el.inner_text()).strip() if title_el else ""
            if not title or not _is_relevant(title):
                return None

            # Price — ".price-amount" contains the numeric value or "Negotiable"
            price_el = await page.query_selector(".price-amount")
            price_lkr = _parse_price(await price_el.inner_text()) if price_el else None

            # Detail fields — each row has .detail-label and .detail-value spans
            details: dict[str, str] = {}
            for row in await page.query_selector_all(".detail-row"):
                label_el = await row.query_selector(".detail-label")
                value_el = await row.query_selector(".detail-value")
                if label_el and value_el:
                    k = (await label_el.inner_text()).strip().lower().rstrip(":")
                    v = (await value_el.inner_text()).strip()
                    details[k] = v

            # Images — full-size URLs stored in data-full on thumbnail strip
            image_urls: list[str] = []
            for thumb in await page.query_selector_all(".dt-thumb[data-full]"):
                src = await thumb.get_attribute("data-full")
                if src and src.startswith("http"):
                    image_urls.append(src)
            # Fallback: main image
            if not image_urls:
                main_img = await page.query_selector("#mainImg")
                if main_img:
                    src = await main_img.get_attribute("src")
                    if src and src.startswith("http"):
                        image_urls.append(src)

            # District — stored as "Location" in the detail rows
            district = _clean(details.get("location"))

            # Description — inside .more-card-body (the "More Details" section)
            desc_el = await page.query_selector(".more-card-body")
            description = (await desc_el.inner_text()).strip()[:2000] if desc_el else None

        finally:
            await page.close()

        return {
            "source": self.source,
            "source_url": url,
            "title": title,
            "body_type": _infer_body_type(title, details),
            "make": _clean(details.get("make") or details.get("brand")),
            "model": _clean(details.get("model")),
            "year": _parse_year(details.get("year") or details.get("manufactured year")),
            "price_lkr": price_lkr,
            "mileage_km": _parse_mileage(details.get("mileage")),
            "fuel_type": _normalise_fuel(details.get("fuel type") or details.get("fuel")),
            "transmission": _normalise_transmission(details.get("gear") or details.get("transmission")),
            "district": district,
            "description": description,
            "image_urls": image_urls[:10],
        }


# ── helpers ───────────────────────────────────────────────────────────────────

def _is_relevant(title: str) -> bool:
    lower = title.lower()
    return any(kw in lower for kw in _KEYWORDS)


def _clean(value: str | None) -> str | None:
    return value.strip().lower() if value else None


def _parse_price(raw: str) -> int | None:
    digits = re.sub(r"[^\d]", "", raw)
    return int(digits) if digits else None


def _parse_year(raw: str | None) -> int | None:
    if not raw:
        return None
    m = re.search(r"\b(19|20)\d{2}\b", raw)
    return int(m.group()) if m else None


def _parse_mileage(raw: str | None) -> int | None:
    if not raw:
        return None
    text = raw.lower().replace(",", "")
    m = re.search(r"(\d+\.?\d*)\s*k(?!m)", text)
    if m:
        return int(float(m.group(1)) * 1000)
    m = re.search(r"(\d+)", text)
    return int(m.group(1)) if m else None


def _normalise_fuel(raw: str | None) -> str | None:
    if not raw:
        return None
    r = raw.lower()
    if "petrol" in r or "gasoline" in r:
        return "petrol"
    if "diesel" in r:
        return "diesel"
    if "hybrid" in r:
        return "hybrid"
    return None


def _normalise_transmission(raw: str | None) -> str | None:
    if not raw:
        return None
    r = raw.lower()
    if "auto" in r:
        return "automatic"
    if "manual" in r:
        return "manual"
    return None


def _infer_body_type(title: str, details: dict[str, str]) -> str | None:
    lower = title.lower()
    if "double cab" in lower or "double-cab" in lower or "pickup" in lower:
        return "double_cab"
    if "4x4" in lower or "4wd" in lower or "awd" in lower:
        return "4x4"
    body = details.get("body type", "").lower()
    if "suv" in body or "jeep" in body:
        return "suv"
    return None
