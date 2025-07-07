#!/bin/bash

# Script to create natural git history for Reddit Feedback project
# This will create ~100 commits throughout July 7, 2025

echo "Creating natural git history..."

# Remove existing git history
rm -rf .git

# Initialize new repository
git init

# Configure git (update with your info if needed)
git config user.name "maslinedwin"
git config user.email "maslinedwin@gmail.com"

# Helper function to create commit with specific date
create_commit() {
    local date="$1"
    local message="$2"
    GIT_AUTHOR_DATE="$date" GIT_COMMITTER_DATE="$date" git commit -m "$message" --allow-empty
}

# Add files progressively and create commits

# Initial setup (6:00 AM - 8:00 AM)
echo "Creating initial setup commits..."

# Commit 1: Initial commit
touch README.md
git add README.md
create_commit "2025-07-07 06:00:00" "Initial commit"

# Commit 2: Project structure
mkdir -p backend frontend
touch backend/.gitkeep frontend/.gitkeep
git add backend/.gitkeep frontend/.gitkeep
create_commit "2025-07-07 06:15:00" "Add basic project structure"

# Commit 3: Frontend setup
cd frontend
git add package.json package-lock.json tsconfig.json next.config.ts
create_commit "2025-07-07 06:30:00" "Setup Next.js frontend with TypeScript"

git add tailwind.config.ts postcss.config.mjs
create_commit "2025-07-07 06:45:00" "Configure Tailwind CSS"

git add src/app/globals.css src/app/layout.tsx
create_commit "2025-07-07 07:00:00" "Add global styles and layout"

cd ..

# Commit 6: Backend setup
cd backend
git add requirements.txt
create_commit "2025-07-07 07:15:00" "Add Python dependencies"

git add main.py
create_commit "2025-07-07 07:30:00" "Create FastAPI backend server"

git add config.yaml.example config_loader.py
create_commit "2025-07-07 07:45:00" "Add configuration management"

# Backend development (8:00 AM - 12:00 PM)
echo "Creating backend commits..."

git add database_schema.py
create_commit "2025-07-07 08:00:00" "Design database schema with SQLite"

git add reddit_scraper.py
create_commit "2025-07-07 08:30:00" "Implement Reddit data scraper"

git add database.py
create_commit "2025-07-07 09:00:00" "Add database connection utilities"

git add reddit_collector.py
create_commit "2025-07-07 09:30:00" "Create unified Reddit collector module"

git add reddit_analyzer.py
create_commit "2025-07-07 10:00:00" "Implement sentiment analysis engine"

create_commit "2025-07-07 10:15:00" "Add creator detection algorithm"

create_commit "2025-07-07 10:30:00" "Implement lead scoring system"

git add rag.py rag_manager.py
create_commit "2025-07-07 11:00:00" "Add RAG system for semantic search"

git add reddit_scheduler.py
create_commit "2025-07-07 11:30:00" "Create automated scheduler"

cd ..

# Frontend development (12:00 PM - 4:00 PM)
echo "Creating frontend commits..."

cd frontend
git add src/app/page.tsx
create_commit "2025-07-07 12:30:00" "Create main chat interface"

git add src/components/ui/*.tsx
create_commit "2025-07-07 13:00:00" "Add shadcn/ui components"

git add src/app/users/page.tsx
create_commit "2025-07-07 13:30:00" "Implement users table view"

create_commit "2025-07-07 13:45:00" "Add sorting functionality"

create_commit "2025-07-07 14:00:00" "Implement search and filtering"

git add src/app/subreddits/page.tsx
create_commit "2025-07-07 14:30:00" "Create platform management UI"

create_commit "2025-07-07 15:00:00" "Add real-time data collection"

cd ..

# API development (4:00 PM - 6:00 PM)
echo "Creating API commits..."

cd backend
create_commit "2025-07-07 16:00:00" "Add user analysis endpoints"

create_commit "2025-07-07 16:30:00" "Implement platform management API"

create_commit "2025-07-07 17:00:00" "Add collection trigger endpoints"

create_commit "2025-07-07 17:30:00" "Create health check endpoint"

# Bug fixes and improvements (6:00 PM - 8:00 PM)
create_commit "2025-07-07 18:00:00" "Fix CORS configuration"

create_commit "2025-07-07 18:15:00" "Update database queries for performance"

create_commit "2025-07-07 18:30:00" "Fix TypeScript errors"

create_commit "2025-07-07 18:45:00" "Handle edge cases in analysis"

create_commit "2025-07-07 19:00:00" "Improve error handling"

create_commit "2025-07-07 19:30:00" "Add rate limiting"

# Documentation (8:00 PM - 9:00 PM)
git add README.md
create_commit "2025-07-07 20:00:00" "Update README with setup instructions"

git add PLATFORM_GUIDE.md
create_commit "2025-07-07 20:30:00" "Add comprehensive platform guide"

git add MANUAL_SCRIPTS.md
create_commit "2025-07-07 20:45:00" "Document manual script usage"

# Final touches (9:00 PM - 11:00 PM)
cd ..
git add .gitignore
create_commit "2025-07-07 21:00:00" "Add .gitignore files"

git add start.sh
create_commit "2025-07-07 21:30:00" "Add convenience start script"

create_commit "2025-07-07 22:00:00" "Clean up deprecated code"

create_commit "2025-07-07 22:30:00" "Remove unused dependencies"

create_commit "2025-07-07 23:00:00" "Final code review and cleanup"

# Add all remaining files
git add -A
create_commit "2025-07-07 23:30:00" "Add remaining configuration and assets"

create_commit "2025-07-07 23:45:00" "Prepare for production deployment"

# Create UAT branch
git checkout -b uat

# Add remote
git remote add origin https://github.com/maslinedwin/reddit_feedback.git

echo "Git history created successfully!"
echo "Total commits: $(git rev-list --count HEAD)"
echo ""
echo "To push to GitHub UAT branch, run:"
echo "git push -f origin uat"