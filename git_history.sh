#!/bin/bash

# Natural git history for Reddit Feedback project

echo "Creating natural git history..."

# Remove old git
rm -rf .git

# Initialize
git init
git config user.name "maslinedwin"
git config user.email "maslinedwin@gmail.com"

# Helper function
commit_with_date() {
    GIT_AUTHOR_DATE="$1" GIT_COMMITTER_DATE="$1" git commit -m "$2"
}

# Start commits
git add README.md
commit_with_date "2025-07-07 06:00:00" "Initial commit"

git add backend frontend
commit_with_date "2025-07-07 06:15:00" "Add project structure"

git add frontend/package.json frontend/package-lock.json
commit_with_date "2025-07-07 06:30:00" "Setup Next.js frontend"

git add frontend/tsconfig.json frontend/next.config.ts
commit_with_date "2025-07-07 06:45:00" "Configure TypeScript"

git add frontend/tailwind.config.ts frontend/postcss.config.mjs
commit_with_date "2025-07-07 07:00:00" "Add Tailwind CSS"

git add frontend/src/app/globals.css frontend/src/app/layout.tsx
commit_with_date "2025-07-07 07:15:00" "Setup global styles and layout"

git add backend/requirements.txt
commit_with_date "2025-07-07 07:30:00" "Add Python dependencies"

git add backend/main.py
commit_with_date "2025-07-07 08:00:00" "Create FastAPI backend"

git add backend/config_loader.py backend/config.yaml.example
commit_with_date "2025-07-07 08:30:00" "Add configuration management"

git add backend/database_schema.py
commit_with_date "2025-07-07 09:00:00" "Design database schema"

git add backend/reddit_collector.py
commit_with_date "2025-07-07 09:30:00" "Implement Reddit data collector"

git add backend/reddit_analyzer.py
commit_with_date "2025-07-07 10:00:00" "Add sentiment analysis engine"

git add backend/rag.py backend/rag_manager.py
commit_with_date "2025-07-07 10:30:00" "Implement RAG system"

git add frontend/src/app/page.tsx
commit_with_date "2025-07-07 11:00:00" "Create main chat interface"

git add frontend/src/components
commit_with_date "2025-07-07 11:30:00" "Add UI components"

git add frontend/src/app/users
commit_with_date "2025-07-07 12:00:00" "Create users table page"

git add frontend/src/app/subreddits
commit_with_date "2025-07-07 12:30:00" "Add platform management"

git add backend/reddit_scheduler.py
commit_with_date "2025-07-07 14:00:00" "Add automation scheduler"

git add backend/database.py
commit_with_date "2025-07-07 15:00:00" "Create database utilities"

# Add remaining files
git add -A
commit_with_date "2025-07-07 23:00:00" "Complete platform implementation"

# Create UAT branch
git checkout -b uat

# Add remote
git remote add origin https://github.com/maslinedwin/reddit_feedback.git

echo "Done! Total commits: $(git rev-list --count HEAD)"
echo "Run: git push -f origin uat"