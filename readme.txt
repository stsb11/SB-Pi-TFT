Wiring up (from https://aaron-brown.net/blog/?p=99)

TFT    	  Pi		Pin no.
BL_LED 	  GPIO_18	12
SCK    	  SCLK		23
MISO   	  MISO		21
MOSI   	  MOSI		19
CS     	  CE0		24
RST    	  GPIO_25	22
D/C    	  GPIO_24	18
Vin    	  3.3V 		17
GND    	  GND		20

A Pi 3 will not work with the rest of the Aaron-Brown setup guide, and will trash the /boot DIR, necessitating plugging it into a PC to repair.

Use the Adafruit method shown here (for both 2.2" and 2.4").
Hardware Driver (from https://learn.adafruit.com/adafruit-pitft-28-inch-resistive-touchscreen-display-raspberry-pi/easy-install)

curl -SLs https://apt.adafruit.com/add-pin | sudo bash
sudo apt-get install raspberrypi-bootloader adafruit-pitft-helper raspberrypi-kernel
sudo adafruit-pitft-helper -t 22
(22 for for 2.2" and 2.4" non-touch screens)

Use sudo raspi-config to set to boot to CLI, then reboot.

Install dependencies (look at the import lines at the top of the PY file.
Use sudo python tft.py & disown
