from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from reddit_scraper import bulk_scrape_subreddit  # Deprecated - use reddit_collector instead
from rag import find_similar_documents, update_rag_index, get_rag_stats
from pydantic import BaseModel
from typing import List, Optional, Dict
import pandas as pd
from database import get_data, get_user_analysis
import re
from collections import Counter
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Query(BaseModel):
    query: str

class SubredditRequest(BaseModel):
    subreddit: str
    platform_name: Optional[str] = None

class UserSummary(BaseModel):
    user_id: str
    username: str
    post_count: int
    comment_count: int
    total_score: int
    platform: Optional[str]  # Platform where user was found
    platform_sentiment: str  # positive, negative, neutral, mixed
    platform_rating: float  # 1-10
    main_topics: List[str]
    summary: str
    reddit_profile_url: str
    lead_score: float  # 0-100 overall conversion likelihood
    # New fields from analysis
    creator_likelihood: float  # 0-100
    discussion_starter_score: float
    last_active_in_data: Optional[str]
    account_age_days_in_data: int
    # Reddit API enriched fields
    reddit_account_created: Optional[str]
    reddit_account_age_days: Optional[int]
    reddit_link_karma: Optional[int]
    reddit_comment_karma: Optional[int]
    reddit_total_karma: Optional[int]
    reddit_last_active: Optional[str]
    is_active: Optional[bool]
    account_status: Optional[str]  # active, suspended, not_found, error
    
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Allow Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/bulk_scrape/{subreddit_name}")
def bulk_scrape(subreddit_name: str):
    # Deprecated endpoint - use /collect/{subreddit} instead
    return {"error": "This endpoint is deprecated. Use POST /collect/{subreddit} instead"}

@app.post("/query")
def query(query: Query):
    similar_documents = find_similar_documents(query.query)
    return {"context": "\n".join(similar_documents)}

@app.get("/rag/stats")
def rag_stats():
    """Get RAG system statistics"""
    return get_rag_stats()

@app.post("/rag/refresh")
def refresh_rag_index():
    """Manually refresh the RAG index"""
    success = update_rag_index()
    return {"success": success, "message": "RAG index refreshed" if success else "No data to index"}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "rag_stats": get_rag_stats()}

def analyze_patreon_sentiment(text: str) -> tuple[str, float]:
    """Analyze Patreon sentiment and return sentiment type and rating"""
    text_lower = text.lower()
    
    # Keywords for sentiment analysis
    positive_keywords = [
        "love", "great", "excellent", "amazing", "good", "helpful", "support",
        "useful", "valuable", "worth", "recommend", "happy", "satisfied",
        "appreciate", "fantastic", "wonderful", "best", "perfect"
    ]
    
    negative_keywords = [
        "hate", "bad", "terrible", "awful", "poor", "disappointing", "frustrating",
        "annoying", "expensive", "overpriced", "scam", "waste", "useless",
        "broken", "buggy", "slow", "confusing", "complicated", "difficult"
    ]
    
    neutral_keywords = [
        "okay", "fine", "alright", "average", "normal", "standard"
    ]
    
    # Count sentiment keywords
    positive_count = sum(1 for word in positive_keywords if word in text_lower)
    negative_count = sum(1 for word in negative_keywords if word in text_lower)
    neutral_count = sum(1 for word in neutral_keywords if word in text_lower)
    
    # Calculate sentiment score (1-10)
    total_keywords = positive_count + negative_count + neutral_count
    
    if total_keywords == 0:
        # Use basic heuristics if no keywords found
        if "?" in text and len(text) < 100:
            return "neutral", 5.0
        elif "!" in text and any(word in text_lower for word in ["great", "love", "amazing"]):
            return "positive", 8.0
        elif "!" in text and any(word in text_lower for word in ["hate", "terrible", "awful"]):
            return "negative", 2.0
        else:
            return "neutral", 5.0
    
    # Calculate weighted score
    sentiment_score = 5.0  # Base score
    
    # Adjust based on keyword counts
    if positive_count > negative_count:
        sentiment_score = 5.0 + (positive_count / total_keywords) * 5.0
        if negative_count > 0:
            sentiment_type = "mixed"
            sentiment_score -= 1.0  # Penalty for mixed sentiment
        else:
            sentiment_type = "positive"
    elif negative_count > positive_count:
        sentiment_score = 5.0 - (negative_count / total_keywords) * 4.0
        if positive_count > 0:
            sentiment_type = "mixed"
            sentiment_score += 0.5  # Slight boost for mixed sentiment
        else:
            sentiment_type = "negative"
    else:
        sentiment_type = "neutral"
    
    # Clamp score between 1 and 10
    sentiment_score = max(1.0, min(10.0, sentiment_score))
    
    return sentiment_type, round(sentiment_score, 1)

def generate_user_summary(user_posts: pd.DataFrame, user_comments: pd.DataFrame) -> str:
    """Generate AI-like summary of user's contributions"""
    summaries = []
    
    # Analyze posts
    if not user_posts.empty:
        post_topics = user_posts['title'].str.cat(sep=' ')
        summaries.append(f"Created {len(user_posts)} posts mainly discussing: {post_topics[:100]}...")
    
    # Analyze comments
    if not user_comments.empty:
        # Get context from parent posts
        all_data = get_data()
        comment_contexts = []
        
        for _, comment in user_comments.iterrows():
            parent_id = comment.get('parent_id', '')
            if parent_id.startswith('t3_'):  # It's a post
                post_id = parent_id[3:]
                parent_post = all_data[all_data['id'] == post_id]
                if not parent_post.empty:
                    comment_contexts.append({
                        'comment': comment['text'],
                        'post_title': parent_post.iloc[0]['title'],
                        'agrees': 'agree' in comment['text'].lower() or 'same' in comment['text'].lower()
                    })
        
        if comment_contexts:
            agreements = sum(1 for ctx in comment_contexts if ctx['agrees'])
            summaries.append(f"Made {len(user_comments)} comments, agreed with posts {agreements} times")
            
            # Add specific context
            for ctx in comment_contexts[:2]:  # First 2 for brevity
                if ctx['agrees']:
                    summaries.append(f"Agreed with post about '{ctx['post_title'][:50]}...'")
                else:
                    summaries.append(f"Commented on '{ctx['post_title'][:50]}...'")
    
    return " | ".join(summaries) if summaries else "No significant activity found"

@app.get("/users", response_model=List[UserSummary])
def get_users():
    """Get all analyzed users from pre-processed data"""
    # Load the main user analysis file
    df = get_user_analysis()
    
    if df.empty:
        logger.warning("No user analysis data found. Run analyze_and_save_users.py first.")
        return []
    
    # Convert DataFrame to list of UserSummary objects
    user_summaries = []
    for _, row in df.iterrows():
        user_summary = UserSummary(
            user_id=row['username'],
            username=row['username'],
            post_count=int(row['post_count']),
            comment_count=int(row['comment_count']),
            total_score=int(row['total_score']),
            platform=row.get('platform', 'patreon'),  # Add platform field
            platform_sentiment=row.get('platform_sentiment', row.get('patreon_sentiment', 'neutral')),
            platform_rating=float(row.get('platform_rating', row.get('patreon_rating', 5.0))),
            main_topics=row['main_topics'] if isinstance(row['main_topics'], list) else [],
            summary=row['summary'],
            reddit_profile_url=row['reddit_profile_url'],
            lead_score=float(row.get('lead_score', 0)),  # Add lead_score field
            # New fields with defaults
            creator_likelihood=float(row.get('creator_likelihood', 0)),
            discussion_starter_score=float(row.get('discussion_starter_score', 0)),
            last_active_in_data=row.get('last_active_in_data'),
            account_age_days_in_data=int(row.get('account_age_days_in_data', 0)),
            # Reddit enriched fields
            reddit_account_created=row.get('reddit_account_created') if pd.notna(row.get('reddit_account_created')) else None,
            reddit_account_age_days=int(row.get('reddit_account_age_days')) if pd.notna(row.get('reddit_account_age_days')) else None,
            reddit_link_karma=int(row.get('reddit_link_karma')) if pd.notna(row.get('reddit_link_karma')) else None,
            reddit_comment_karma=int(row.get('reddit_comment_karma')) if pd.notna(row.get('reddit_comment_karma')) else None,
            reddit_total_karma=int(row.get('reddit_total_karma')) if pd.notna(row.get('reddit_total_karma')) else None,
            reddit_last_active=row.get('reddit_last_active') if pd.notna(row.get('reddit_last_active')) else None,
            is_active=row.get('is_active') if pd.notna(row.get('is_active')) else None,
            account_status=row.get('account_status', 'unknown')
        )
        user_summaries.append(user_summary)
    
    return user_summaries

@app.get("/users/{username}", response_model=UserSummary)
def get_user(username: str):
    """Get detailed analysis for a specific user"""
    users = get_users()
    for user in users:
        if user.username == username:
            return user
    return {"error": "User not found"}

@app.post("/users/analyze")
def analyze_users():
    """Trigger re-analysis of all users (this may take a while)"""
    try:
        # Import and run the analysis function
        from analyze_and_save_users import analyze_users as run_analysis
        run_analysis()
        return {"success": True, "message": "User analysis completed successfully"}
    except Exception as e:
        logger.error(f"Error during user analysis: {e}")
        return {"success": False, "error": str(e)}

@app.post("/subreddits/add")
def add_subreddit(request: SubredditRequest):
    """Add new subreddit to monitor"""
    try:
        from database_schema import RedditDatabase
        db = RedditDatabase()
        
        # Add to monitored list
        platform_name = request.platform_name or request.subreddit
        db.add_monitored_subreddit(request.subreddit, platform_name)
        
        return {
            "success": True, 
            "message": f"Added r/{request.subreddit} as platform '{platform_name}'",
            "subreddit": request.subreddit,
            "platform": platform_name
        }
    except Exception as e:
        logger.error(f"Error adding subreddit: {e}")
        return {"success": False, "error": str(e)}

@app.get("/subreddits")
def get_monitored_subreddits():
    """Get list of monitored subreddits"""
    try:
        from database_schema import RedditDatabase
        db = RedditDatabase()
        
        subreddits = db.get_monitored_subreddits()
        return {
            "success": True,
            "subreddits": subreddits,
            "count": len(subreddits)
        }
    except Exception as e:
        logger.error(f"Error getting subreddits: {e}")
        return {"success": False, "error": str(e)}

@app.delete("/subreddits/{subreddit}")
def remove_subreddit(subreddit: str):
    """Stop monitoring a subreddit"""
    try:
        from database_schema import RedditDatabase
        db = RedditDatabase()
        
        db.set_subreddit_active(subreddit, False)
        return {
            "success": True,
            "message": f"Stopped monitoring r/{subreddit}"
        }
    except Exception as e:
        logger.error(f"Error removing subreddit: {e}")
        return {"success": False, "error": str(e)}

@app.post("/collect/{subreddit}")
def collect_subreddit_now(subreddit: str):
    """Trigger immediate collection for specific subreddit"""
    try:
        from reddit_collector import RedditCollector
        from database_schema import RedditDatabase
        
        db = RedditDatabase()
        collector = RedditCollector()
        
        # Get platform name
        subs = db.get_monitored_subreddits()
        platform = subreddit  # default
        for sub in subs:
            if sub['subreddit'] == subreddit:
                platform = sub['platform_name'] or subreddit
                break
        
        # Add if not exists
        db.add_monitored_subreddit(subreddit, platform)
        
        # Collect
        items = collector.collect_subreddit(subreddit, platform, incremental=True)
        
        return {
            "success": True,
            "message": f"Collected {items} items from r/{subreddit}",
            "items_collected": items
        }
    except Exception as e:
        logger.error(f"Error collecting from {subreddit}: {e}")
        return {"success": False, "error": str(e)}