#!/bin/sh

#script to run from an init system to launch the touchscreen interface

cd /home/pi/Thermal_imager_touchscreen
su pi -c ./run.sh
/sbin/poweroff
