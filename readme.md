# Powerful Product Url Crawler

## Overview
Powerful Crawler is an asynchronous web crawler designed to fetch and parse HTML content from websites and return the products url. 

## Features
- Fully asynchronous design using coroutines.
- Modular worker-based architecture.
- Fetcher Worker: Fetches HTML content for given URLs.
- Parser Worker: Parses HTML content and extracts child URLs.
- Frontier Queue: Manages URLs to be fetched.
- HTML Queue: Stores fetched HTML content for parsing.

## Architecture
Below is a visual representation of the components and their interactions:

```mermaid
    Start[Start Crawler] --> Seed[Seed URLs]
    Seed -->|Add to Frontier| FrontierQueue[Frontier Queue]
    FrontierQueue -->|URL| FetcherWorker[Fetcher Worker]
    FetcherWorker -->|HTML| HTMLQueue[HTML Queue]
    FetcherWorker -->|Retry with Selenium| SeleniumFetcher[Selenium Fetcher]
    HTMLQueue -->|HTML| ParserWorker[Parser Worker]
    ParserWorker -->|Analyze| ProductPageClassifier[Product Page Classifier]
    ParserWorker -->|Dead End Detection| ProductUrlAnalyzer[Product URL Analyzer]
    ProductPageClassifier -->|Is Product Page?| Output[Output Product URLs]
    ProductUrlAnalyzer -->|Dead End URLs| FrontierQueue
    ParserWorker -->|Child URLs| FrontierQueue
    End[End Crawler] <-- Output
```

### Component Details
1. **Frontier Queue**: Stores URLs to be fetched. Acts as the starting point for the crawler.
2. **Fetcher Worker**: Fetches HTML content for URLs from the Frontier Queue and adds it to the HTML Queue.
3. **HTML Queue**: Stores fetched HTML content temporarily for parsing.
4. **Parser Worker**: Parses HTML content from the HTML Queue and extracts child URLs to add back to the Frontier Queue.

# Note : 
- Make sure the ChromeDriver is installed.

## How to Run
1. Clone the repository.
2. Install dependencies using `pip install -r requirements.txt`.
3. Run the crawler using `python crawler.py`.

## Troubleshooting
- If the crawler is stuck, check the logs for errors.
- Ensure the Frontier Queue is populated with valid URLs.
- Debug the Fetcher and Parser Workers to ensure proper interaction.

## Future Improvements
- Add support for rate-limiting and retries.
- Implement better error handling and logging.
- Optimize queue management for large-scale crawling.

## License
This project is licensed under the MIT License.