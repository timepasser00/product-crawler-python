import asyncio
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import httpx
import random
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/112.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Firefox/113.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
]


TIMEOUT = httpx.Timeout(None, connect=5.0)

HEADERS_BASE = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive"
}

@retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException))
)
async def fetch_static(url: str) -> dict:
    headers = HEADERS_BASE.copy()
    headers["User-Agent"] = random.choice(USER_AGENTS)

    async with httpx.AsyncClient(http2=True, timeout=TIMEOUT, follow_redirects=True) as client:
        try:
            response = await client.get(url, headers=headers)

            content_type = response.headers.get("content-type", "")
            if "text/html" not in content_type:
                return {
                    "url": str(response.url),
                    "status": response.status_code,
                    "html": None,
                    "error": "Non-HTML content"
                }
            soup = BeautifulSoup(response.text, "html.parser")
            return {
                "url": str(response.url),
                "status": response.status_code,
                "html": soup.prettify() if soup else None,
                "error": None
            }

        except httpx.RequestError as e:
            return {
                "url": url,
                "status": None,
                "html": None,
                "error": f"Request error: {str(e)}"
            }

def _fetch_with_selenium_sync(url: str) -> dict:
    options = Options()
    options.headless = True
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--user-agent=' + random.choice(USER_AGENTS))

    try:
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(20)
        driver.get(url)

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")
        driver.quit()
        return {"url": url, "html": soup.prettify(), "status": 200}
    except Exception as e:
        return {"url": url, "html": "", "status": None}
    
async def fetch_html_with_selenium(url: str) -> dict:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _fetch_with_selenium_sync, url)


async def smart_fetch_html(url: str):
    result = await fetch_static(url)
    if result["status"] == 200 and result["html"].strip():
        return result
    result = await fetch_html_with_selenium(url)
    return result