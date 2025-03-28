#!/bin/bash
echo "Installing..."

#Navigate to "pi" user home, and ensure pi user
sudo -u pi -i
cd ~

#Acquire Root
sudo su

#Install Basic Packages
apt-get install python3
apt-get install python3-pip
apt-get install git

#Install Python Packages
pip install -r requirements.txt --break-system-packages

#Assemble Services
mv binderly-kiosk.service /home/pi/.config/systemd/user/
mv binderly-back.service /etc/systemd/system/

#Refresh & Enable Services
systemctl daemon-reload
systemctl enable binderly-back.service

#navigate back to pi
exit

#Refresh USER Services & Enable em
systemctl --user daemon-reload
systemctl enable binderly-kiosk.service

echo "Installation finished; Reboot to Finish"
