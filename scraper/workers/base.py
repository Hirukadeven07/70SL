from abc import ABC, abstractmethod

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

# ── Title relevance filter (shared by all scrapers) ───────────────────────────

_INCLUDE = frozenset([
    "4x4", "4wd", "awd", "double cab", "double-cab", "pickup",
    "hilux", "ranger", "d-max", "triton", "navara",
    "fortuner", "prado", "land cruiser", "landcruiser", "pajero", "montero", "surf",
    "jeep", "suv",
])

# Any of these in the title → not a vehicle-for-sale listing
_EXCLUDE = frozenset([
    # Parts & accessories
    "lamp", " light", "grille", "grill", "body kit", "conversion kit",
    "side step", "wheel arch", "wheel cover", "clutch kit", "air filter",
    "shock absorber", "spare part", "used part", "for parts",
    # Rentals & hire
    "rent a car", "for rent", "for hire", "wedding car", "car hire",
    # Finance/leasing-only ads
    "easy leasing", "easy loan",
])


def is_relevant_title(title: str) -> bool:
    """Return True only if the title suggests a 4x4/double-cab vehicle for sale."""
    lower = title.lower()
    if any(ex in lower for ex in _EXCLUDE):
        return False
    return any(kw in lower for kw in _INCLUDE)


_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

RATE_LIMITS: dict[str, dict[str, int]] = {
    "ikman":      {"delay_s": 3, "concurrency": 2},
    "riyasewana": {"delay_s": 4, "concurrency": 1},
    "sarathiads": {"delay_s": 3, "concurrency": 2},
}


class BaseScraper(ABC):
    source: str
    base_url: str

    def __init__(self) -> None:
        self._browser: Browser | None = None
        self._ctx: BrowserContext | None = None
        self.delay_s: int = RATE_LIMITS.get(self.source, {"delay_s": 3})["delay_s"]

    async def __aenter__(self) -> "BaseScraper":
        self._pw = await async_playwright().start()
        self._browser = await self._pw.chromium.launch(headless=True)
        self._ctx = await self._browser.new_context(
            user_agent=_UA,
            extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
        )
        return self

    async def __aexit__(self, *args: object) -> None:
        if self._ctx:
            await self._ctx.close()
        if self._browser:
            await self._browser.close()
        await self._pw.stop()

    async def _new_page(self) -> Page:
        assert self._ctx is not None
        return await self._ctx.new_page()

    @abstractmethod
    async def fetch_listing_urls(self) -> list[str]:
        """Return all listing URLs from search/category pages."""
        ...

    @abstractmethod
    async def parse_listing(self, url: str, html: str) -> dict | None:
        """
        Parse a single listing page.
        Return None to skip (listing is not a 4x4 / double-cab).
        """
        ...
