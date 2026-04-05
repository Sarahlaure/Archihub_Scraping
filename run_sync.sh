#!/bin/bash

# AI/ML Innovation Pilot - Automation Trigger
# This script syncs the latest news and prepares the dashboard.

echo "🚀 Starting Intelligence Sync..."
source venv/bin/activate
python3 tools/scraper.py

if [ $? -eq 0 ]; then
    echo "✅ Sync Complete. Dashboard updated."
    mkdir -p public
    cp .tmp/articles.json public/articles.json
    echo "🌐 Run 'npm run dev' to view the modern dashboard at http://localhost:3000"
else
    echo "❌ Sync Failed. Check logs in progress.md"
    exit 1
fi
