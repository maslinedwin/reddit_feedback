"""
Reddit Data Analyzer - Analysis and intelligence engine
Performs sentiment analysis, creator detection, and lead scoring
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from collections import Counter
import json

from config_loader import config
from database_schema import RedditDatabase

logging.basicConfig(
    level=getattr(logging, config.get('logging.level', 'INFO')),
    format=config.get('logging.format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)
logger = logging.getLogger(__name__)

class RedditAnalyzer:
    def __init__(self):
        self.config = config
        self.db = RedditDatabase(config.database_path)
        
        # Load configuration
        self.creator_keywords = config.get_creator_keywords()
        self.positive_keywords = set(config.get('analysis.positive_keywords', []))
        self.negative_keywords = set(config.get('analysis.negative_keywords', []))
        self.lead_weights = config.get_lead_scoring_weights()
        
    def analyze_all(self, force: bool = False):
        """Main analysis method - analyzes all users needing updates"""
        run_id = self.db.log_analysis_run('analyze', {
            'force': force,
            'min_activity': config.get('analysis.min_activity_threshold', 5)
        })
        
        try:
            # Get users to analyze
            limit = 1000 if force else 200
            users = self.db.get_users_for_analysis(limit)
            
            logger.info(f"Analyzing {len(users)} users...")
            analyzed_count = 0
            
            for username in users:
                try:
                    self.analyze_user(username)
                    analyzed_count += 1
                    
                    if analyzed_count % 50 == 0:
                        logger.info(f"Progress: {analyzed_count}/{len(users)} users analyzed")
                        
                except Exception as e:
                    logger.error(f"Error analyzing user {username}: {e}")
                    
            self.db.update_analysis_run(run_id, 'completed', analyzed_count)
            logger.info(f"Analysis completed: {analyzed_count} users analyzed")
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            self.db.update_analysis_run(run_id, 'failed', 0, str(e))
            raise
            
    def analyze_user(self, username: str):
        """Analyze a single user"""
        # Get user data
        user = self.db.get_user(username)
        if not user:
            logger.warning(f"User {username} not found")
            return
            
        # Get user's posts and comments
        with self.db.connect() as conn:
            cursor = conn.cursor()
            
            # Get posts
            cursor.execute("""
                SELECT id, title, selftext, score, created_utc
                FROM posts WHERE author = ?
                ORDER BY created_utc DESC
            """, (username,))
            posts = [dict(row) for row in cursor.fetchall()]
            
            # Get comments
            cursor.execute("""
                SELECT c.id, c.body, c.score, c.created_utc, 
                       p.title as post_title, c.parent_id
                FROM comments c
                JOIN posts p ON c.post_id = p.id
                WHERE c.author = ?
                ORDER BY c.created_utc DESC
            """, (username,))
            comments = [dict(row) for row in cursor.fetchall()]
            
        # Analyze content
        all_text = self._get_user_text(posts, comments)
        
        # Perform analyses
        sentiment, rating = self._analyze_platform_sentiment(all_text)
        creator_likelihood = self._calculate_creator_likelihood(all_text)
        discussion_score = self._calculate_discussion_starter_score(posts, comments)
        main_topics = self._extract_topics(all_text)
        summary = self._generate_summary(posts, comments)
        lead_score = self._calculate_lead_score(
            creator_likelihood, discussion_score, sentiment, rating,
            user.get('total_karma', 0), len(posts) + len(comments)
        )
        
        # Update user record
        self.db.upsert_user({
            'username': username,
            'platform_sentiment': sentiment,  # Changed from patreon_sentiment
            'platform_rating': rating,  # Changed from patreon_rating
            'creator_likelihood': creator_likelihood,
            'discussion_starter_score': discussion_score,
            'main_topics': main_topics,
            'summary': summary,
            'lead_score': lead_score,
            'analysis_version': 3  # Track analysis version
        })
        
    def _get_user_text(self, posts: List[Dict], comments: List[Dict]) -> str:
        """Combine all user text for analysis"""
        text_parts = []
        
        for post in posts:
            text_parts.append(post['title'])
            if post.get('selftext'):
                text_parts.append(post['selftext'])
                
        for comment in comments:
            text_parts.append(comment['body'])
            
        return ' '.join(text_parts).lower()
        
    def _analyze_platform_sentiment(self, text: str) -> Tuple[str, float]:
        """Analyze sentiment toward monetization platforms"""
        # Count sentiment indicators
        positive_count = sum(1 for word in self.positive_keywords if word in text)
        negative_count = sum(1 for word in self.negative_keywords if word in text)
        
        # Calculate base sentiment
        total_indicators = positive_count + negative_count
        
        if total_indicators == 0:
            # No clear sentiment indicators
            if '?' in text and len(text) < 500:
                return 'neutral', 5.0
            else:
                return 'neutral', 5.0
                
        # Calculate sentiment score
        sentiment_score = 5.0  # Base score
        
        if positive_count > negative_count:
            sentiment_score = 5.0 + (positive_count / total_indicators) * 5.0
            sentiment_type = 'positive' if negative_count == 0 else 'mixed'
        elif negative_count > positive_count:
            sentiment_score = 5.0 - (negative_count / total_indicators) * 4.0
            sentiment_type = 'negative' if positive_count == 0 else 'mixed'
        else:
            sentiment_type = 'neutral'
            
        # Clamp score
        sentiment_score = max(1.0, min(10.0, sentiment_score))
        
        return sentiment_type, round(sentiment_score, 1)
        
    def _calculate_creator_likelihood(self, text: str) -> float:
        """Calculate likelihood that user is a creator (0-100)"""
        if not text:
            return 0.0
            
        score = 0.0
        matches = 0
        
        # Check for creator keywords
        for keyword, weight in self.creator_keywords.items():
            if keyword.lower() in text:
                score += weight
                matches += 1
                
        # Additional patterns for any creator platform
        creator_patterns = [
            (r'\bmy (youtube|twitch|podcast|blog|channel)\b', 8),
            (r'\b(subscribe|follow) (to )?my\b', 9),
            (r'\bsupport (me|my)\b', 8),
            (r'\bi (create|make|produce|upload)\b', 6),
            (r'\bmy (fans|audience|viewers|readers|supporters)\b', 7),
            # Platform-specific patterns
            (r'\b(patreon|kofi|ko-fi|buymeacoffee|gumroad|onlyfans|substack)\.com/\w+\b', 10),
            (r'\bmy (patreon|kofi|onlyfans|gumroad|substack)\b', 10),
            (r'\b(tip|donate|support) (on|via|through)\b', 7),
            (r'\bexclusive content\b', 6),
            (r'\bmonthly subscription\b', 7),
        ]
        
        for pattern, weight in creator_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                score += weight
                matches += 1
                
        # Normalize to 0-100 scale
        if matches == 0:
            return 0.0
            
        # Cap at 100 and apply diminishing returns
        likelihood = min(100, score * (10 / matches))
        
        return round(likelihood, 1)
        
    def _calculate_discussion_starter_score(self, posts: List[Dict], 
                                          comments: List[Dict]) -> float:
        """Calculate how often user starts discussions"""
        if not posts:
            return 0.0
            
        # Calculate average engagement per post
        total_engagement = sum(p.get('score', 0) + p.get('num_comments', 0) * 2 
                              for p in posts)
        avg_engagement = total_engagement / len(posts) if posts else 0
        
        # Calculate post frequency
        if posts:
            first_post = min(posts, key=lambda p: p['created_utc'])
            last_post = max(posts, key=lambda p: p['created_utc'])
            
            first_date = datetime.fromisoformat(first_post['created_utc'])
            last_date = datetime.fromisoformat(last_post['created_utc'])
            
            days_active = max(1, (last_date - first_date).days)
            post_frequency = len(posts) / days_active * 30  # Posts per month
        else:
            post_frequency = 0
            
        # Combine metrics
        score = (avg_engagement * 0.7) + (post_frequency * 10 * 0.3)
        
        # Cap at 100
        return min(100, round(score, 1))
        
    def _extract_topics(self, text: str) -> List[str]:
        """Extract main discussion topics"""
        # Common words to exclude
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'under', 'again',
            'further', 'then', 'once', 'that', 'this', 'i', 'me', 'my', 'myself',
            'we', 'you', 'your', 'he', 'she', 'it', 'they', 'them', 'their',
            'what', 'which', 'who', 'when', 'where', 'why', 'how', 'is', 'are',
            'was', 'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does',
            'did', 'will', 'would', 'should', 'could', 'may', 'might', 'must',
            'can', 'just', 'now', 'than', 'very', 'some', 'all', 'any', 'more',
            'most', 'other', 'such', 'only', 'own', 'same', 'so', 'too', 'also'
        }
        
        # Extract words
        words = re.findall(r'\b[a-z]+\b', text)
        
        # Filter and count
        word_counts = Counter(w for w in words 
                            if len(w) > 3 and w not in stop_words)
        
        # Get top topics
        topics = []
        for word, count in word_counts.most_common(5):
            if count >= 3:  # Mentioned at least 3 times
                topics.append(word)
                
        return topics
        
    def _generate_summary(self, posts: List[Dict], comments: List[Dict]) -> str:
        """Generate user activity summary"""
        summaries = []
        
        # Post summary
        if posts:
            post_topics = ' '.join(p['title'][:50] for p in posts[:3])
            summaries.append(f"Created {len(posts)} posts discussing: {post_topics}...")
            
        # Comment summary
        if comments:
            # Count agreements
            agreements = sum(1 for c in comments 
                           if any(word in c['body'].lower() 
                                 for word in ['agree', 'same', 'exactly', 'this']))
            
            summaries.append(f"Made {len(comments)} comments, agreed {agreements} times")
            
            # Add sample interactions
            for comment in comments[:2]:
                if len(comment['body']) > 20:
                    action = "Agreed with" if any(word in comment['body'].lower() 
                                                 for word in ['agree', 'same']) else "Commented on"
                    summaries.append(f"{action} post about '{comment['post_title'][:50]}...'")
                    
        return " | ".join(summaries) if summaries else "No significant activity found"
        
    def _calculate_lead_score(self, creator_likelihood: float,
                             discussion_score: float,
                             sentiment: str, rating: float,
                             karma: int, activity_count: int) -> float:
        """Calculate overall lead quality score (0-100)"""
        weights = self.lead_weights
        
        # Normalize inputs
        sentiment_score = {
            'positive': 100,
            'mixed': 60,
            'neutral': 40,
            'negative': 20
        }.get(sentiment, 50)
        
        rating_normalized = rating * 10  # 0-100 scale
        karma_score = min(100, karma / 100)  # 10k karma = 100
        activity_score = min(100, activity_count * 2)  # 50 activities = 100
        
        # Calculate weighted score
        score = (
            creator_likelihood * weights.get('creator_likelihood_weight', 0.4) +
            discussion_score * weights.get('discussion_starter_weight', 0.2) +
            sentiment_score * weights.get('sentiment_weight', 0.2) +
            karma_score * weights.get('karma_weight', 0.1) +
            activity_score * weights.get('activity_weight', 0.1)
        )
        
        return round(score, 1)

def main():
    """Run analyzer manually"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Reddit Data Analyzer')
    parser.add_argument('--force', action='store_true',
                       help='Force re-analysis of all users')
    parser.add_argument('--user', type=str,
                       help='Analyze specific user only')
    
    args = parser.parse_args()
    
    analyzer = RedditAnalyzer()
    
    if args.user:
        analyzer.analyze_user(args.user)
        print(f"Analyzed user: {args.user}")
    else:
        analyzer.analyze_all(args.force)
        
if __name__ == "__main__":
    main()