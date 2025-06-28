// puppeteer_fetcher.js
const puppeteer = require('puppeteer');

const url = process.argv[2]; // Get URL from command-line argument

(async () => {
  try {
    const browser = await puppeteer.launch({ headless: true, args: ['--no-sandbox'] });
    const page = await browser.newPage();
    await page.setUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36");
    await page.goto(url, { waitUntil: 'networkidle2', timeout: 20000 });

    const htmlContent = await page.content();
    process.stdout.write(htmlContent);
    await browser.close();
  } catch (err) {
    process.exit(1);
  }
})();
