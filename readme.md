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
flowchart TD;

    A[Start] --> B[Traverse each Seed URL one by one]
    B --> C[Initialize Frontier with Seed URL <br> Create Fetcher Task <br> Create Parser Task]

    C --> D[Fetcher Worker]
    D --> E[Async Fetcher tries Async Client]
    E -->|Success| F[HTML Content → HTML Queue]
    E -->|Failure| G[Uses Selenium]
    G --> H[HTML Content → HTML Queue]

    F & H --> I[Parser Worker waits on HTML Queue]

    I --> J{HTML Content available?}
    J -->|Yes| K[Parse HTML:<br>- Extract Child URLs<br>- Detect Product URL]

    K --> L[Use Product Page Analyzer: <br>- Check HTML Features + URL Patterns]
    K --> M[Use Product URL Analyzer: <br>Detect Dead-end URLs]

    L --> N[If Product Page → Write to Output File]
    M --> O[If Valid & Not Visited → Add Child URLs to Frontier]

    J -->|No more HTML| P[Insert None in Queue\n→ Signal Parser to Stop]
    D --> Q[All URLs Fetched → Fetcher Worker Stops]

    P --> R[Parser Worker Stops]
    R --> S[Stop]
    Q --> S

    style A fill:green,stroke:#333,stroke-width:2px
    style S fill:red,stroke:#333,stroke-width:2px

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
