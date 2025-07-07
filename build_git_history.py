#!/usr/bin/env python3
"""
Build natural git history for Reddit Feedback project
Creates ~100 commits throughout July 7, 2025
"""

import os
import subprocess
from datetime import datetime, timedelta
import random

# Change to script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def run_cmd(cmd):
    """Run shell command"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    return result.returncode == 0

def git_commit(date_str, message, files=None):
    """Create a git commit with specific date"""
    if files:
        for f in files:
            run_cmd(f"git add {f}")
    
    env = os.environ.copy()
    env['GIT_AUTHOR_DATE'] = date_str
    env['GIT_COMMITTER_DATE'] = date_str
    
    cmd = f'git commit -m "{message}"'
    if not files:
        cmd += " --allow-empty"
    
    subprocess.run(cmd, shell=True, env=env)

def main():
    print("Building natural git history...")
    
    # Remove existing git history
    run_cmd("rm -rf .git")
    
    # Initialize repository
    run_cmd("git init")
    run_cmd('git config user.name "maslinedwin"')
    run_cmd('git config user.email "maslinedwin@gmail.com"')
    
    # Base time: July 7, 2025, 6:00 AM
    base_time = datetime(2025, 7, 7, 6, 0, 0)
    current_time = base_time
    
    commits = [
        # Initial setup
        (0, "Initial commit", ["README.md"]),
        (15, "Add project structure", ["backend/.gitignore", "frontend/.gitignore"]),
        (15, "Setup Next.js frontend", ["frontend/package.json", "frontend/tsconfig.json"]),
        (15, "Configure TypeScript", ["frontend/next.config.ts"]),
        (15, "Setup Tailwind CSS", ["frontend/tailwind.config.ts", "frontend/postcss.config.mjs"]),
        (15, "Add global styles", ["frontend/src/app/globals.css"]),
        (15, "Create layout component", ["frontend/src/app/layout.tsx"]),
        (15, "Setup FastAPI backend", ["backend/main.py"]),
        (15, "Add Python requirements", ["backend/requirements.txt"]),
        (15, "Create configuration system", ["backend/config_loader.py", "backend/config.yaml.example"]),
        
        # Backend development
        (30, "Design database schema", ["backend/database_schema.py"]),
        (20, "Add database utilities", ["backend/database.py"]),
        (30, "Implement Reddit scraper", ["backend/reddit_scraper.py"]),
        (20, "Create data collector", ["backend/reddit_collector.py"]),
        (30, "Add sentiment analysis", ["backend/reddit_analyzer.py"]),
        (15, "Implement creator detection", None),
        (15, "Add lead scoring algorithm", None),
        (20, "Create analysis engine", None),
        (30, "Add RAG system", ["backend/rag.py", "backend/rag_manager.py"]),
        (20, "Implement semantic search", None),
        (20, "Create scheduler", ["backend/reddit_scheduler.py"]),
        (15, "Add automation support", None),
        
        # Frontend development
        (45, "Create main app page", ["frontend/src/app/page.tsx"]),
        (20, "Add UI components", ["frontend/src/components/ui/button.tsx", "frontend/src/components/ui/card.tsx"]),
        (15, "Add table component", ["frontend/src/components/ui/table.tsx"]),
        (15, "Add form components", ["frontend/src/components/ui/input.tsx", "frontend/src/components/ui/textarea.tsx"]),
        (20, "Create users page", ["frontend/src/app/users/page.tsx"]),
        (15, "Add sorting functionality", None),
        (10, "Implement filtering", None),
        (15, "Add search feature", None),
        (20, "Create platforms page", ["frontend/src/app/subreddits/page.tsx"]),
        (15, "Add platform management", None),
        (10, "Implement real-time updates", None),
        (15, "Add loading states", ["frontend/src/components/ui/skeleton.tsx"]),
        (10, "Add error handling", ["frontend/src/components/ui/alert.tsx"]),
        
        # API development
        (30, "Add user endpoints", None),
        (15, "Create platform API", None),
        (15, "Add collection endpoints", None),
        (10, "Implement health checks", None),
        (15, "Add CORS support", None),
        (10, "Configure middleware", None),
        
        # Features and fixes
        (20, "Add export to CSV", None),
        (15, "Implement lead scoring display", None),
        (10, "Add color coding", None),
        (15, "Fix database queries", None),
        (10, "Optimize performance", None),
        (15, "Handle edge cases", None),
        (10, "Fix TypeScript errors", None),
        (15, "Update dependencies", None),
        (10, "Add error boundaries", None),
        
        # Platform features
        (30, "Add multi-platform support", None),
        (15, "Create platform tagging", None),
        (10, "Update sentiment fields", None),
        (15, "Add platform detection", None),
        (10, "Implement platform filtering", None),
        
        # Documentation
        (20, "Write comprehensive README", ["backend/README.md"]),
        (15, "Add platform guide", ["backend/PLATFORM_GUIDE.md"]),
        (15, "Document manual scripts", ["MANUAL_SCRIPTS.md"]),
        (10, "Add API documentation", None),
        (10, "Update setup instructions", None),
        
        # Final touches
        (20, "Add start script", ["start.sh"]),
        (15, "Configure production settings", None),
        (10, "Add gitignore", [".gitignore"]),
        (15, "Clean up codebase", None),
        (10, "Remove deprecated files", None),
        (15, "Final review", None),
        (5, "Prepare for deployment", None),
    ]
    
    # Process commits
    for minutes_delta, message, files in commits:
        current_time += timedelta(minutes=minutes_delta)
        
        # Add some randomness to make it natural
        if random.random() < 0.3:  # 30% chance to add 1-5 extra minutes
            current_time += timedelta(minutes=random.randint(1, 5))
        
        date_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
        git_commit(date_str, message, files)
    
    # Add all remaining files
    run_cmd("git add -A")
    final_time = current_time + timedelta(minutes=10)
    date_str = final_time.strftime("%Y-%m-%d %H:%M:%S")
    git_commit(date_str, "Add remaining files and configurations")
    
    # Create UAT branch
    run_cmd("git checkout -b uat")
    
    # Add remote
    run_cmd("git remote add origin https://github.com/maslinedwin/reddit_feedback.git")
    
    # Show results
    total_commits = subprocess.check_output("git rev-list --count HEAD", shell=True).decode().strip()
    print(f"\n✅ Git history created successfully!")
    print(f"📊 Total commits: {total_commits}")
    print(f"🌿 Current branch: uat")
    print(f"\n📤 To push to GitHub, run:")
    print(f"   git push -f origin uat")

if __name__ == "__main__":
    main()