#!/bin/bash

# Get the absolute path to the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/cron_execution.log"

# Create a temporary file for the new crontab
TEMP_CRON=$(mktemp)

# Export current crontab
crontab -l > "$TEMP_CRON" 2>/dev/null || echo "# Blog Automation Crontab" > "$TEMP_CRON"

# Check if our job is already in the crontab
if ! grep -q "blog_automation.py" "$TEMP_CRON"; then
    # Add our job to run daily at 10:00 AM
    echo "# Run blog automation daily at 10:00 AM" >> "$TEMP_CRON"
    echo "0 10 * * * cd $SCRIPT_DIR && /usr/bin/python3 $SCRIPT_DIR/blog_automation.py >> $LOG_FILE 2>&1" >> "$TEMP_CRON"
    
    # Install the new crontab
    crontab "$TEMP_CRON"
    echo "Cron job added successfully. Blog posts will be created daily at 10:00 AM."
else
    echo "Cron job already exists."
fi

# Clean up
rm "$TEMP_CRON"

echo ""
echo "To check your current crontab, run: crontab -l"
echo "To edit your crontab manually, run: crontab -e"