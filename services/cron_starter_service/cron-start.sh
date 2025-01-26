#!/bin/bash
set -u

# Create log directory
[ ! -f /var/log/cron.log ] && touch /var/log/cron.log

# Create crontab file
cat /dev/null > /etc/crontabs/root

# Directly use cron jobs from /etc/crontabs/root (already mounted)
echo "> Using cron jobs from /etc/crontabs/root"

# Create logrotate configuration file
cat << EOF > /etc/logrotate.d/cron_logs
/var/log/cron.log {
    size 10M
    rotate 5
    missingok
    notifempty
    compress
    delaycompress
    create 0644 root root
    postrotate
        /usr/bin/killall -HUP crond
    endscript
}
EOF

# Add logrotate scheduled task to crontab
echo "0 * * * * /usr/sbin/logrotate /etc/logrotate.d/cron_logs" >> /etc/crontabs/root

# Start crond and keep it running in the foreground, while outputting logs
crond

# Continuously output all log files
exec tail -f /var/log/cron.log