# scraper.py

import asyncio
import re
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from apify_fetcher import fetch_top_videos_from_apify

async def scrape_tiktok_sound_async(sound_url):
    async with async_playwright() as p:
        iphone = p.devices["iPhone 13 Pro"]
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(**iphone)
        page = await context.new_page()

        try:
            await page.goto(sound_url, timeout=60000)
            await page.wait_for_timeout(8000)

            # Dismiss popups
            for text in ["Accept", "×"]:
                try:
                    button = page.locator(f"button:has-text('{text}')").first
                    if await button.is_visible():
                        await button.click()
                        await page.wait_for_timeout(1000)
                except:
                    pass

            # Extract title
            try:
                title = await page.locator("h1").first.inner_text()
                if not title.strip():
                    raise ValueError("Empty h1")
            except:
                title = await page.title() or "Title not found"

            # Extract UGC count
            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text()

            match_ugc = re.search(r"([\d\.]+)([KM]?)\s+videos", text)
            if match_ugc:
                num = float(match_ugc.group(1))
                suffix = match_ugc.group(2)
                multiplier = {"K": 1_000, "M": 1_000_000}.get(suffix, 1)
                ugc_count = int(num * multiplier)
            else:
                ugc_count = None

            return {
                "title": title,
                "ugc_count": ugc_count
            }

        except Exception as e:
            return {
                "title": "Error",
                "ugc_count": None,
                "error": str(e)
            }

        finally:
            await context.close()
            await browser.close()

# Sync wrapper for Flask
def scrape_tiktok_sound(sound_url):
    return asyncio.run(scrape_tiktok_sound_async(sound_url))
