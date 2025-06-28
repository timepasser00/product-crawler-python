import subprocess
import asyncio

def _run_puppeteer_sync(url: str) -> dict:
    try:
        result = subprocess.run(
            ['node', 'puppeteer_fetcher.js', url],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return {
                "html": result.stdout,
                "status": 200,
                "url": url
            }
        else:
            return {
                "html": "",
                "status": None,
                "url": url
            }
    except subprocess.TimeoutExpired:
        print("Puppeteer request timed out.")
        return {
            "html": "",
            "status": None,
            "url": url
        }

async def fetch_html_with_puppeteer(url: str) -> dict:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _run_puppeteer_sync, url)
