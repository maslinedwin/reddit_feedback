"""
Reddit Data Collector - Unified scraping and enrichment
Combines functionality of reddit_scraper.py and enrich_users_reddit.py
"""

import praw
import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Set
import json
import sqlite3

from config_loader import config
from database_schema import RedditDatabase

logging.basicConfig(
    level=getattr(logging, config.get('logging.level', 'INFO')),
    format=config.get('logging.format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)
logger = logging.getLogger(__name__)

class RedditCollector:
    def __init__(self):
        self.config = config
        self.db = RedditDatabase(config.database_path)
        self.reddit = self._init_reddit()
        self.rate_limit = config.get('reddit.api_rate_limit', 1.2)
        
    def _init_reddit(self) -> praw.Reddit:
        """Initialize Reddit API client"""
        return praw.Reddit(
            client_id=config.reddit_client_id,
            client_secret=config.reddit_client_secret,
            user_agent=config.reddit_user_agent
        )
        
    def collect_all(self, incremental: bool = True):
        """Main collection method - scrapes posts/comments and enriches users"""
        # Get monitored subreddits from database
        subreddits = self.db.get_monitored_subreddits(active_only=True)
        
        run_id = self.db.log_analysis_run('collect', {
            'incremental': incremental,
            'subreddits': [s['subreddit'] for s in subreddits]
        })
        
        try:
            total_items = 0
            
            # Collect from each monitored subreddit
            for sub_config in subreddits:
                subreddit_name = sub_config['subreddit']
                platform_name = sub_config['platform_name'] or subreddit_name
                
                logger.info(f"Collecting from r/{subreddit_name} (platform: {platform_name})")
                items = self.collect_subreddit(subreddit_name, platform_name, incremental)
                total_items += items
                
            # Enrich users who need updates
            logger.info("Enriching user data...")
            enriched = self.enrich_users(limit=100)
            
            self.db.update_analysis_run(
                run_id, 'completed', 
                total_items + enriched
            )
            
            logger.info(f"Collection completed: {total_items} items scraped, {enriched} users enriched")
            
        except Exception as e:
            logger.error(f"Collection failed: {e}")
            self.db.update_analysis_run(run_id, 'failed', total_items, str(e))
            raise
            
    def collect_subreddit(self, subreddit_name: str, platform_name: str, incremental: bool = True) -> int:
        """Collect posts and comments from a subreddit"""
        subreddit = self.reddit.subreddit(subreddit_name)
        items_collected = 0
        users_found = set()
        
        # Get last scraped timestamp if incremental
        last_scraped = None
        if incremental:
            with self.db.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT MAX(created_utc) FROM posts WHERE subreddit = ?
                """, (subreddit_name,))
                result = cursor.fetchone()
                if result and result[0]:
                    last_scraped = datetime.fromisoformat(result[0])
                    
        # Collect posts
        posts_collected, users_found = self._collect_posts(subreddit, platform_name, last_scraped)
        items_collected += posts_collected
        
        # Update subreddit stats
        self.db.update_subreddit_stats(subreddit_name, posts_collected, len(users_found))
        
        logger.info(f"Collected {posts_collected} posts from r/{subreddit_name}")
        
        return items_collected
        
    def _collect_posts(self, subreddit, platform_name: str, last_scraped: Optional[datetime]) -> tuple[int, set]:
        """Collect posts from subreddit"""
        posts_collected = 0
        authors_seen = set()
        
        # Determine collection limit
        limit = None if not last_scraped else config.get('reddit.scrape_limit', 1000)
        
        try:
            for post in subreddit.new(limit=limit):
                # Check if we've reached posts older than last_scraped
                post_time = datetime.fromtimestamp(post.created_utc)
                if last_scraped and post_time <= last_scraped:
                    logger.info(f"Reached previously scraped posts at {post_time}")
                    break
                    
                # Skip if too old
                max_age = config.get('reddit.max_age_days', 365)
                if (datetime.now() - post_time).days > max_age:
                    continue
                    
                # Save post with platform
                self._save_post(post, platform_name)
                posts_collected += 1
                
                # Track author for enrichment
                if post.author:
                    authors_seen.add(post.author.name)
                
                # Collect comments
                post.comments.replace_more(limit=0)
                for comment in post.comments.list():
                    if comment.author:
                        self._save_comment(comment, post.id)
                        authors_seen.add(comment.author.name)
                        
                # Rate limiting
                time.sleep(self.rate_limit)
                
                # Progress update
                if posts_collected % 100 == 0:
                    logger.info(f"Progress: {posts_collected} posts collected")
                    
        except Exception as e:
            logger.error(f"Error collecting posts: {e}")
            
        # Create user records for new authors with platform
        self._create_user_records(authors_seen, platform_name)
        
        return posts_collected, authors_seen
        
    def _save_post(self, post, platform_name: str):
        """Save post to database"""
        with self.db.connect() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO posts 
                    (id, reddit_id, subreddit, platform, author, title, selftext, url, 
                     score, upvote_ratio, num_comments, created_utc)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    post.id,
                    f"t3_{post.id}",
                    post.subreddit.display_name,
                    platform_name,
                    post.author.name if post.author else '[deleted]',
                    post.title,
                    post.selftext,
                    post.url,
                    post.score,
                    post.upvote_ratio,
                    post.num_comments,
                    datetime.fromtimestamp(post.created_utc)
                ))
                
                # Update user post count
                if post.author:
                    cursor.execute("""
                        UPDATE users SET post_count = post_count + 1,
                        last_activity = MAX(last_activity, ?)
                        WHERE username = ?
                    """, (datetime.fromtimestamp(post.created_utc), post.author.name))
                    
            except sqlite3.IntegrityError:
                # Post already exists, update scores
                cursor.execute("""
                    UPDATE posts SET score = ?, num_comments = ?
                    WHERE id = ?
                """, (post.score, post.num_comments, post.id))
                
    def _save_comment(self, comment, post_id: str):
        """Save comment to database"""
        with self.db.connect() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO comments
                    (id, reddit_id, post_id, parent_id, author, body, score, created_utc)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    comment.id,
                    f"t1_{comment.id}",
                    post_id,
                    comment.parent_id,
                    comment.author.name if comment.author else '[deleted]',
                    comment.body,
                    comment.score,
                    datetime.fromtimestamp(comment.created_utc)
                ))
                
                # Update user comment count
                if comment.author:
                    cursor.execute("""
                        UPDATE users SET comment_count = comment_count + 1,
                        last_activity = MAX(last_activity, ?)
                        WHERE username = ?
                    """, (datetime.fromtimestamp(comment.created_utc), comment.author.name))
                    
            except sqlite3.IntegrityError:
                # Comment exists, update score
                cursor.execute("""
                    UPDATE comments SET score = ? WHERE id = ?
                """, (comment.score, comment.id))
                
    def _create_user_records(self, usernames: Set[str], platform: str):
        """Create user records for new users with platform assignment"""
        with self.db.connect() as conn:
            cursor = conn.cursor()
            
            for username in usernames:
                if username == '[deleted]':
                    continue
                    
                # Try to insert new user with platform
                cursor.execute("""
                    INSERT INTO users (username, platform, found_in_subreddits)
                    VALUES (?, ?, ?)
                    ON CONFLICT(username) DO UPDATE SET
                    found_in_subreddits = CASE
                        WHEN found_in_subreddits IS NULL THEN ?
                        WHEN json_extract(found_in_subreddits, '$') NOT LIKE '%' || ? || '%' 
                        THEN json_insert(found_in_subreddits, '$[#]', ?)
                        ELSE found_in_subreddits
                    END
                """, (username, platform, json.dumps([platform]), 
                      json.dumps([platform]), platform, platform))
                
    def enrich_users(self, limit: int = 100) -> int:
        """Enrich user data from Reddit API"""
        users_to_enrich = self.db.get_users_for_enrichment(limit)
        enriched_count = 0
        
        for username in users_to_enrich:
            try:
                user_data = self._fetch_reddit_user_data(username)
                if user_data:
                    self.db.upsert_user(user_data)
                    enriched_count += 1
                    
                # Rate limiting
                time.sleep(self.rate_limit)
                
                if enriched_count % 10 == 0:
                    logger.info(f"Enriched {enriched_count}/{len(users_to_enrich)} users")
                    
            except Exception as e:
                logger.error(f"Error enriching user {username}: {e}")
                
        return enriched_count
        
    def _fetch_reddit_user_data(self, username: str) -> Optional[Dict]:
        """Fetch user data from Reddit API"""
        try:
            user = self.reddit.redditor(username)
            
            # Try to access user data to check if account exists
            created_utc = user.created_utc
            
            user_data = {
                'username': username,
                'reddit_id': user.id,
                'account_created': datetime.fromtimestamp(created_utc),
                'link_karma': user.link_karma,
                'comment_karma': user.comment_karma,
                'total_karma': user.link_karma + user.comment_karma,
                'has_verified_email': getattr(user, 'has_verified_email', None),
                'is_mod': getattr(user, 'is_mod', False),
                'is_suspended': False,
                'last_reddit_api_check': datetime.now()
            }
            
            # Get recent activity
            recent_activity = None
            for item in user.new(limit=1):
                recent_activity = datetime.fromtimestamp(item.created_utc)
                break
                
            if recent_activity:
                user_data['last_activity'] = recent_activity
                
            return user_data
            
        except Exception as e:
            if '404' in str(e) or 'not found' in str(e).lower():
                # User doesn't exist or is suspended
                return {
                    'username': username,
                    'is_suspended': True,
                    'last_reddit_api_check': datetime.now()
                }
            else:
                logger.error(f"Error fetching user {username}: {e}")
                return None

def main():
    """Run collector manually"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Reddit Data Collector')
    parser.add_argument('--incremental', action='store_true', 
                       help='Only collect new content')
    parser.add_argument('--subreddit', type=str, 
                       help='Collect from specific subreddit only')
    parser.add_argument('--platform', type=str,
                       help='Platform name for the subreddit (defaults to subreddit name)')
    parser.add_argument('--enrich-only', action='store_true',
                       help='Only enrich user data')
    parser.add_argument('--limit', type=int, default=100,
                       help='Limit for enrichment')
    
    args = parser.parse_args()
    
    collector = RedditCollector()
    
    if args.enrich_only:
        enriched = collector.enrich_users(args.limit)
        print(f"Enriched {enriched} users")
    elif args.subreddit:
        platform = args.platform or args.subreddit
        # Add to monitored subreddits if not exists
        collector.db.add_monitored_subreddit(args.subreddit, platform)
        items = collector.collect_subreddit(args.subreddit, platform, args.incremental)
        print(f"Collected {items} items from r/{args.subreddit}")
    else:
        collector.collect_all(args.incremental)
        
if __name__ == "__main__":
    main()