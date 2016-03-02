#!/bin/bash
sudo cp /home/pi/Projects/pinoon/pinoon /etc/init.d/
sudo chmod +x /etc/init.d/pinoon
sudo update-rc.d pinoon defaults