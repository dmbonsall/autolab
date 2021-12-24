#!/bin/sh
# ===== Copy the start script =====
cp ./start.sh /usr/local/bin/autolab-start
chmod 755 /usr/local/bin/autolab-start

# ===== Copy the systemd unit file =====
cp ./autolab.service /etc/systemd/system/
chmod 664 /etc/systemd/system/autolab.service

systemctl daemon-reload
systemctl enable autolab.service
systemctl start autolab.service
