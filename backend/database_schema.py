"""
Unified database schema for Reddit Lead Generation System
Uses SQLite for simplicity and portability
"""

import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any, List
import json

class RedditDatabase:
    def __init__(self, db_path: str = "reddit_leads.db"):
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn
        
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            
    def create_tables(self):
        """Create all necessary tables"""
        with self.connect() as conn:
            cursor = conn.cursor()
            
            # Users table - consolidated profile with analysis
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    -- Reddit API data
                    reddit_id TEXT UNIQUE,
                    account_created TIMESTAMP,
                    link_karma INTEGER,
                    comment_karma INTEGER,
                    total_karma INTEGER,
                    is_suspended BOOLEAN DEFAULT FALSE,
                    has_verified_email BOOLEAN,
                    is_mod BOOLEAN,
                    -- Activity data
                    post_count INTEGER DEFAULT 0,
                    comment_count INTEGER DEFAULT 0,
                    last_activity TIMESTAMP,
                    -- Platform data
                    platform TEXT,  -- Primary platform (where first found)
                    found_in_subreddits TEXT,  -- JSON array of all subreddits
                    -- Analysis data
                    platform_sentiment TEXT,  -- Changed from patreon_sentiment
                    platform_rating REAL,  -- Changed from patreon_rating
                    creator_likelihood REAL,
                    discussion_starter_score REAL,
                    main_topics TEXT,  -- JSON array
                    summary TEXT,
                    lead_score REAL,  -- Overall lead quality score
                    -- Metadata
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_reddit_api_check TIMESTAMP,
                    analysis_version INTEGER DEFAULT 1
                )
            """)
            
            # Posts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id TEXT PRIMARY KEY,
                    reddit_id TEXT UNIQUE,
                    subreddit TEXT NOT NULL,
                    platform TEXT,  -- Platform name (usually same as subreddit)
                    author TEXT NOT NULL,
                    title TEXT NOT NULL,
                    selftext TEXT,
                    url TEXT,
                    score INTEGER,
                    upvote_ratio REAL,
                    num_comments INTEGER,
                    created_utc TIMESTAMP,
                    -- Analysis
                    embedding BLOB,  -- Store as binary
                    topics TEXT,  -- JSON array
                    sentiment TEXT,
                    -- Metadata
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (author) REFERENCES users(username)
                )
            """)
            
            # Comments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS comments (
                    id TEXT PRIMARY KEY,
                    reddit_id TEXT UNIQUE,
                    post_id TEXT NOT NULL,
                    parent_id TEXT,
                    author TEXT NOT NULL,
                    body TEXT NOT NULL,
                    score INTEGER,
                    created_utc TIMESTAMP,
                    -- Analysis
                    embedding BLOB,
                    sentiment TEXT,
                    is_agreement BOOLEAN,
                    -- Metadata
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (post_id) REFERENCES posts(id),
                    FOREIGN KEY (author) REFERENCES users(username)
                )
            """)
            
            # Analysis runs audit trail
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_type TEXT NOT NULL,  -- 'scrape', 'analyze', 'enrich'
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    status TEXT DEFAULT 'running',  -- 'running', 'completed', 'failed'
                    items_processed INTEGER DEFAULT 0,
                    error_message TEXT,
                    metadata TEXT  -- JSON with additional info
                )
            """)
            
            # Monitored subreddits table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS monitored_subreddits (
                    subreddit TEXT PRIMARY KEY,
                    platform_name TEXT,  -- Display name (defaults to subreddit name)
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    last_scraped TIMESTAMP,
                    posts_collected INTEGER DEFAULT 0,
                    users_found INTEGER DEFAULT 0
                )
            """)
            
            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_lead_score ON users(lead_score DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_creator_likelihood ON users(creator_likelihood DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_last_activity ON users(last_activity DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_platform ON users(platform)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_created ON posts(created_utc DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_subreddit ON posts(subreddit)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_posts_platform ON posts(platform)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_comments_author ON comments(author)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_runs_started ON analysis_runs(started_at DESC)")
            
            conn.commit()
            
    def upsert_user(self, user_data: Dict[str, Any]):
        """Insert or update user data"""
        with self.connect() as conn:
            cursor = conn.cursor()
            
            # Convert lists/dicts to JSON strings
            if 'main_topics' in user_data and isinstance(user_data['main_topics'], list):
                user_data['main_topics'] = json.dumps(user_data['main_topics'])
                
            # Build dynamic query based on provided fields
            fields = list(user_data.keys())
            placeholders = [f":{field}" for field in fields]
            
            # Add last_updated
            fields.append('last_updated')
            placeholders.append('CURRENT_TIMESTAMP')
            
            # Build UPDATE clause for conflicts
            update_clause = ", ".join([f"{field}=excluded.{field}" for field in fields if field != 'username'])
            
            query = f"""
                INSERT INTO users ({', '.join(fields)})
                VALUES ({', '.join(placeholders)})
                ON CONFLICT(username) DO UPDATE SET
                {update_clause}
            """
            
            cursor.execute(query, user_data)
            
    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row:
                user = dict(row)
                # Parse JSON fields
                if user.get('main_topics'):
                    user['main_topics'] = json.loads(user['main_topics'])
                return user
            return None
            
    def get_users_for_analysis(self, limit: int = 100, min_activity: int = 5):
        """Get users that need analysis"""
        with self.connect() as conn:
            cursor = conn.cursor()
            # Get users with activity but no recent analysis
            query = """
                SELECT username FROM users 
                WHERE (post_count + comment_count) >= ?
                AND (last_updated < datetime('now', '-7 days') OR platform_sentiment IS NULL OR lead_score IS NULL)
                ORDER BY last_activity DESC
                LIMIT ?
            """
            cursor.execute(query, (min_activity, limit))
            return [row['username'] for row in cursor.fetchall()]
            
    def get_users_for_enrichment(self, limit: int = 100):
        """Get users that need Reddit API enrichment"""
        with self.connect() as conn:
            cursor = conn.cursor()
            query = """
                SELECT username FROM users 
                WHERE last_reddit_api_check IS NULL 
                OR last_reddit_api_check < datetime('now', '-7 days')
                ORDER BY (post_count + comment_count) DESC
                LIMIT ?
            """
            cursor.execute(query, (limit,))
            return [row['username'] for row in cursor.fetchall()]
            
    def log_analysis_run(self, run_type: str, metadata: Optional[Dict] = None):
        """Start logging an analysis run"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO analysis_runs (run_type, metadata)
                VALUES (?, ?)
            """, (run_type, json.dumps(metadata) if metadata else None))
            return cursor.lastrowid
            
    def update_analysis_run(self, run_id: int, status: str, items_processed: int = 0, error_message: str = None):
        """Update analysis run status"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE analysis_runs 
                SET status = ?, items_processed = ?, error_message = ?, 
                    completed_at = CASE WHEN ? IN ('completed', 'failed') THEN CURRENT_TIMESTAMP ELSE NULL END
                WHERE id = ?
            """, (status, items_processed, error_message, status, run_id))
            
    def add_monitored_subreddit(self, subreddit: str, platform_name: Optional[str] = None):
        """Add a subreddit to monitor"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO monitored_subreddits 
                (subreddit, platform_name)
                VALUES (?, ?)
            """, (subreddit, platform_name or subreddit))
            
    def get_monitored_subreddits(self, active_only: bool = True) -> List[Dict]:
        """Get list of monitored subreddits"""
        with self.connect() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM monitored_subreddits"
            if active_only:
                query += " WHERE is_active = TRUE"
            query += " ORDER BY added_at DESC"
            
            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]
            
    def set_subreddit_active(self, subreddit: str, is_active: bool):
        """Enable or disable a subreddit"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE monitored_subreddits 
                SET is_active = ?
                WHERE subreddit = ?
            """, (is_active, subreddit))
            
    def update_subreddit_stats(self, subreddit: str, posts_collected: int, users_found: int):
        """Update subreddit collection statistics"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE monitored_subreddits 
                SET posts_collected = posts_collected + ?,
                    users_found = users_found + ?,
                    last_scraped = CURRENT_TIMESTAMP
                WHERE subreddit = ?
            """, (posts_collected, users_found, subreddit))

# Utility functions
def init_database():
    """Initialize database with schema"""
    db = RedditDatabase()
    db.create_tables()
    print("Database initialized successfully")
    
if __name__ == "__main__":
    init_database()