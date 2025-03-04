#!/bin/bash
echo "Installing..."

#Acquire Root
sudo su

#Install Basic Packages
apt-get install python3
apt-get install python3-pip
apt-get install git

#Fetch Repo
git clone https://github.com/KaiyoFox/binderlySmartLink.git
cd binderlySmartLink

#Install Python Packages
pip install -r requirements.txt --break-system-packages

#Assemble Services
mv binderly-kiosk.service /etc/systemd/system/binderly-kiosk.service
mv binderly-back.service /etc/systemd/system/binderly-back.service

#Refresh & Enable Services
systemctl daemon-reload
systemctl enable binderly-back.service
systemctl enable binderly-kiosk.service

echo "Installation finished; Reboot to Finish"
