# Manual Script Commands

## Quick Reference for Running Scripts Manually

### 1. Start the Platform

**Option A: Start Everything**
```bash
# Backend (in one terminal)
cd backend
uvicorn main:app --reload --port 8000

# Frontend (in another terminal)
cd frontend
npm run dev
```

**Option B: Backend Only (for script usage)**
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

### 2. Data Collection Scripts

**Collect from All Monitored Platforms**
```bash
cd backend
python reddit_collector.py
```

**Collect from Specific Platform**
```bash
cd backend
python reddit_collector.py --subreddit patreon --days 7
```

**Force Full Collection (ignore incremental)**
```bash
cd backend
python reddit_collector.py --force
```

### 3. Analysis Scripts

**Analyze All Users**
```bash
cd backend
python reddit_analyzer.py
```

**Force Re-analysis of All Users**
```bash
cd backend
python reddit_analyzer.py --force
```

**Analyze Specific User**
```bash
cd backend
python reddit_analyzer.py --user USERNAME
```

### 4. Scheduler Commands

**Run Full Daily Process**
```bash
cd backend
python reddit_scheduler.py daily
```

**Just Collect Data**
```bash
cd backend
python reddit_scheduler.py collect
```

**Just Run Analysis**
```bash
cd backend
python reddit_scheduler.py analyze
```

**Database Maintenance**
```bash
cd backend
python reddit_scheduler.py maintenance
```

### 5. Database Queries

**View High-Value Leads**
```bash
cd backend
sqlite3 reddit_leads.db "SELECT username, lead_score, platform_sentiment, creator_likelihood FROM users WHERE lead_score > 70 ORDER BY lead_score DESC LIMIT 20;"
```

**Export Leads to CSV**
```bash
cd backend
sqlite3 -header -csv reddit_leads.db "SELECT * FROM users WHERE lead_score > 50;" > high_value_leads.csv
```

**Check Platform Stats**
```bash
cd backend
sqlite3 reddit_leads.db "SELECT platform, COUNT(*) as user_count, AVG(lead_score) as avg_score FROM users GROUP BY platform;"
```

**View Recent Collections**
```bash
cd backend
sqlite3 reddit_leads.db "SELECT * FROM monitored_subreddits ORDER BY last_scraped DESC;"
```

### 6. Monitoring Commands

**Check System Health**
```bash
curl http://localhost:8000/health
```

**View Analysis History**
```bash
cd backend
sqlite3 reddit_leads.db "SELECT * FROM analysis_runs ORDER BY started_at DESC LIMIT 10;"
```

**Check User Count**
```bash
cd backend
sqlite3 reddit_leads.db "SELECT COUNT(*) FROM users;"
```

### 7. Add Platform via CLI

```bash
cd backend
curl -X POST "http://localhost:8000/subreddits/add" \
  -H "Content-Type: application/json" \
  -d '{"subreddit": "buymeacoffee", "platform_name": "buymeacoffee"}'
```

### 8. Trigger Immediate Collection

```bash
cd backend
curl -X POST "http://localhost:8000/collect/patreon"
```

### 9. Backup Database

```bash
cd backend
cp reddit_leads.db backups/reddit_leads_$(date +%Y%m%d_%H%M%S).db
```

### 10. Setup Cron Job

Add to crontab (`crontab -e`):
```bash
# Run daily at 2 AM
0 2 * * * cd /path/to/reddit_feedback/backend && /usr/bin/python3 reddit_scheduler.py daily >> scheduler.log 2>&1
```

## Common Workflows

### Adding a New Platform
1. Start the backend: `uvicorn main:app --reload`
2. Add platform: `curl -X POST "http://localhost:8000/subreddits/add" -H "Content-Type: application/json" -d '{"subreddit": "onlyfans"}'`
3. Collect data: `python reddit_collector.py --subreddit onlyfans`
4. Analyze users: `python reddit_analyzer.py`

### Emergency Re-analysis
```bash
# If something went wrong, force re-analyze everyone
cd backend
python reddit_analyzer.py --force
```

### Export for CRM
```bash
cd backend
# Export with all fields
sqlite3 -header -csv reddit_leads.db "SELECT username, lead_score, platform, platform_sentiment, creator_likelihood, reddit_profile_url, last_activity FROM users WHERE lead_score > 60 ORDER BY lead_score DESC;" > crm_import.csv
```

### Debug Issues
```bash
# Check logs
cd backend
tail -f *.log

# Check specific user
sqlite3 reddit_leads.db "SELECT * FROM users WHERE username='USERNAME';"

# Check recent errors
sqlite3 reddit_leads.db "SELECT * FROM analysis_runs WHERE status='failed';"
```

## Tips

1. **Always run from backend directory** - Scripts expect to find config.yaml there
2. **Check config.yaml** - Make sure Reddit credentials are set
3. **Monitor rate limits** - Reddit API has limits, space out large collections
4. **Regular backups** - Database backups are created automatically but you can make manual ones
5. **Lead scores update** - Re-run analyzer weekly to update scores based on new activity