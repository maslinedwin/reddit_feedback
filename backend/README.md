# Reddit Lead Generation Platform

A powerful AI-driven platform for discovering and analyzing potential leads from Reddit communities focused on creator monetization platforms (Patreon, Ko-fi, OnlyFans, etc.).

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- Reddit API credentials (client ID, secret, user agent)

### Installation

1. **Backend Setup**
```bash
cd backend
pip install -r requirements.txt

# Configure your Reddit API credentials
cp config.yaml.example config.yaml
# Edit config.yaml with your credentials
```

2. **Frontend Setup**
```bash
cd frontend
npm install
```

### Running the Platform

1. **Start Backend API**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

2. **Start Frontend**
```bash
cd frontend
npm run dev
```

3. **Access the Platform**
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

## 🎯 Core Features

### 1. Dynamic Platform Management
- Add any creator monetization subreddit (Patreon, Ko-fi, OnlyFans, etc.)
- Automatic user discovery and tagging by platform
- Real-time data collection

### 2. Lead Scoring System
Each user gets a lead score (0-100) based on:
- **Creator Likelihood** (40% weight) - Keywords indicating they're a creator
- **Discussion Starter** (20% weight) - How often they start conversations
- **Platform Sentiment** (20% weight) - Positive/negative views on monetization
- **Karma Score** (10% weight) - Reddit reputation
- **Activity Level** (10% weight) - Engagement frequency

### 3. Advanced Analytics
- Sentiment analysis (positive/negative/neutral/mixed)
- Topic extraction and interests
- Activity patterns and engagement metrics
- Reddit profile enrichment

## 📖 Platform Usage Guide

### Adding New Platforms/Subreddits

1. Navigate to the **Platforms** tab in the UI
2. Enter the subreddit name (e.g., "buymeacoffee")
3. Click **Add Platform**
4. Click **Collect Now** to start immediate data collection

### Understanding the Users Table

- **Lead Score**: Color-coded conversion likelihood
  - 🟢 Green (70-100): High-quality leads
  - 🟡 Yellow (40-69): Medium potential
  - ⚫ Gray (0-39): Lower priority
  
- **Creator %**: Likelihood the user is already a creator
- **Discussion Score**: How often they start conversations
- **Platform View**: Their sentiment toward monetization platforms

### Manual Script Usage

If you need to run scripts manually:

```bash
# Collect data from all monitored platforms
python reddit_collector.py

# Analyze all users and calculate lead scores
python reddit_analyzer.py

# Run both collection and analysis
python reddit_scheduler.py daily

# Force re-analysis of all users
python reddit_analyzer.py --force

# Analyze specific user
python reddit_analyzer.py --user USERNAME
```

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Next.js UI    │────▶│   FastAPI Backend │────▶│  SQLite Database │
│  (Port 3000)    │     │    (Port 8000)   │     │  (reddit_leads.db)│
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                     ┌─────────────────────┐
                     │   Reddit API        │
                     │  (Data Collection)  │
                     └─────────────────────┘
```

### Core Components

1. **reddit_collector.py** - Collects posts, comments, and user data
2. **reddit_analyzer.py** - Performs sentiment analysis and lead scoring
3. **reddit_scheduler.py** - Handles automated daily runs
4. **main.py** - FastAPI backend server
5. **database_schema.py** - SQLite database structure

## 🔧 Configuration

Edit `config.yaml` to customize:

```yaml
reddit:
  client_id: "your_client_id"
  client_secret: "your_secret"
  user_agent: "your_app_name"

collection:
  posts_per_subreddit: 100
  days_back: 30

analysis:
  min_activity_threshold: 5
  sentiment_keywords:
    positive: ["love", "great", "amazing", ...]
    negative: ["hate", "terrible", "scam", ...]
```

## 📊 Database Schema

- **users** - User profiles with analysis data
- **posts** - Reddit posts from monitored subreddits  
- **comments** - Comments with sentiment analysis
- **monitored_subreddits** - Platforms being tracked
- **analysis_runs** - Tracking and monitoring

## 🚦 API Endpoints

- `GET /users` - Get analyzed users with lead scores
- `GET /subreddits` - List monitored platforms
- `POST /subreddits/add` - Add new platform to monitor
- `POST /collect/{subreddit}` - Trigger immediate collection
- `POST /users/analyze` - Re-analyze all users

## 🛠️ Maintenance

### Daily Automation
The platform can run automatically via cron:
```bash
# Add to crontab
0 2 * * * cd /path/to/backend && python reddit_scheduler.py daily
```

### Database Backups
Backups are automatically created in the `backups/` folder during daily runs.

### Monitoring
- Check `analysis_runs` table for job history
- Monitor API health at `/health` endpoint

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Test thoroughly
4. Submit a pull request

## 📝 License

This project is proprietary software. All rights reserved.