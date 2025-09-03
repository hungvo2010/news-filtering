# News Filtering System MVP Technical Specification

## Document Overview
**Document Title**: News Filtering System MVP Specification  
**Version**: 1.0  
**Date**: September 3, 2025  
**Authors**: Perplexity AI (based on iterative user discussion)  
**Purpose**: This document provides a complete, developer-ready specification for building the Minimum Viable Product (MVP) of a news filtering system. It synthesizes requirements from user discussions, focusing on automated daily email digests of filtered news from Vietnamese sources. The system filters out negative content using fixed keywords and selects positive news based on default categories. This spec includes all functional and non-functional requirements, architecture recommendations, data handling, error handling, and a testing plan to enable immediate implementation.

**Assumptions**:
- Development will use open-source tools where possible to minimize costs.
- The system will run on a cloud platform (e.g., AWS, Google Cloud) for scalability.
- All operations comply with Vietnamese data protection laws (e.g., no unnecessary data collection).
- Scraping respects site terms (e.g., check robots.txt; use RSS feeds preferentially to avoid legal issues).
- Current date/time is based on Vietnam timezone (+07).

**Dependencies**:
- External libraries: For Python-based implementation (recommended), use BeautifulSoup/Scrapy for scraping, feedparser for RSS, smtplib or a service like SendGrid for emails.
- No user authentication or database in MVP beyond temporary storage.

**In Scope (MVP)**:
- Daily news collection from fixed sources.
- Fixed-keyword filtering and selection.
- Email generation and sending to a fixed list of recipients.
- Basic logging and error handling.

**Out of Scope**:
- User signup/registration.
- Customizable filters or preferences.
- Advanced AI/ML for prioritization or summarization.
- Mobile app or web interface.
- Analytics or performance monitoring beyond basic logs.

## System Overview and Objectives
- **Primary Objective**: Automate the collection, filtering, and daily emailing of positive news articles from Vietnamese sources to individual users, excluding negative or unrelated content.
- **Key Features**:
  - Fetch current-day news from specified sites.
  - Apply fixed negative filters to exclude bad news (e.g., violence, showbiz).
  - Select and group news by positive categories (e.g., laws, pricing).
  - Send minimalist emails with up to 5 articles, including summaries and links.
- **Target Users**: Individuals (fixed email list in MVP).
- **High-Level Workflow**:
  1. Scheduled daily job fetches news.
  2. Filter and select articles.
  3. Generate and send email.
- **Success Criteria**: System reliably sends daily emails with relevant content; no more than 5 articles; error rate <5% in testing.

## Functional Requirements
This section details what the system must do. Requirements are numbered for reference.

### REQ-1: News Collection
- **Description**: Fetch articles from sources, prioritizing current-day content.
- **Inputs**: Source URLs/RSS feeds; current date (from system clock, adjusted to +07).
- **Process**:
  - Check sources daily at a fixed time (e.g., 07:00 +07).
  - Use RSS feeds where available (e.g., VnExpress: https://vnexpress.net/rss; LaoDong: https://laodong.vn/rss; TuoiTre: https://tuoitre.vn/rss; ZingNews: scrape if no RSS).
  - For non-RSS sites, scrape headlines, summaries, publish dates, and URLs using selectors (e.g., HTML tags for titles).
  - Filter to include only articles where publish_date == current_date.
  - Output: List of articles with {title, summary (first 150 chars), url, publish_time, source}.
- **Constraints**: Limit fetch to 100-200 articles per source to avoid overload.

### REQ-2: Filtering and Selection
- **Description**: Apply fixed keywords to exclude negative news and select positive ones.
- **Inputs**: Fetched articles.
- **Negative Keywords** (case-insensitive, search in title/summary):
  - Violence: "giết người", "án mạng", "bạo lực", "tội phạm", "thảm sát", "đâm chém".
  - KOL: "KOL", "người ảnh hưởng", "drama KOL", "gossip KOL", "scandal influencer".
  - Showbiz: "showbiz", "scandal", "tin đồn", "ngôi sao" + "ly hôn", "bê bối", "drama".
  - General: "tử vong", "tai nạn chết người", "thảm họa", "xung đột", "chiến tranh".
- **Positive Categories/Keywords** (match at least one; group by category):
  - Vietnam Laws: "luật pháp Việt Nam", "dự luật mới", "cải cách pháp lý", "quy định mới", "nghị định".
  - Pricing (Gold/ETH/Coins/Dollar): "giá vàng", "giá ETH", "giá coin", "giá đô la", "tỷ giá ngoại tệ", "biến động giá vàng".
  - Health Issues: "sức khỏe cộng đồng", "bệnh dịch", "cập nhật y tế", "vaccine", "dinh dưỡng", "bệnh mãn tính".
  - Atmospheric Conditions: "thời tiết", "ô nhiễm không khí", "biến đổi khí hậu", "dự báo thời tiết", "môi trường", "chất lượng không khí".
- **Process**:
  - Exclude if any negative keyword matches.
  - Include and categorize if positive keyword matches.
  - Sort: Group by category, then by publish_time (descending).
  - Limit: Select top 5 articles across categories (e.g., round-robin: 1-2 per category if available; if <5, send all).
- **Output**: Filtered list of up to 5 articles.

### REQ-3: Email Generation and Sending
- **Description**: Create and send daily digest emails.
- **Inputs**: Filtered articles; fixed email list (e.g., stored in config file as array: ["user1@example.com", "user2@example.com"]).
- **Process**:
  - Generate HTML/plain-text email.
  - Subject: "Daily News Digest - [DD/MM/YYYY]".
  - Body Structure (minimalist):
    - Greeting: "Chào bạn,".
    - Sections: Markdown headers (e.g., ## Vietnam Laws).
    - Per Article: **Title** - Summary (truncated 100-150 chars). Đọc thêm: [url].
    - Footer: "Email này được gửi tự động. Không trả lời.".
  - Send to all in fixed list via SMTP (e.g., using SendGrid API for reliability).
- **Frequency**: Once daily (e.g., 08:00 +07), after filtering.
- **If No Articles**: Send email with body: "Không có tin tức phù hợp hôm nay.".

### REQ-4: Scheduling and Execution
- **Description**: Automate daily runs.
- **Process**: Use cron job or scheduler (e.g., APScheduler in Python) to trigger REQ-1 to REQ-3.

## Non-Functional Requirements
- **Performance**: Process <500 articles in <5 minutes; handle up to 10 recipients.
- **Availability**: 99% uptime; daily job must run reliably (e.g., retry on failure).
- **Security**: No user data stored; use secure SMTP (TLS); avoid storing scraped content long-term.
- **Scalability**: MVP handles fixed load; design for easy expansion (e.g., modular code).
- **Usability**: Emails are readable on mobile/desktop (responsive HTML).
- **Reliability**: Log all actions (e.g., using Python logging module); retry failed scrapes once.
- **Compliance**: Respect source copyrights (summaries only, with links); no data resale.

## Architecture Choices
- **High-Level Architecture**: Serverless or simple backend script.
  - **Language**: Python (recommended for scraping/email ease).
  - **Components**:
    - Scraper Module: Handles REQ-1 (use requests + BeautifulSoup/feedparser).
    - Filter Module: Handles REQ-2 (simple string matching).
    - Email Module: Handles REQ-3 (use smtplib or email service API).
    - Scheduler: Cron or APScheduler for daily execution.
  - **Deployment**: Cloud VM (e.g., AWS EC2) or container (Docker) for portability.
  - **Database**: None needed; use in-memory lists or temporary JSON files.
- **Data Flow Diagram** (Textual):
  ```
  Scheduler --> Scraper (Fetch from Sources) --> Filter (Apply Keywords) --> Email Generator --> SMTP Service --> Recipients
  ```
- **Tech Stack Example**:
  - Python 3.x
  - Libraries: requests, beautifulsoup4, feedparser, smtplib, python-dotenv (for config).
  - Config File: .env with email list, SMTP credentials, keywords (as JSON).

## Data Handling Details
- **Data Sources**: External websites (scraped/RSS).
- **Data Types**: Article metadata (title, summary, url, date) – transient, not stored beyond processing.
- **Storage**: Temporary (in-memory or local JSON during run); delete after email send.
- **Privacy**: Fixed emails are hardcoded/config-based; no collection or processing of personal data.
- **Backup**: None in MVP; logs stored in files for debugging.

## Error Handling Strategies
- **Scraping Errors** (e.g., site down): Retry once; log error; skip source and proceed.
- **Filtering Errors** (e.g., no matches): Send fallback email as per REQ-3.
- **Email Sending Errors** (e.g., SMTP failure): Retry up to 3 times; log and alert admin (e.g., via secondary email).
- **General Errors**: Use try-except blocks; log to file (e.g., errors.log) with timestamp, message, stack trace.
- **Monitoring**: Basic – check logs daily; future: integrate with tools like Sentry.

## Testing Plan
- **Unit Tests**: Test individual modules (e.g., scraper fetches correct data; filter excludes/includes properly). Use pytest; mock external calls (e.g., mock RSS responses).
- **Integration Tests**: End-to-end flow (fetch --> filter --> generate email string). Simulate with sample data from user attachments.
- **Functional Tests**: Verify REQ-1 to REQ-4 (e.g., run daily job; check email content for 5 articles, correct grouping).
- **Edge Cases**: No articles; partial source failures; non-UTF8 content; date mismatches.
- **Performance Tests**: Time execution for 200 articles (<5 min).
- **Manual Tests**: Send test emails to dummy addresses; verify formatting on email clients (Gmail, Outlook).
- **Test Environment**: Local dev machine; staging cloud instance.
- **Acceptance Criteria**: 100% test coverage for core functions; no critical bugs; successful daily simulation.
- **Tools**: Pytest for automation; Postman for API mocks if needed.

This specification is self-contained and ready for implementation. If additional details (e.g., code snippets) are needed, provide feedback for revisions.

[1](https://www.smartsheet.com/free-technical-specification-templates)
[2](https://www.template.net/technical-specification)
[3](https://documentero.com/templates/it-engineering/document/technical-specification-document/)
[4](https://cds.cern.ch/record/2719227/files/IPPOG_Web_design_Technical_Specification_document_final_BBG.pdf)
[5](https://ijrpr.com/uploads/V3ISSUE6/IJRPR4729.pdf)
[6](https://www.ucl.ac.uk/isd/sites/isd/files/migrated-files/SRS-1-System-Requirements-Specifications-Template-v1p0.doc)
[7](https://procurement-notices.undp.org/view_file.cfm?doc_id=22162)
[8](https://www.smartsheet.com/sites/default/files/2021-03/IC-Software-Technical-Specification-9008_WORD.dotx)