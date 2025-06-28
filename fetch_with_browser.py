from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin

async def fetch_with_browser(url: str, base_url: str = "") -> dict:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        try:
            await page.goto(url, timeout=15000, wait_until='networkidle')
            html = await page.content()
        except Exception as e:
            html = ""
        await browser.close()

        return {
            "html": html,
            "status": 200 if html else None,
            "url": url
        }
