Pi Noon
=======

Mini Pi Noon code
-----------------

Ensure [pinoon](pinoon) init.d script file contains correct project install path, then setup the init.d script.

	sudo cp /home/pi/Projects/pinoon/pinoon /etc/init.d/  
	sudo chmod +x /etc/init.d/pinoon  
	sudo update-rc.d pinoon defaults  

Or for a simpler service install, just run with *sudo* permission the [install.sh](install.sh) file.

	sudo chmod +x *.sh  
	sudo ./install.sh  

### You must install bluetooth service and cwiid python module

	sudo apt-get install --no-install-recommends bluetooth  
	sudo apt-get install python-cwiid  

### Installing I2C, first enable it in raspi-config

	sudo apt-get install i2c-tools  
	sudo apt-get install python-smbus  


Update: 
https://pythonhosted.org/triangula/sixaxis.html  
	sudo apt-get install bluetooth libbluetooth3 libusb-dev python-dev  
	sudo systemctl enable bluetooth.service  
	sudo usermod -G bluetooth -a pi  
	wget http://www.pabr.org/sixlinux/sixpair.c  
	gcc -o sixpair sixpair.c -lusb  

	sudo ./sixpair  

	bluetoothctl  
	devices  
	agent on  
	trust [MAC]  
	quit  

	ls /dev/input  
	Look for js0  

	pip install triangula  
	