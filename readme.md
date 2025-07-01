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

``` mermaid

flowchart TD
    A[Main: __main__] --> B[Initialize AsyncCrawler]
    B --> C[Seed URLs list]
    C --> D[Call crawl_multiple_seeds]
    D --> E[crawl_and_collect for each seed]

    subgraph Crawl_Workflow
        E --> F1[Init logger, tracker, lock]
        F1 --> F2[Create URLFrontier]
        F2 --> F3[Add seed_url to frontier]
        F3 --> F4[Start parser worker]
        F3 --> F5[Start fetcher workers - uses semaphore]

        subgraph Parallel_Fetchers
            F5 --> FW[Fetcher worker]
            FW --> F6[smart_fetch_html]
            F6 --> F7[Fetch using Selenium - headless Chrome]
            F7 --> F8[Return HTML result]
            F8 --> F9[Put url, html, depth into HTML queue]
            F9 --> F10[Tracker add]
        end

        F4 --> P1[Wait for HTML from queue]
        P1 --> P2[Call HTMLParser parse_html]

        subgraph HTMLParser
            P2 --> HP1[Parse HTML with BeautifulSoup]
            HP1 --> HP2[Run ProductPageClassifier analyze]
            HP2 --> HP3{Is product page}
            HP3 -->|Yes| HP4[Add to product_urls]
            HP3 -->|No| HP5[Skip]

            HP1 --> HP6[Extract anchor tags]
            HP6 --> HP7[Join and normalize hrefs]
            HP7 --> HP8[Filter by domain]
            HP8 --> HP9[Remove dead ends - is_dead_end_url]
            HP9 --> HP10[Add valid child_urls]
        end

        HP10 --> P3[Add child_urls to frontier]
        HP4 --> P4[Write product_urls to CSV]
        P4 --> P5[Tracker done]
        F10 --> P5
        P5 --> F11[Wait for all tasks to finish]
    end

    F11 --> G[Cleanup workers]
    G --> H[Return collected product URLs]

    subgraph URLFrontier
        F2 --> UF1[Use priority queue for URLs]
        UF1 --> UF2[Score each URL with score_url]
        UF2 --> UF3{URL type}
        UF3 --> UF4[High confidence product - score 1]
        UF3 --> UF5[Medium confidence - score 3]
        UF3 --> UF6[Dead end - score 100]
        UF3 --> UF7[Default - score 10]
    end


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
