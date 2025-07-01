import asyncio
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import random
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

class AsyncFetcher:
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/112.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Firefox/113.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    ]

    def __init__(self):
        pass

    def __fetch_with_selenium_sync(self, url: str) -> dict:
        options = Options()
        options.headless = True
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--user-agent=' + random.choice(self.USER_AGENTS))

        try:
            # driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
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


    async def __fetch_html_with_selenium(self, url: str) -> dict:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.__fetch_with_selenium_sync, url)

    async def smart_fetch_html(self, url: str):
        result = await self.__fetch_html_with_selenium(url)
        return result