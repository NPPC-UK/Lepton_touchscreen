#!/bin/sh
cd /home/pi/mjpg-streamer/mjpg-streamer-experimental && ./mjpg_streamer -i "input_file.so -f /tmp" -o "output_http.so -p 8080 -w ./www" &
cd /home/pi/Thermal_imager_touchscreen


while [ "0" = "0" ] ; do
    python LeptonFB.py
    if [ "$?" = "1" ] ; then
	echo "switching display"
	if [ "$VC_DISPLAY" = "5" ] ; then
	    export VC_DISPLAY=4
	    echo "Switching to touchscreen"
	else
	    export VC_DISPLAY=5
	    echo "Switching to HDMI"
	fi
    else
        break
    fi
done

killall mjpg_streamer