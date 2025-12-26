#!/bin/bash

# Navigate to your project directory on the AWS server
cd /home/ubuntu/finance-dashboard-quant

# Log the execution timestamp to a specific log file for monitoring
echo "Cron job execution started at $(date)" >> /home/ubuntu/finance-dashboard-quant/cron/cron_log.txt

# Execute the script using the standard Python3 interpreter installed on Ubuntu
/usr/bin/python3 cron/daily_report.py >> /home/ubuntu/finance-dashboard-quant/cron/cron_log.txt 2>&1
