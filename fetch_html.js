// fetch_html.js
const puppeteer = require('puppeteer');


const url = process.argv[2];
console.log(`Node process started with URL: ${url}`);

if (!url) {
  console.error(JSON.stringify({ url: null, status: 0, html: null, error: "Missing URL argument" }));
  process.exit(1);
}

(async () => {
  try {
    const browser = await puppeteer.launch({
      headless: true,
      args: ['--no-sandbox']
    });

    const page = await browser.newPage();
    await page.setUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36");
    const response = await page.goto(url, { waitUntil: 'networkidle2' , timeout:20000});

    const html = await page.content();
    const status = response ? response.status() : 0;

    console.log(`Fetched ${url} with status ${status}`);

    await browser.close();

    process.stdout.write(JSON.stringify({
      url,
      status,
      html,
      error: null
    }));
  } catch (err) {
    process.stdout.write(JSON.stringify({
      url,
      status: 0,
      html: null,
      error: err.message
    }));
  }
})();
