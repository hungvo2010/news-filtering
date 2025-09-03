# News Filter System MVP

A Vietnamese news filtering and email notification system that collects, filters, and sends daily email summaries of relevant news articles.

## Features

- **Multi-source News Collection**: RSS feeds + web scraping from Vietnamese news sites
- **Smart Filtering**: Positive/negative keyword filtering with case-insensitive matching
- **Email Notifications**: Responsive HTML emails with daily summaries
- **Automated Scheduling**: Daily execution at 07:00 Vietnam time (+07)
- **Error Handling**: Retry mechanisms and comprehensive logging

## Project Structure

```
news-filter/
├── src/                    # Source code modules
│   ├── config.py          # Configuration management
│   ├── scraper.py         # RSS/web scraping
│   ├── filter.py          # Keyword filtering & selection
│   ├── email_generator.py # HTML email generation
│   ├── email_sender.py    # SMTP email sending
│   └── scheduler.py       # Daily scheduling
├── tests/                 # Unit tests (29 tests)
├── config/                # Configuration files
│   └── .env              # Environment variables
├── main.py               # Main entry point
└── requirements.txt      # Dependencies
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables in `config/.env`:
```env
# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Email Recipients (JSON format)
EMAIL_RECIPIENTS=["recipient1@example.com", "recipient2@example.com"]

# Keywords Configuration (JSON format)
POSITIVE_KEYWORDS={"technology": ["công nghệ", "AI", "robot"], "economy": ["kinh tế", "GDP"], "sports": ["thể thao", "bóng đá"]}

NEGATIVE_KEYWORDS=["tai nạn", "thảm họa", "giết", "chết"]
```

## Usage

### Test Configuration
```bash
python3 main.py --config-only
```

### Test Pipeline (without sending email)
```bash
python3 main.py --mode=test
```

### Test Pipeline (with email sending)
```bash
python3 main.py --mode=test --send-email
```

### Run Pipeline Once
```bash
python3 main.py --mode=run-once
```

### Run Scheduled Mode (Daily at 07:00 +07)
```bash
python3 main.py --mode=schedule
```

## Testing

Run all unit tests:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ --cov=src --cov-report=html
```

## News Sources

**RSS Sources:**
- VnExpress
- LaoDong 
- TuoiTre

**Scraping Sources:**
- ZingNews (configurable selectors)

## Email Features

- **Responsive Design**: Mobile-friendly HTML emails
- **Vietnamese Language**: Native language support
- **Smart Truncation**: Summaries limited to 150 characters
- **Fallback Content**: "No news" message when no articles match
- **Source Attribution**: Clear source and timestamp info

## Filtering Logic

1. **Date Filtering**: Only current-day articles (Vietnam timezone +07)
2. **Negative Exclusion**: Remove articles containing negative keywords
3. **Positive Categorization**: Group articles by keyword categories
4. **Smart Selection**: Round-robin selection of top 5 articles across categories
5. **Time Sorting**: Newest articles prioritized

## Dependencies

- `requests`: HTTP requests for RSS/scraping
- `beautifulsoup4`: HTML parsing
- `python-dotenv`: Environment variable management
- `APScheduler`: Task scheduling
- `pytest`: Testing framework
- `responses`: HTTP mocking for tests

## System Requirements

- Python 3.7+
- SMTP server access (Gmail recommended with app passwords)
- Internet connectivity for news source access

## Scheduling

The system runs daily at **07:00 Vietnam time (+07)** and sends emails by **08:00**.

## Error Handling

- **Retry Logic**: 3 retries for email sending, 1 retry for scraping
- **Graceful Degradation**: Continues with partial data if some sources fail
- **Comprehensive Logging**: All operations logged to `news_filter.log`
- **Exception Handling**: Robust error handling throughout pipeline

## Test Coverage

- 29 unit tests covering all core functionality
- Mock-based testing for external dependencies
- 100% coverage of critical business logic

## Development

The codebase follows TDD principles with comprehensive test coverage. Each module has corresponding unit tests in the `tests/` directory.

To add new news sources:
1. Update RSS sources in `.env`
2. For scraping sources, add selectors to `SCRAPING_SOURCES` config
3. Test with `--mode=test` before production deployment