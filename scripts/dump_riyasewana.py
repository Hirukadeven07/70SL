"""Dump the raw HTML of the riyasewana search page so we can inspect selectors."""
import asyncio
from playwright.async_api import async_playwright

URL = "https://riyasewana.com/search/jeep"

async def main() -> None:
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        ctx = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )
        page = await ctx.new_page()
        await page.goto(URL, wait_until="domcontentloaded")
        await asyncio.sleep(3)

        # Print all anchor hrefs containing a number (potential listing links)
        links = await page.query_selector_all("a[href]")
        print(f"Total anchors: {len(links)}")
        for lnk in links[:80]:
            href = await lnk.get_attribute("href") or ""
            text = (await lnk.inner_text()).strip()[:60]
            if href:
                print(f"  {href!r:70s}  |  {text!r}")

        # Dump a snippet of the HTML around listing cards
        html = await page.content()
        with open("riyasewana_dump.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\nFull HTML saved to riyasewana_dump.html ({len(html)} chars)")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
