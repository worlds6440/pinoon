Pi Noon
=======

Mini Pi Noon code
-----------------

Ensure [pinoon](pinoon) init.d script file contains correct project install path.

	sudo cp /home/pi/Projects/pinoon/pinoon /etc/init.d/  
	sudo chmod +x /etc/init.d/pinoon  
	sudo update-rc.d pinoon defaults  

Or for a simpler service install, just run with *sudo* permission the [install.sh](install.sh) file.


You must install bluetooth service and cwiid python module

	sudo apt-get install --no-install-recommends bluetooth  
	sudo apt-get install python-cwiid  
