#!/bin/bash

# Make script executable and set up local cron job for testing
# This is useful for local development before using GitHub Actions

# Check if script is being run with sudo
if [ "$EUID" -ne 0 ]; then
  echo "Please run with sudo: sudo $0"
  exit 1
fi

# Get the absolute path of the current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Make the Python script executable
chmod +x "$SCRIPT_DIR/blog_automation.py"

# Create a temporary cron file
TEMP_CRON=$(mktemp)

# Export current crontab
crontab -l > "$TEMP_CRON" 2>/dev/null || true

# Check if entry already exists
if grep -q "blog_automation.py" "$TEMP_CRON"; then
    echo "Cron job for blog automation already exists."
else
    # Add new cron job to run daily at 10:00 AM (adjust time as needed)
    echo "0 10 * * * cd $SCRIPT_DIR && python blog_automation.py --headless >> $SCRIPT_DIR/logs/cron_execution.log 2>&1" >> "$TEMP_CRON"
    
    # Install new crontab
    crontab "$TEMP_CRON"
    echo "Cron job added successfully. Blog posts will be created daily at 10:00 AM."
fi

# Clean up
rm "$TEMP_CRON"

echo "Setup complete! You can test the script manually with: python $SCRIPT_DIR/blog_automation.py"