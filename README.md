# pinoon
Mini Pi Noon code

Ensure doorbell init.d script file contains correct project install path.
sudo cp /home/pi/Projects/pinoon/pinoon /etc/init.d/
sudo chmod +x /etc/init.d/pinoon
sudo update-rc.d pinoon defaults