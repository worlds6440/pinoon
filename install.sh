#!/bin/bash
sudo cp pinoon /etc/init.d/
sudo chmod +x /etc/init.d/pinoon
sudo update-rc.d pinoon defaults
sudo chmod +x *.py
