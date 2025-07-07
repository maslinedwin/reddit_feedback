# Platform Usage Guide - Reddit Lead Generation System

## 🎯 Overview

This system helps you discover potential customers from Reddit who are interested in creator monetization platforms. It's designed to work with ANY platform - Patreon, Ko-fi, OnlyFans, Buy Me a Coffee, Gumroad, Substack, and more.

## 🚀 Getting Started

### Step 1: Access the Platform
1. Start the backend: `uvicorn main:app --reload --port 8000`
2. Start the frontend: `npm run dev`
3. Open http://localhost:3000 in your browser

### Step 2: Add Your First Platform
1. Click the **"Platforms"** tab in the header
2. Enter a subreddit name (e.g., "patreon", "onlyfans", "buymeacoffee")
3. Click **"Add Platform"**
4. The system will start monitoring this subreddit

### Step 3: Collect Data
- Click **"Collect Now"** next to any platform for immediate data collection
- Or wait for the automated daily collection (2 AM by default)

### Step 4: View and Analyze Leads
1. Click the **"Users"** tab
2. Browse discovered users sorted by lead score
3. Use filters to find specific types of leads

## 📊 Understanding Lead Scores

### What is a Lead Score?
A number from 0-100 indicating how likely a user is to convert to a paid customer on creator platforms.

### Score Breakdown:
- **90-100**: 🔥 HOT LEAD - Creator actively looking for monetization
- **70-89**: 🟢 WARM LEAD - High interest, likely to convert
- **50-69**: 🟡 MODERATE - Some interest, needs nurturing
- **30-49**: 🟠 COOL - Low interest currently
- **0-29**: ❄️ COLD - Unlikely to convert

### Factors Affecting Lead Score:

1. **Creator Likelihood (40% weight)**
   - Uses keywords like "my channel", "my content", "support me"
   - Links to creator platforms
   - Mentions of subscriber counts or audience

2. **Discussion Starter (20% weight)**
   - How often they create posts
   - Engagement their posts receive
   - Quality of discussions started

3. **Platform Sentiment (20% weight)**
   - **Positive**: "love patreon", "great platform"
   - **Negative**: "too expensive", "hate fees"
   - **Mixed**: Both positive and negative views
   - **Neutral**: Asking questions, no clear opinion

4. **Reddit Karma (10% weight)**
   - Total karma indicates credibility
   - Higher karma = more established user

5. **Activity Level (10% weight)**
   - Frequency of posts and comments
   - Recent activity weighted higher

## 🔍 Using the Users Table

### Columns Explained:

- **User**: Reddit username with karma count
- **Account Age**: How long they've been on Reddit
- **Last Active**: When they last posted/commented
- **Activity**: Posts (P) and Comments (C) count
- **Creator %**: Likelihood they're already a creator
- **Discussion**: How good they are at starting conversations
- **Platform**: Which subreddit they were found in
- **Platform View**: Their sentiment toward monetization
- **Lead Score**: Overall conversion likelihood

### Sorting and Filtering:

- Click any column header to sort
- Use the search bar to filter by:
  - Username
  - Topics they discuss
  - Platform sentiment
  - Summary keywords

### Taking Action:

1. **Click "Profile"** to view their Reddit history
2. **Export to CSV** for CRM integration
3. **High lead scores** → Prioritize for outreach
4. **Creator likelihood > 50%** → They may need platform switching info
5. **Positive sentiment** → Ready for direct pitch

## 🎮 Advanced Features

### Adding Multiple Platforms
```
Common subreddits to monitor:
- patreon
- onlyfans
- buymeacoffee (or kofi)
- gumroad
- substack
- subscribestar
- fansly
- justforfans
```

### Platform-Specific Analysis
Each platform's users are analyzed separately:
- Users found in r/patreon are tagged as "patreon" platform
- Users can appear in multiple platforms
- Sentiment is specific to where they were discussing

### Bulk Operations

**Force Complete Re-analysis:**
```bash
python reddit_analyzer.py --force
```

**Collect Specific Platform Only:**
```bash
python reddit_collector.py --subreddit onlyfans --days 7
```

**Export All Data:**
```bash
sqlite3 reddit_leads.db ".mode csv" ".output all_users.csv" \
  "SELECT * FROM users WHERE lead_score > 50 ORDER BY lead_score DESC" ".quit"
```

## 📈 Best Practices

### 1. Regular Monitoring
- Check new leads daily
- Focus on users with scores > 70
- Track sentiment changes over time

### 2. Platform Selection
- Add platforms where YOUR customers might be
- Include competitor subreddits
- Monitor general creator subreddits (r/NewTubers, r/Twitch, etc.)

### 3. Lead Qualification
- **High Score + Recent Activity** = Contact immediately
- **High Creator % + Negative Sentiment** = Platform switching opportunity
- **High Discussion Score** = Potential influencer/advocate

### 4. Data Hygiene
- The system auto-updates user data weekly
- Remove inactive platforms quarterly
- Export and backup high-value leads

## 🔧 Troubleshooting

### No Users Showing Up?
1. Wait 5-10 minutes after adding a platform
2. Click "Collect Now" to force collection
3. Check if the subreddit name is correct (no "r/" prefix)

### Lead Scores Seem Low?
- Normal distribution: Most users score 20-60
- Scores > 70 are genuinely high-quality leads
- Adjust `config.yaml` weights if needed

### Missing Recent Activity?
- Reddit API has rate limits
- Large subreddits may take longer to process
- Check back in a few hours

## 💡 Pro Tips

1. **Cross-Reference Platforms**: Users appearing in multiple platform subreddits are often serious about monetization

2. **Sentiment Patterns**: Users with "mixed" sentiment often have specific pain points you can address

3. **Activity Timing**: Users active in the last 24h are 3x more likely to respond to outreach

4. **Creator Detection**: Even 30% creator likelihood is significant - many creators don't explicitly state it

5. **Bulk Analysis**: Export to CSV and use pivot tables for deeper insights

## 📞 Example Outreach Strategy

For a user with:
- Lead Score: 85
- Platform Sentiment: Mixed (7.5/10)
- Creator Likelihood: 70%

**Approach**: "Hey [username], I noticed you had some concerns about Patreon's fees in your recent post. Have you considered [alternative]? We offer [specific benefit addressing their concern]..."

## 🔐 Privacy & Ethics

- All data is publicly available Reddit content
- Respect Reddit's ToS and API limits
- Use for legitimate business development only
- Don't spam or harass users

---

**Questions?** Check the main README.md or examine the source code for deeper customization options.