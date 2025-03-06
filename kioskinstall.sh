#!/bin/sh

echo "adding something to a file....."

sudo su

# Append Chromium Kiosk Command to .service file
echo "ExecStart=/usr/bin/chromium-browser --noerrdialogs --kiosk http://localhost" >> /home/%user/.config/systemd/binderly-kiosk.service

# Hopefully make cursor invisible
apt install unclutter
echo "ExecStartPre=/usr/bin/unclutter -idle 0" >> /home/%user/.config/systemd/binderly-kiosk.service

# ----random notes----

# Uncomment the following line to install Chromium browser if needed
# apt install chromium-browser

# This is the command to run chromium in kiosk mode. so make sure this works before leaving.
# chromium-browser --noerrdialogs --kiosk http://localhost

# home/%user/.config/systemd/binderly-kiosk.service
