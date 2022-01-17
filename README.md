# Inner-Space-Lighting
Build LEDs that respond to human consciousness.

# Materials

You will need:

A Raspberry Pi 3b+ (not tested on the 4 series) with Micro SD card

An external memory stick for storing data

A ubldit TrueRNG: https://ubld.it/truerng_v3

A 5 volt power supply: https://www.amazon.com/gp/product/B074YHN8D1/

As many WS2811 LED strips as you would like: https://www.amazon.com/ALITOVE-Individually-Addressable-Advertising-Waterproof/dp/B01AG923EU/

# Setup

Flash the micro SD card with the 2020-05-28 version of Raspberry Pi OS: https://downloads.raspberrypi.org/raspios_full_armhf/images/. Newer versions appear to result in problems.

Connect your Raspberry Pi to a screen and keyboard, open the terminal and run the following commands:

> git clone https://github.com/DoctorOzone/Inner-Space-Lighting/
> wget https://ubld.it/wp-content/uploads/2014/02/TrueRNG-Linux-udev-rules.tar.gz
> sudo tar -zxvf TrueRNG-Linux-udev-rules.tar.gz -C /etc/udev/rules.d/
> sudo pip3 install board
> sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel
> pip3 install serial
> pip3 install pyserial
> sudo mkdir /media/usb

Note: do NOT run 'sudo apt upgrade', this will break the lights.

Now we must edit the rc.local file, which contains commands run at startup. In the terminal, run 'sudo nano /etc/rc.local'. Insert the following lines after the blue text:

sudo mount /dev/sda1 /media/usb/
sudo python3 /home/pi/WSlights_v5c.py &

Save changes to this file and shut down the Raspberry Pi.
