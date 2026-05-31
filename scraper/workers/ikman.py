import asyncio
import re

from scraper.workers.base import BaseScraper

_CATEGORY = (
    "https://www.ikman.lk/en/ads/sri-lanka/vehicles/cars"
    "?filter.category.slug=jeeps-suvs-vans"
)

_KEYWORDS = frozenset(
    [
        "4x4", "4wd", "awd", "double cab", "double-cab", "pickup",
        "hilux", "ranger", "d-max", "triton", "navara",
        "fortuner", "prado", "landcruiser", "pajero", "montero", "surf",
    ]
)


class IkmanScraper(BaseScraper):
    source = "ikman"
    base_url = "https://www.ikman.lk"

    async def fetch_listing_urls(self) -> list[str]:
        urls: list[str] = []
        page = await self._new_page()
        page_num = 1

        while True:
            await asyncio.sleep(3)
            await page.goto(f"{_CATEGORY}&page={page_num}", wait_until="domcontentloaded")
            links = await page.query_selector_all("a[data-testid='ad-card-link']")
            if not links:
                # Try alternative selector pattern
                links = await page.query_selector_all("a.sl-card-link, a[href*='/en/ad/']")
            hrefs = [await lnk.get_attribute("href") for lnk in links]
            hrefs = [h for h in hrefs if h and "/en/ad/" in h]
            if not hrefs:
                break
            urls.extend(
                f"{self.base_url}{h}" if h.startswith("/") else h for h in hrefs
            )
            page_num += 1

        await page.close()
        return list(dict.fromkeys(urls))  # deduplicate while preserving order

    async def parse_listing(self, url: str, html: str) -> dict | None:
        page = await self._new_page()
        try:
            await asyncio.sleep(3)
            await page.goto(url, wait_until="networkidle")

            title_el = await page.query_selector("h1[class*='title']")
            title = (await title_el.inner_text()).strip() if title_el else ""
            if not title or not _is_relevant(title):
                return None

            price_el = await page.query_selector("[class*='price']")
            price_lkr = _parse_price(await price_el.inner_text()) if price_el else None

            desc_el = await page.query_selector("[class*='description']")
            description = (await desc_el.inner_text()).strip() if desc_el else None

            images = await page.query_selector_all("img[class*='image']")
            image_urls = [
                src
                for img in images
                if (src := await img.get_attribute("src"))
            ]

            details: dict[str, str] = {}
            for item in await page.query_selector_all("li[class*='item']"):
                key_el = await item.query_selector("[class*='key']")
                val_el = await item.query_selector("[class*='value']")
                if key_el and val_el:
                    k = (await key_el.inner_text()).strip().lower()
                    v = (await val_el.inner_text()).strip()
                    details[k] = v

            district_el = await page.query_selector("[class*='location']")
            district = (await district_el.inner_text()).strip().lower() if district_el else None

        finally:
            await page.close()

        return {
            "source": self.source,
            "source_url": url,
            "title": title,
            "body_type": _infer_body_type(title, details),
            "make": details.get("make", "").strip().lower() or None,
            "model": details.get("model", "").strip().lower() or None,
            "year": _parse_year(details.get("year of manufacture", "")),
            "price_lkr": price_lkr,
            "mileage_km": _parse_mileage(details.get("mileage", "")),
            "fuel_type": _normalise_fuel(details.get("fuel type", "")),
            "transmission": _normalise_transmission(details.get("transmission", "")),
            "district": district,
            "description": description,
            "image_urls": image_urls,
        }


def _is_relevant(title: str) -> bool:
    lower = title.lower()
    return any(kw in lower for kw in _KEYWORDS)


def _parse_price(raw: str) -> int | None:
    digits = re.sub(r"[^\d]", "", raw)
    return int(digits) if digits else None


def _parse_year(raw: str) -> int | None:
    m = re.search(r"\b(19|20)\d{2}\b", raw)
    return int(m.group()) if m else None


def _parse_mileage(raw: str) -> int | None:
    raw = raw.lower().replace(",", "")
    m = re.search(r"(\d+\.?\d*)\s*k", raw)
    if m:
        return int(float(m.group(1)) * 1000)
    m = re.search(r"(\d+)", raw)
    return int(m.group(1)) if m else None


def _normalise_fuel(raw: str) -> str | None:
    raw = raw.lower()
    if "petrol" in raw or "gasoline" in raw:
        return "petrol"
    if "diesel" in raw:
        return "diesel"
    if "hybrid" in raw:
        return "hybrid"
    return None


def _normalise_transmission(raw: str) -> str | None:
    raw = raw.lower()
    if "auto" in raw:
        return "automatic"
    if "manual" in raw:
        return "manual"
    return None


def _infer_body_type(title: str, details: dict[str, str]) -> str | None:
    lower = title.lower()
    body = details.get("body type", "").lower()
    if "double cab" in lower or "double-cab" in lower or "pickup" in lower:
        return "double_cab"
    if "4x4" in lower or "4wd" in lower or "awd" in lower:
        return "4x4"
    if "suv" in body or "jeep" in body:
        return "suv"
    return None
