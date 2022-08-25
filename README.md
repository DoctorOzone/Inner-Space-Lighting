# Inner-Space-Lighting
Build LEDs that respond to human consciousness.

## Materials

You will need:

A Raspberry Pi 3b+ (not tested on the 4 series) with Micro SD card

At least 2 female to male jumper wires

An external memory stick for storing data

A ubldit TrueRNG: https://ubld.it/truerng_v3

A 5 volt power supply: https://www.amazon.com/gp/product/B074YHN8D1/

As many WS2811 LED strips as you would like: https://www.amazon.com/ALITOVE-Individually-Addressable-Advertising-Waterproof/dp/B01AG923EU/

## Setup

Flash the micro SD card with the 2020-05-28 version of Raspberry Pi OS: https://downloads.raspberrypi.org/raspios_full_armhf/images/. Newer versions appear to result in problems.

Connect your Raspberry Pi to a screen and keyboard, open the terminal and run the following commands:

$ git clone https://github.com/DoctorOzone/Inner-Space-Lighting/

$ wget https://ubld.it/wp-content/uploads/2014/02/TrueRNG-Linux-udev-rules.tar.gz

$ sudo tar -zxvf TrueRNG-Linux-udev-rules.tar.gz -C /etc/udev/rules.d/

$ sudo pip3 install board

$ sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel

$ pip3 install serial

$ pip3 install pyserial

$ sudo mkdir /media/usb

If using version 10:

$ pip3 install scipy

$ sudo apt-get install python3-scipy


Note: do NOT run 'sudo apt upgrade', this will break the lights.

Version 5 and USB autostart:

Edit the rc.local file, which contains commands run at startup. In the terminal, run 'sudo nano /etc/rc.local'. Insert the following lines after the blue text:

sudo mount /dev/sda1 /media/usb/
sudo python3 /home/pi/WSlights_v5c.py &

Save changes to this file and shut down the Raspberry Pi.

Version 10 autostart:

Remove the python execution line from the rc.local file, if present. From the home directory:

$ cd .config

$ mkdir autostart

$ cd autostart

$ nano MyApp.desktop

Add the following content:

[Desktop Entry]

Name=Your Application Name

Type=Application

Comment=Some Comments about your program

Exec=sudo python3 /home/pi/WSlights_v10.py


Save and exit, then:

$ sudo chmod +x MyApp.desktop

## Build

The WS2811 LED strips contain power, ground, and data wires, typically red, blue, and white respectively. Using the jumper wires, connect the GPIO 18 pin (usually pin #12) to the data wire and a ground pin (usually pin #14) to the ground wire. Do not attempt to power the LEDs with the Raspberry Pi - instead, connect that to your external power supply. If chaining multiple LED strips together, it may be important to supply power to both ends, or at multiple points, to reduce color loss.

Plug in the TrueRNG and your external storage device into any USB ports.

## Use

Power on the Raspberry Pi and wait about 1 minute. The application should run. By default, this assumes a 14 x 14 grid array of lights.

To gracefully shutdown and save data files, connect pins 39 and 40 with something conductive, wait for the lights to turn off, then wait about 30 seconds before unplugging.

## Customizing

With consciousness-driven lighting, each LED is classified as either a filler or a node. The colors of nodes are controlled by independent bitstreams from the TrueRNG, and the fillers blend the colors from neighboring nodes.

To create a design, make a text or csv file with the columns X,Y,Z,IsNode. The X, Y, and Z values should corrospond to the approximate spatial positions of the lights in your design. Units of measurement do not matter, as long as it is within the cartesian coordinate system. You can use integers, floating points, and negative numbers. The IsNode column should contain 0 if the LED is a filler, and 1 if it is a node.

Open SimShape.py and configure the settings:


light_config_file = 'pegboard.txt' #enter the design file you just made

output_filename = 'pegboard_sim.txt' #name of output file for simulation

WM_ll = 1.9 #minimum distance, in the spatial units you used, between *neighboring* nodes

WM_ul = 2.3 #maximum distance, in the spatial units you used, between *neighboring* nodes


It is recommended to run this script on your local machine, as running it on the Raspberry Pi will take a very long time to complete.

When the script completes, open WSlights_v5c.py and configure the settings:


detectlights = 200 #How many LEDs are detectable. Should be a multiple of 50, even if not all lights will be used.

StartLight = 4 #Start counting at 0 and tell the program what light to start at.

light_config_file = 'pegboard.txt' #enter the design file you just made

simulation_file = 'pegboard_sim.txt' #enter the simulation file just produced by SimShape.py

WM_ll = 1.9 #minimum distance, in the spatial units you used, between *neighboring* nodes

WM_ul = 2.3 #maximum distance, in the spatial units you used, between *neighboring* nodes

Csamp_scale = 10 #Number of samples the script will draw when Z/e = 1. Roughly speaking, higher numbers will require you to do less "work" to achieve an aesthetic output.


That's it! Enjoy
