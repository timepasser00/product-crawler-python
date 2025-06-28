import asyncio
import json
import subprocess
import httpx
import random
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from typing import Optional

USER_AGENTS = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
]

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/112.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Firefox/113.0",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
# ]


TIMEOUT = httpx.Timeout(None, connect=5.0)

HEADERS_BASE = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive"
}

@retry(
    stop=stop_after_attempt(3),
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

            return {
                "url": str(response.url),
                "status": response.status_code,
                "html": response.text,
                "error": None
            }

        except httpx.RequestError as e:
            return {
                "url": url,
                "status": None,
                "html": None,
                "error": f"Request error: {str(e)}"
            }

async def fetch_html_with_node_async(url: str) -> dict:
    try:
        print(f"creating node process")
        process = await asyncio.create_subprocess_exec(
            'node', 'fetch_html.js', url,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            return json.loads(stdout.decode())
        else:
            return {
                "url": url,
                "status": 0,
                "html": None,
                "error": stderr.decode().strip()
            }

    except Exception as e:
        return {
            "url": url,
            "status": 0,
            "html": None,
            "error": str(e)
        }

def fetch_html_with_node(url: str) -> str:
    try:
        result = subprocess.run(
            ['node', 'fetch_html.js', url],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"[!] Node script error: {result.stderr}")
    except Exception as e:
        print(f"[!] Failed to fetch HTML: {e}")
    return ""

async def smart_fetch_html(url: str):
    result = await fetch_static(url)
    if result["status"] == 200 and result["html"].strip():
        return result
    print(f"Trying to fetch with Node for {url} due to static fetch failure.")
    result = await fetch_html_with_node_async(url)
    return result