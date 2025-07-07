#!/usr/bin/env python3
"""Export users from database to CSV for API"""

import sqlite3
import pandas as pd
import json

print("Exporting users from database...")

conn = sqlite3.connect('reddit_leads.db')

query = '''
SELECT 
    username,
    post_count,
    comment_count,
    COALESCE(total_karma, 0) AS total_score,
    COALESCE(platform, 'patreon') AS platform,
    COALESCE(platform_sentiment, 'neutral') AS platform_sentiment,
    COALESCE(platform_rating, 5.0) AS platform_rating,
    COALESCE(creator_likelihood, 0.0) AS creator_likelihood,
    COALESCE(discussion_starter_score, 0.0) AS discussion_starter_score,
    COALESCE(lead_score, 0.0) AS lead_score,
    COALESCE(main_topics, '[]') AS main_topics,
    COALESCE(summary, '') AS summary,
    'https://reddit.com/user/' || username AS reddit_profile_url,
    last_activity AS last_active_in_data,
    CASE 
        WHEN account_created IS NOT NULL 
        THEN CAST(julianday('now') - julianday(account_created) AS INTEGER) 
        ELSE 0 
    END AS account_age_days_in_data,
    account_created AS reddit_account_created,
    CASE 
        WHEN account_created IS NOT NULL 
        THEN CAST(julianday('now') - julianday(account_created) AS INTEGER) 
        ELSE NULL 
    END AS reddit_account_age_days,
    link_karma AS reddit_link_karma,
    comment_karma AS reddit_comment_karma,
    total_karma AS reddit_total_karma,
    last_activity AS reddit_last_active,
    CASE WHEN is_suspended = 0 THEN 1 ELSE 0 END AS is_active,
    CASE WHEN is_suspended = 1 THEN 'suspended' ELSE 'active' END AS account_status,
    last_updated
FROM users
WHERE (post_count + comment_count) > 0
ORDER BY lead_score DESC
'''

try:
    df = pd.read_sql_query(query, conn)
    
    # Clean up summary field
    df['summary'] = df['summary'].str.replace('\n', ' ').str.replace('"', "'")
    
    # Save to CSV
    df.to_csv('user_analysis.csv', index=False, quoting=1)
    print(f'Successfully exported {len(df)} users to user_analysis.csv')
    
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()