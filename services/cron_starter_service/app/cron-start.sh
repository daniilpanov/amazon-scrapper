#!/bin/bash
set -u

# Directly use cron jobs from /etc/crontabs/* and /etc/cron.d/* (already mounted)
echo "> Using cron jobs from /etc/crontabs/* and /etc/cron.d/*"

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

echo 'Copy the user cron tasks to the system';

#for d in /res/crontabs/* ; do
#    cat "$d" >> /var/spool/cron/crontabs/root
#done
cat /res/crontabs/root > /var/spool/cron/crontabs/root;

echo 'Start crond';

# Start crond and keep it running in the foreground, while outputting logs
crond -f -l 7 -d > /var/log/cron.log;

echo 'Crond stopped';

# Continuously output all log files
exec tail -f /var/log/cron.log;

echo 'Logs wrote';