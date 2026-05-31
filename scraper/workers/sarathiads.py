import asyncio
import re

from scraper.workers.base import BaseScraper

_SEARCH_URLS = [
    "https://www.sarathiads.lk/vehicles/cars/jeep-suv-van",
    "https://www.sarathiads.lk/vehicles/cars/double-cab",
]

_KEYWORDS = frozenset([
    "4x4", "4wd", "awd", "double cab", "double-cab", "pickup",
    "hilux", "ranger", "d-max", "triton", "navara",
    "fortuner", "prado", "landcruiser", "pajero", "montero", "surf",
])


class SarathiadsScraper(BaseScraper):
    source = "sarathiads"
    base_url = "https://www.sarathiads.lk"

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

                    links = await page.query_selector_all(
                        ".ad-card a[href], .listing-card a[href], .item a[href]"
                    )
                    if not links:
                        links = await page.query_selector_all("a[href]")
                        links = [
                            lnk for lnk in links
                            if re.search(
                                r"/vehicles/|/cars/|/ad/|/listing/",
                                await lnk.get_attribute("href") or "",
                            )
                        ]

                    hrefs = [await lnk.get_attribute("href") for lnk in links]
                    hrefs = [
                        h if h.startswith("http") else self.base_url + h
                        for h in hrefs
                        if h and re.search(r"/\d+|/ad/|/listing/", h)
                    ]

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

            title_el = await page.query_selector("h1, .ad-title, .listing-title")
            title = (await title_el.inner_text()).strip() if title_el else ""
            if not title or not _is_relevant(title):
                return None

            price_el = await page.query_selector(".price, .ad-price, [class*='price']")
            price_lkr = _parse_price(await price_el.inner_text()) if price_el else None

            details: dict[str, str] = {}
            for row in await page.query_selector_all("table tr, .specs li, .detail-row, dl"):
                cells = await row.query_selector_all("td, dd, dt, span, p")
                if len(cells) >= 2:
                    k = (await cells[0].inner_text()).strip().lower().rstrip(":")
                    v = (await cells[1].inner_text()).strip()
                    details[k] = v

            image_urls: list[str] = []
            for img in await page.query_selector_all(".ad-images img, .gallery img, .slider img"):
                src = await img.get_attribute("src") or await img.get_attribute("data-src")
                if src and src.startswith("http"):
                    image_urls.append(src)

            loc_el = await page.query_selector(".location, .district, [class*='location']")
            district = (await loc_el.inner_text()).strip().lower() if loc_el else None

            desc_el = await page.query_selector(".description, .ad-description, #description")
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
            "year": _parse_year(details.get("year") or details.get("manufacture year")),
            "price_lkr": price_lkr,
            "mileage_km": _parse_mileage(details.get("mileage")),
            "fuel_type": _normalise_fuel(details.get("fuel type") or details.get("fuel")),
            "transmission": _normalise_transmission(details.get("transmission")),
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
    m = re.search(r"(\d+\.?\d*)\s*k", text)
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
