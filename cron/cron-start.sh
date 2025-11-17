#!/bin/bash
set -u

# Write the cron jobs (already mounted)
echo "> Applying cron jobs"

# Create logrotate configuration file
cat << EOF > /etc/logrotate.d/cron_logs
/var/log/* {
    size 1M
    rotate 5
    missingok
    notifempty
    compress
    delaycompress
    su root root
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
