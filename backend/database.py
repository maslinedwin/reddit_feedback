import pandas as pd
import os
import json

DATA_FILE = "reddit_data.csv"
USER_ANALYSIS_FILE = "user_analysis.csv"

def save_data(data):
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
    else:
        df = pd.DataFrame()
    
    new_df = pd.DataFrame(data)
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

def get_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame()

def save_user_analysis(users_data):
    """Save analyzed user data to CSV"""
    df = pd.DataFrame(users_data)
    df.to_csv(USER_ANALYSIS_FILE, index=False)
    return True

def get_user_analysis():
    """Get analyzed user data directly from database"""
    import sqlite3
    
    try:
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
        
        df = pd.read_sql_query(query, conn)
        
        # Parse JSON strings back to lists for main_topics
        def parse_topics(x):
            if pd.isna(x) or x == '' or x == '[]':
                return []
            try:
                return json.loads(x)
            except:
                return []
        
        df['main_topics'] = df['main_topics'].apply(parse_topics)
        
        # Clean up summary field
        df['summary'] = df['summary'].str.replace('\n', ' ').str.replace('"', "'")
        
        conn.close()
        return df
        
    except Exception as e:
        print(f"Error loading user data: {e}")
        return pd.DataFrame()

def update_user_analysis(username, data):
    """Update specific user analysis"""
    df = get_user_analysis()
    if not df.empty:
        # Update existing user or append new one
        user_index = df[df['username'] == username].index
        if len(user_index) > 0:
            for key, value in data.items():
                df.at[user_index[0], key] = value
        else:
            # Add new user
            df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
        
        # Save back to CSV (convert lists to JSON)
        df_save = df.copy()
        df_save['main_topics'] = df_save['main_topics'].apply(lambda x: json.dumps(x) if isinstance(x, list) else x)
        df_save.to_csv(USER_ANALYSIS_FILE, index=False)
        return True
    return False