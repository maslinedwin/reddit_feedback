# Reddit Lead Generation System - Refactored Architecture

## Overview

The Reddit Lead Generation System has been refactored from 12+ separate scripts into a clean, maintainable architecture with just 3 core components:

1. **reddit_collector.py** - Data collection (scraping + enrichment)
2. **reddit_analyzer.py** - Intelligence & analysis
3. **reddit_scheduler.py** - Automation & orchestration

## Quick Start

```bash
# 1. Run the setup script
python setup.py

# 2. Start the API server
python main.py

# 3. Access the frontend
# http://localhost:3000
```

## Architecture

### Core Components

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Collector     │────►│    Analyzer     │────►│   Scheduler     │
│                 │     │                 │     │                 │
│ • Scrape Reddit │     │ • Sentiment     │     │ • Daily runs    │
│ • Enrich users  │     │ • Lead scoring  │     │ • Backups       │
│ • Rate limiting │     │ • Creator detect│     │ • Monitoring    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │                       │
         └───────────────┬───────────────────────────────┘
                         ▼
                  ┌─────────────────┐
                  │  SQLite DB      │
                  │ reddit_leads.db │
                  └─────────────────┘
```

### Database Schema

- **users** - User profiles with analysis
- **posts** - Reddit posts with metadata  
- **comments** - Comments with relationships
- **analysis_runs** - Audit trail

### Configuration

All settings in `config.yaml`:
```yaml
reddit:
  subreddits: [patreon, creators]
  api_rate_limit: 1.2
  
analysis:
  min_activity_threshold: 5
  creator_keywords: {...}
  
scheduler:
  daily_run_time: "02:00"
  retention_days: 90
```

## Usage

### Manual Operations

```bash
# Collect new data (incremental)
python reddit_collector.py --incremental

# Collect from specific subreddit
python reddit_collector.py --subreddit patreon

# Analyze all users
python reddit_analyzer.py

# Analyze specific user
python reddit_analyzer.py --user username

# Run full daily workflow
python reddit_scheduler.py --mode=daily
```

### Automated Daily Runs

```bash
# Show cron entry
python reddit_scheduler.py --mode=cron

# Add to crontab for 2 AM daily runs
0 2 * * * /usr/bin/python3 /path/to/reddit_scheduler.py --mode=daily
```

### Data Migration

If you have existing data:
```bash
python migrate_data.py

# Verify migration
python migrate_data.py --verify-only
```

## API Endpoints

The FastAPI server provides:

- `GET /users` - List all analyzed users
- `GET /users/{username}` - Get specific user details
- `POST /query` - RAG-powered content search
- `GET /health` - System health check

## Features

### Lead Scoring Algorithm

Users are scored 0-100 based on:
- **Creator Likelihood** (40%) - Keywords & patterns
- **Discussion Starter** (20%) - Post engagement
- **Sentiment** (20%) - Patreon attitude
- **Karma** (10%) - Reddit reputation
- **Activity** (10%) - Engagement level

### Sentiment Analysis

Analyzes user attitudes toward Patreon:
- **Positive** - Supportive, recommending
- **Negative** - Critical, frustrated
- **Mixed** - Both positive and negative
- **Neutral** - Informational, questioning

### Creator Detection

Identifies potential creators using:
- Keyword matching ("my patreon", "my channel")
- Pattern recognition (self-promotion indicators)
- Context analysis (creator-specific language)

## Monitoring

### Logs
```bash
tail -f reddit_leads.log
```

### Database Stats
```sql
sqlite3 reddit_leads.db
.tables
SELECT COUNT(*) FROM users WHERE lead_score > 70;
```

### Analysis Runs
```sql
SELECT * FROM analysis_runs ORDER BY started_at DESC LIMIT 10;
```

## Troubleshooting

### Reddit API Issues
- Check credentials in config.yaml
- Verify rate limiting (1.2s between calls)
- Check for suspended accounts

### Database Issues
```bash
# Backup database
cp reddit_leads.db reddit_leads.db.backup

# Check integrity
sqlite3 reddit_leads.db "PRAGMA integrity_check;"
```

### Performance
- Adjust `min_activity_threshold` for fewer users
- Use incremental mode for daily runs
- Monitor disk space for backups

## Development

### Adding New Analysis Features

1. Update `reddit_analyzer.py`:
```python
def _calculate_new_metric(self, user_data):
    # Your analysis logic
    return score
```

2. Update database schema if needed
3. Add to lead scoring weights in config.yaml

### Adding New Subreddits

Edit `config.yaml`:
```yaml
reddit:
  subreddits:
    - patreon
    - creators
    - newsubreddit  # Add here
```

## Maintenance

### Regular Tasks
- Monitor log file size
- Clean old backups (automatic after 7 days)
- Check analysis quality quarterly
- Update creator keywords as needed

### Backup Strategy
- Automatic daily backups before runs
- 7-day retention (configurable)
- Stored in `backups/` directory

## Migration from Old System

The old system had these files:
- reddit_scraper.py
- analyze_and_save_users.py  
- enrich_users_reddit.py
- Multiple CSV files

Now consolidated into:
- reddit_collector.py (scraping + enrichment)
- reddit_analyzer.py (all analysis)
- reddit_leads.db (single database)

All existing data can be migrated using `migrate_data.py`.