#!/bin/bash

# Navigate to the project root directory to ensure Python module imports resolve correctly
cd /workspaces/finance-dashboard-quant

# Log the execution timestamp for monitoring and debugging purposes
echo "Cron job execution started at $(date)"

# Execute the daily report generator using the project-specific Python interpreter
/home/codespace/.python/current/bin/python cron/daily_report.py
