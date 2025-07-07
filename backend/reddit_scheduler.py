#!/usr/bin/env python3
"""
Reddit Lead Generation Scheduler
Handles automated daily runs, maintenance, and monitoring
"""

import os
import sys
import logging
import shutil
import json
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import subprocess
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

from config_loader import config
from database_schema import RedditDatabase
from reddit_collector import RedditCollector
from reddit_analyzer import RedditAnalyzer

logging.basicConfig(
    level=getattr(logging, config.get('logging.level', 'INFO')),
    format=config.get('logging.format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
    handlers=[
        logging.FileHandler(config.get('logging.file', 'reddit_leads.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RedditScheduler:
    def __init__(self):
        self.config = config
        self.db = RedditDatabase(config.database_path)
        self.collector = RedditCollector()
        self.analyzer = RedditAnalyzer()
        
    def run_daily(self):
        """Execute daily collection and analysis workflow"""
        logger.info("Starting daily Reddit lead generation run")
        start_time = datetime.now()
        
        try:
            # Backup database before starting
            if config.get('database.backup_enabled', True):
                self._backup_database()
                
            # Run collection (incremental by default)
            logger.info("Phase 1: Data Collection")
            self.collector.collect_all(incremental=config.get('scheduler.incremental_scrape', True))
            
            # Run analysis
            logger.info("Phase 2: User Analysis")
            self.analyzer.analyze_all()
            
            # Cleanup old data
            logger.info("Phase 3: Data Cleanup")
            self._cleanup_old_data()
            
            # Generate stats
            stats = self._generate_run_stats(start_time)
            
            # Send notifications
            if config.get('scheduler.notifications.enabled', False):
                self._send_notification("Daily run completed", stats)
                
            logger.info(f"Daily run completed successfully in {datetime.now() - start_time}")
            
        except Exception as e:
            logger.error(f"Daily run failed: {e}")
            
            # Send error notification
            if config.get('scheduler.notifications.enabled', False):
                self._send_notification("Daily run failed", str(e), is_error=True)
                
            raise
            
    def run_full_refresh(self):
        """Run full data refresh - scrapes all data and re-analyzes"""
        logger.info("Starting full refresh")
        
        try:
            # Backup first
            self._backup_database()
            
            # Run full collection
            self.collector.collect_all(incremental=False)
            
            # Run full analysis
            self.analyzer.analyze_all(force=True)
            
            logger.info("Full refresh completed")
            
        except Exception as e:
            logger.error(f"Full refresh failed: {e}")
            raise
            
    def _backup_database(self):
        """Create database backup"""
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        # Create timestamped backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"reddit_leads_{timestamp}.db"
        
        shutil.copy2(config.database_path, backup_path)
        logger.info(f"Database backed up to {backup_path}")
        
        # Cleanup old backups
        backup_count = config.get('database.backup_count', 7)
        backups = sorted(backup_dir.glob("reddit_leads_*.db"))
        
        if len(backups) > backup_count:
            for old_backup in backups[:-backup_count]:
                old_backup.unlink()
                logger.info(f"Removed old backup: {old_backup}")
                
    def _cleanup_old_data(self):
        """Clean up old data based on retention policy"""
        retention_days = config.get('scheduler.retention_days', 90)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        with self.db.connect() as conn:
            cursor = conn.cursor()
            
            # Remove old analysis runs
            cursor.execute("""
                DELETE FROM analysis_runs 
                WHERE started_at < ?
            """, (cutoff_date,))
            
            deleted_runs = cursor.rowcount
            
            # Archive old posts/comments if needed
            archive_days = config.get('scheduler.archive_after_days', 365)
            if archive_days:
                archive_date = datetime.now() - timedelta(days=archive_days)
                # In a real system, you'd move to archive tables
                # For now, we'll just log what would be archived
                cursor.execute("""
                    SELECT COUNT(*) FROM posts WHERE created_utc < ?
                """, (archive_date,))
                
                archive_count = cursor.fetchone()[0]
                if archive_count > 0:
                    logger.info(f"Would archive {archive_count} old posts")
                    
        logger.info(f"Cleanup completed: removed {deleted_runs} old analysis runs")
        
    def _generate_run_stats(self, start_time: datetime) -> str:
        """Generate statistics for the run"""
        with self.db.connect() as conn:
            cursor = conn.cursor()
            
            # Get user stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_users,
                    COUNT(CASE WHEN lead_score > 70 THEN 1 END) as high_quality_leads,
                    COUNT(CASE WHEN creator_likelihood > 50 THEN 1 END) as likely_creators,
                    AVG(lead_score) as avg_lead_score
                FROM users
                WHERE last_updated > ?
            """, (start_time,))
            
            user_stats = dict(cursor.fetchone())
            
            # Get collection stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as new_posts,
                    COUNT(DISTINCT author) as unique_authors
                FROM posts
                WHERE scraped_at > ?
            """, (start_time,))
            
            post_stats = dict(cursor.fetchone())
            
        duration = datetime.now() - start_time
        
        stats = f"""
Daily Run Statistics:
====================
Duration: {duration}
New Posts Collected: {post_stats['new_posts']}
Unique Authors: {post_stats['unique_authors']}
Users Analyzed: {user_stats['total_users']}
High Quality Leads: {user_stats['high_quality_leads']}
Likely Creators: {user_stats['likely_creators']}
Average Lead Score: {user_stats['avg_lead_score']:.1f}
"""
        
        return stats
        
    def _send_notification(self, subject: str, body: str, is_error: bool = False):
        """Send notification via configured channel"""
        # Webhook notification (Slack/Discord)
        webhook_url = config.get('scheduler.notifications.webhook_url')
        if webhook_url:
            self._send_webhook(webhook_url, subject, body, is_error)
            
        # Email notification
        email_config = {
            'to': config.get('scheduler.notifications.email_to'),
            'from': config.get('scheduler.notifications.email_from'),
            'smtp_host': config.get('scheduler.notifications.smtp_host'),
            'smtp_port': config.get('scheduler.notifications.smtp_port'),
            'smtp_user': config.get('scheduler.notifications.smtp_user'),
            'smtp_pass': config.get('scheduler.notifications.smtp_pass'),
        }
        
        if all(email_config.values()):
            self._send_email(subject, body, is_error, email_config)
            
    def _send_webhook(self, url: str, subject: str, body: str, is_error: bool):
        """Send webhook notification"""
        try:
            # Format for Slack/Discord
            color = "#ff0000" if is_error else "#00ff00"
            
            payload = {
                "attachments": [{
                    "color": color,
                    "title": subject,
                    "text": body,
                    "footer": "Reddit Lead Generation",
                    "ts": int(datetime.now().timestamp())
                }]
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
            
    def _send_email(self, subject: str, body: str, is_error: bool, config: dict):
        """Send email notification"""
        try:
            msg = MIMEMultipart()
            msg['Subject'] = f"[Reddit Leads] {subject}"
            msg['From'] = config['from']
            msg['To'] = config['to']
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(config['smtp_host'], config['smtp_port']) as server:
                server.starttls()
                server.login(config['smtp_user'], config['smtp_pass'])
                server.send_message(msg)
                
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            
    def generate_cron_entry(self) -> str:
        """Generate cron entry for daily runs"""
        run_time = config.get('scheduler.daily_run_time', '02:00')
        hour, minute = run_time.split(':')
        
        python_path = sys.executable
        script_path = os.path.abspath(__file__)
        
        cron_entry = f"{minute} {hour} * * * {python_path} {script_path} --mode=daily >> /var/log/reddit_leads.log 2>&1"
        
        return cron_entry
        
    def install_cron(self):
        """Install cron job for daily runs"""
        cron_entry = self.generate_cron_entry()
        
        print("Add the following line to your crontab (crontab -e):")
        print(cron_entry)
        print("\nOr run: python reddit_scheduler.py --mode=daily")
        print("to test the daily run manually")

def main():
    """Run scheduler with command line arguments"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Reddit Lead Generation Scheduler')
    parser.add_argument('--mode', choices=['daily', 'full', 'cron'],
                       default='daily',
                       help='Run mode: daily (incremental), full (complete refresh), cron (show cron entry)')
    
    args = parser.parse_args()
    
    scheduler = RedditScheduler()
    
    if args.mode == 'daily':
        scheduler.run_daily()
    elif args.mode == 'full':
        scheduler.run_full_refresh()
    elif args.mode == 'cron':
        scheduler.install_cron()
        
if __name__ == "__main__":
    main()