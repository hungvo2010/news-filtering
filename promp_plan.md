## Project Blueprint: News Filtering System MVP

This blueprint outlines a structured approach to building the MVP based on the provided technical specification. The system will be implemented in Python, using open-source libraries like feedparser for RSS, BeautifulSoup for scraping, smtplib or SendGrid for emails, and APScheduler for scheduling. The architecture is modular: scraper, filter, email generator, and scheduler. Data handling is transient (in-memory or temporary JSON), with basic logging and error handling. Deployment targets a cloud VM for daily runs.

### High-Level Steps
1. **Setup Environment**: Initialize project structure, dependencies, and configuration.
2. **Implement News Collection**: Fetch articles from sources using RSS and scraping.
3. **Implement Filtering and Selection**: Apply keyword-based exclusion and categorization.
4. **Implement Email Generation and Sending**: Create and send digests to fixed recipients.
5. **Implement Scheduling**: Automate daily execution with error retries.
6. **Add Logging and Error Handling**: Integrate throughout modules.
7. **Testing**: Unit, integration, and functional tests.
8. **Integration and Deployment**: Wire everything together and deploy.

## Iterative Breakdown into Chunks

### Initial Chunks (High-Level Iterative Builds)
- **Chunk 1: Core Setup and News Collection** - Establish base project and fetch functionality.
- **Chunk 2: Filtering Logic** - Add exclusion and selection on top of fetched data.
- **Chunk 3: Email Functionality** - Generate and send emails based on filtered data.
- **Chunk 4: Scheduling and Automation** - Schedule the full pipeline.
- **Chunk 5: Error Handling and Logging** - Enhance reliability across chunks.
- **Chunk 6: Testing and Integration** - Verify and connect all parts.

### Refined Smaller Steps (Second Round Breakdown)
Refining each chunk into smaller, testable steps. Each step includes implementation, testing, and integration with prior steps.

- **Chunk 1 Steps**:
  - 1.1: Project setup (directories, virtual env, dependencies).
  - 1.2: Basic scraper for one RSS source.
  - 1.3: Extend to multiple sources, including scraping for non-RSS.
  - 1.4: Date filtering for current-day articles.

- **Chunk 2 Steps**:
  - 2.1: Negative keyword exclusion function.
  - 2.2: Positive keyword matching and categorization.
  - 2.3: Sorting and limiting to top 5 articles.

- **Chunk 3 Steps**:
  - 3.1: Email body generation (HTML/plain-text).
  - 3.2: Sending mechanism with config-based recipients.
  - 3.3: Handle no-articles case.

- **Chunk 4 Steps**:
  - 4.1: Basic scheduler setup.
  - 4.2: Integrate full pipeline into scheduler.

- **Chunk 5 Steps**:
  - 5.1: Add logging to all modules.
  - 5.2: Implement retries and error handling.

- **Chunk 6 Steps**:
  - 6.1: Unit tests for each module.
  - 6.2: Integration tests for end-to-end flow.
  - 6.3: Manual verification and deployment prep.

### Review and Final Sizing
After iteration, these steps are right-sized: Each is small (e.g., one function or module addition), allows for immediate testing (e.g., unit tests per step), and builds incrementally without big jumps. For instance, starting with one source in 1.2 ensures early validation before scaling. No step introduces untested complexity; each integrates with the previous (e.g., filtering uses collection output). This supports safe, progressive development.

## Series of Prompts for Code-Generation LLM

Below is a series of prompts designed for a code-generation LLM (e.g., GPT-4 or similar) to implement the project in a test-driven development (TDD) manner. Each prompt builds on the previous, assuming the LLM maintains context across generations. Prompts emphasize TDD: write tests first, then code to pass them, refactor. They ensure incremental progress, with no orphaned code—each step integrates into the growing codebase. Use Python 3.x, follow PEP 8, and include docstrings.

Prompts are separated by markdown sections, with the prompt text in code blocks.

### Prompt 1: Project Setup
```
You are implementing a News Filtering System MVP in Python. Start with test-driven development: write tests first, then code to pass them.

Task: Set up the project structure. Create a directory structure: /news_filter (root), /news_filter/src (for modules), /news_filter/tests (for tests), /news_filter/config (for .env). Install dependencies: requests, beautifulsoup4, feedparser, smtplib, python-dotenv, apscheduler. Add a basic config.py in src that loads .env (with placeholders for SMTP creds, email list as JSON array, keywords as JSON).

Write unit tests for config loading (e.g., test it reads .env correctly). Then implement the code. Ensure no errors in setup. Output the code files and test results.
```

### Prompt 2: Basic RSS Scraper
```
Building on the previous setup. Now implement REQ-1 partially: a scraper module for one RSS source (VnExpress: https://vnexpress.net/rss).

In src/scraper.py, create a function fetch_rss_articles(url, current_date) that uses feedparser to get entries, filters by publish_date == current_date (use datetime in +07 timezone), and returns list of dicts: {'title': str, 'summary': str[:150], 'url': str, 'publish_time': datetime, 'source': str}.

Write TDD: First, tests in tests/test_scraper.py (mock feedparser response, test filtering, test output format). Then code. Integrate with config if needed (e.g., load sources from .env). Run tests.
```

### Prompt 3: Extend to Multiple Sources and Scraping
```
Extend the scraper from previous. Add support for multiple RSS sources (add LaoDong and TuoiTre URLs to config). For ZingNews (no RSS), implement scraping using requests and BeautifulSoup: fetch headlines, summaries, dates from their site (assume selectors like 'article' tags—research minimal selectors).

Update fetch_articles(sources, current_date) to handle both RSS and scraping, combine results, limit to 100-200 per source. TDD: Add tests for multi-source, scraping mocks (use responses lib for HTTP mocks), edge cases like no articles. Integrate with prior scraper code; ensure it builds on Prompt 2.
```

### Prompt 4: Negative Keyword Filtering
```
Now REQ-2 partially: In src/filter.py, create exclude_negative(articles, negative_keywords) that checks title/summary case-insensitively for keywords (load from config JSON: e.g., {"violence": ["giết người", ...]}). Return filtered list.

TDD: Tests in tests/test_filter.py (sample articles, test exclusion, test case-insensitivity). Then code. Integrate by calling this after fetch_articles in a new main.py pipeline stub. Build on previous prompts' code.
```

### Prompt 5: Positive Keyword Matching and Categorization
```
Extend filter.py: Add categorize_positive(articles, positive_keywords) where positive_keywords is config JSON like {"laws": ["luật pháp Việt Nam", ...]}. Match at least one keyword, assign category, return dict of category: list of articles.

Then, combine with exclude_negative in a filter_and_select(articles) function. TDD: Tests for matching, categorization, non-matches. Integrate into main.py stub, using output from scraper. Ensure builds on prior steps.
```

### Prompt 6: Sorting and Limiting Articles
```
Finalize REQ-2: In filter.py, add sort_and_limit(categorized_articles) to sort each category by publish_time descending, then select top 5 across categories (round-robin, 1-2 per if available).

TDD: Tests for sorting, limiting, edge cases (fewer than 5, single category). Update filter_and_select to include this. Integrate in main.py: now pipeline is fetch -> filter -> select. Build on previous.
```

### Prompt 7: Email Body Generation
```
REQ-3 partially: In src/email_generator.py, create generate_email_body(articles, current_date) that builds HTML/plain-text: subject, greeting, sections by category (Markdown headers), per article: bold title, summary[:150], link. Handle no articles with fallback message. Use minimal responsive HTML.

TDD: Tests in tests/test_email_generator.py (sample articles, test structure, test fallback). Integrate into main.py pipeline. Builds on prior.
```

### Prompt 8: Email Sending
```
Extend email: Add send_email(body, subject, recipients, smtp_config) using smtplib (or SendGrid if API key in config). Load recipients from config JSON array. Support TLS.

TDD: Tests with mocks (e.g., smtpd for fake server), test sending, retries (up to 3). Update main.py to call this after generation. Ensure integration with previous steps.
```

### Prompt 9: Scheduler Setup
```
REQ-4: In src/scheduler.py, use APScheduler to schedule daily job at 07:00 +07 (use BlockingScheduler). The job calls the full pipeline: fetch, filter, generate, send (at 08:00 effectively).

TDD: Tests for scheduling (mock time, test triggers). Add to main.py as entry point (e.g., if __name__ == '__main__': start_scheduler()). Builds on all prior.
```

### Prompt 10: Logging and Error Handling
```
Add across modules: Use logging module (config in config.py, log to errors.log). In scraper/email, add try-except with retries (1 for scrape, 3 for email). Log errors with timestamp/stack.

TDD: Tests for logging, error scenarios (mock failures, check retries/logs). Refactor existing code to include this. Integrate everywhere; no orphans.
```

### Prompt 11: Unit and Integration Testing
```
Expand tests: Ensure 100% coverage for core (use pytest-cov). Add integration tests in tests/test_integration.py: end-to-end with mocks (full pipeline simulation).

Run all tests, fix issues. This wires everything: update main.py to include full flow. Builds on all previous prompts.
```

### Prompt 12: Final Integration and Deployment Prep
```
Final wiring: Create a deploy script (e.g., Docker setup for cloud VM). Add manual test instructions (e.g., run locally with dummy emails). Verify REQ compliance.

TDD: Add functional tests (simulate daily run). Output complete codebase, ready for deployment. Ensure no hanging code—all integrated from prior steps.
```