```markdown
# TODO.md: News Filtering System MVP Checklist

This checklist is a thorough, step-by-step guide for implementing the News Filtering System MVP based on the provided technical specification. It follows the project blueprint, breaking down into chunks and refined steps. Each item includes sub-tasks for TDD (Test-Driven Development), implementation, integration, and verification. Mark items as complete by changing [ ] to [x].

Use this alongside the series of LLM prompts to generate code incrementally. Assume Python 3.x, modular structure, and best practices (PEP 8, docstrings, error handling).

## Chunk 1: Project Setup and News Collection
Focus: Establish base project and implement REQ-1 (News Collection).

- [ ] **Step 1.1: Project Setup**
  - [ ] Create directory structure: /news_filter (root), /news_filter/src (modules), /news_filter/tests (tests), /news_filter/config (.env).
  - [ ] Install dependencies: requests, beautifulsoup4, feedparser, smtplib, python-dotenv, apscheduler (use pip and requirements.txt).
  - [ ] Write unit tests for basic setup (e.g., verify dependencies import correctly).
  - [ ] Implement config.py in src to load .env placeholders (SMTP creds, email list as JSON, keywords as JSON).
  - [ ] Integrate: Run a basic script to load config and print values.
  - [ ] Verify: Run tests and ensure no setup errors.

- [ ] **Step 1.2: Basic RSS Scraper**
  - [ ] Write TDD tests in tests/test_scraper.py (mock feedparser, test filtering by date, output format).
  - [ ] Implement fetch_rss_articles(url, current_date) in src/scraper.py for one source (e.g., VnExpress).
  - [ ] Handle +07 timezone using datetime.
  - [ ] Integrate: Add to a stub main.py to call the function with sample input.
  - [ ] Verify: Run tests and manual execution with sample RSS URL.

- [ ] **Step 1.3: Extend to Multiple Sources and Scraping**
  - [ ] Update config with multiple RSS URLs (VnExpress, LaoDong, TuoiTre) and scraping targets (ZingNews).
  - [ ] Write TDD tests for multi-source handling and scraping mocks (use responses lib for HTTP).
  - [ ] Implement fetch_articles(sources, current_date) to combine RSS and scraping, limit 100-200 per source.
  - [ ] Add selectors for scraping (e.g., HTML tags for title, summary, date).
  - [ ] Integrate: Update main.py stub to call fetch_articles and output results.
  - [ ] Verify: Test with mocks, check for edge cases like site down (basic handling).

- [ ] **Step 1.4: Date Filtering for Current-Day Articles**
  - [ ] Write TDD tests for date filtering logic.
  - [ ] Refine scraper to strictly filter publish_date == current_date (+07).
  - [ ] Format output as list of dicts: {'title', 'summary'[:150], 'url', 'publish_time', 'source'}.
  - [ ] Integrate: Apply in fetch_articles function.
  - [ ] Verify: Run end-to-chunk simulation with sample data.

## Chunk 2: Filtering Logic
Focus: Implement REQ-2 (Filtering and Selection) on top of collected data.

- [ ] **Step 2.1: Negative Keyword Exclusion**
  - [ ] Write TDD tests in tests/test_filter.py (sample articles, case-insensitivity, exclusion logic).
  - [ ] Implement exclude_negative(articles, negative_keywords) in src/filter.py (load keywords from config).
  - [ ] Handle case-insensitive matching in title/summary.
  - [ ] Integrate: Call after fetch_articles in main.py pipeline.
  - [ ] Verify: Test with positive/negative sample articles.

- [ ] **Step 2.2: Positive Keyword Matching and Categorization**
  - [ ] Write TDD tests for matching and grouping.
  - [ ] Implement categorize_positive(articles, positive_keywords) returning dict {category: [articles]}.
  - [ ] Combine with exclude_negative in filter_and_select(articles).
  - [ ] Integrate: Update main.py to process fetched articles through this.
  - [ ] Verify: Check categorization with mixed samples.

- [ ] **Step 2.3: Sorting and Limiting to Top 5 Articles**
  - [ ] Write TDD tests for sorting (by publish_time descending) and limiting (round-robin, 1-2 per category).
  - [ ] Implement sort_and_limit(categorized_articles) with limit=5, handle <5 cases.
  - [ ] Update filter_and_select to include this step.
  - [ ] Integrate: Ensure main.py outputs final selected list.
  - [ ] Verify: Simulate with varying article counts.

## Chunk 3: Email Functionality
Focus: Implement REQ-3 (Email Generation and Sending).

- [ ] **Step 3.1: Email Body Generation**
  - [ ] Write TDD tests in tests/test_email_generator.py (structure, fallback, responsive HTML).
  - [ ] Implement generate_email_body(articles, current_date) in src/email_generator.py with subject, greeting, sections, articles, footer.
  - [ ] Use Markdown-like headers, truncate summaries to 100-150 chars.
  - [ ] Handle no-articles fallback: "Không có tin tức phù hợp hôm nay."
  - [ ] Integrate: Call after filtering in main.py.
  - [ ] Verify: Generate sample bodies and check formatting.

- [ ] **Step 3.2: Sending Mechanism**
  - [ ] Write TDD tests with SMTP mocks (e.g., smtpd), test retries.
  - [ ] Implement send_email(body, subject, recipients, smtp_config) with TLS support.
  - [ ] Load recipients from config JSON.
  - [ ] Integrate: Call after body generation in main.py.
  - [ ] Verify: Send to dummy emails in test mode.

- [ ] **Step 3.3: Handle No-Articles Case**
  - [ ] Write TDD tests for fallback email.
  - [ ] Ensure generate_email_body and send_email handle empty articles gracefully.
  - [ ] Integrate: Test in full chunk pipeline.
  - [ ] Verify: Simulate zero articles and check email sent.

## Chunk 4: Scheduling and Automation
Focus: Implement REQ-4 (Scheduling and Execution).

- [ ] **Step 4.1: Basic Scheduler Setup**
  - [ ] Write TDD tests for scheduling (mock time, triggers).
  - [ ] Implement setup_scheduler in src/scheduler.py using APScheduler (daily at 07:00 +07).
  - [ ] Define pipeline function for fetch-filter-generate-send.
  - [ ] Integrate: Add to main.py as entry point.
  - [ ] Verify: Run scheduler in test mode.

- [ ] **Step 4.2: Integrate Full Pipeline into Scheduler**
  - [ ] Wire all modules into the pipeline function.
  - [ ] Update scheduler to call pipeline at scheduled time (effective 08:00 send).
  - [ ] Integrate: Ensure main.py runs the scheduler.
  - [ ] Verify: Simulate daily run.

## Chunk 5: Error Handling and Logging
Focus: Add non-functional requirements (reliability, logging).

- [ ] **Step 5.1: Add Logging to All Modules**
  - [ ] Configure logging in config.py (to errors.log, info/error levels).
  - [ ] Write TDD tests for log outputs.
  - [ ] Add logging statements in scraper, filter, email, scheduler (e.g., start/end, errors).
  - [ ] Integrate: Refactor existing code to include logs.
  - [ ] Verify: Run pipeline and check log file.

- [ ] **Step 5.2: Implement Retries and Error Handling**
  - [ ] Write TDD tests for error scenarios (mocks for failures).
  - [ ] Add try-except with retries: 1 for scraping, 3 for email; log errors with timestamp/stack.
  - [ ] Handle general errors (e.g., skip failed sources, alert admin via secondary email if needed).
  - [ ] Integrate: Apply across all modules.
  - [ ] Verify: Simulate failures and check retries/fallbacks.

## Chunk 6: Testing and Integration
Focus: Comprehensive testing and final wiring.

- [ ] **Step 6.1: Unit Tests for Each Module**
  - [ ] Expand tests to cover all functions (use pytest-cov for 100% core coverage).
  - [ ] Include edge cases: no articles, partial failures, non-UTF8, date mismatches.
  - [ ] Run and fix issues.
  - [ ] Verify: Achieve <5% error rate in tests.

- [ ] **Step 6.2: Integration Tests for End-to-End Flow**
  - [ ] Write integration tests in tests/test_integration.py (mock full pipeline).
  - [ ] Test REQ-1 to REQ-4 flows.
  - [ ] Include performance tests: Time for 200 articles (<5 min).
  - [ ] Verify: Simulate with sample data.

- [ ] **Step 6.3: Manual Verification and Deployment Prep**
  - [ ] Perform manual tests: Run daily job, check emails in clients (Gmail, Outlook), verify formatting.
  - [ ] Create deploy script (e.g., Docker for AWS EC2).
  - [ ] Add README.md with setup, run, and deployment instructions.
  - [ ] Final integration: Ensure no orphaned code; run full system simulation.
  - [ ] Verify: Confirm success criteria (reliable emails, up to 5 articles, compliance).

## Additional Tasks
- [ ] **Documentation and Review**
  - [ ] Update README.md with project overview, usage, and tech stack.
  - [ ] Review code for scalability, security (TLS, no long-term storage), and compliance (respect robots.txt, copyrights).
  - [ ] Conduct code review: Check PEP 8, modularity.

- [ ] **Deployment**
  - [ ] Set up cloud VM (e.g., AWS EC2) or container.
  - [ ] Configure cron/APScheduler for production.
  - [ ] Test live run with fixed recipients.

- [ ] **Post-Implementation**
  - [ ] Monitor logs for first few runs.
  - [ ] Plan for future expansions (out of scope, but note ideas like customizable filters).

Total Items: ~50. Track progress weekly. If issues arise, revisit spec or prompts.
```

[1](https://pub.aimind.so/creating-a-simple-to-do-list-in-python-c0f52ab15814)
[2](https://www.youtube.com/watch?v=aEIHZDv_23U)
[3](https://www.w3schools.com/howto/howto_js_todolist.asp)
[4](https://pythongeeks.org/python-to-do-list/)
[5](https://realpython.com/django-todo-lists/)
[6](https://www.w3resource.com/projects/python/python-to-do-list-application-project.php)
[7](https://www.reddit.com/r/learnpython/comments/1hymaxg/ive_created_a_to_do_list_app_in_python_now_whats/)
[8](https://dev.to/carlovo/straight-to-the-money-minimalistic-yet-all-inclusive-python-project-template-4633)
[9](https://v0.app/chat/python-todo-list-project-O22BtG6nQK0)