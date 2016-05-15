#!/bin/sh
killall mjpg_streamer
cd /home/pi/mjpg-streamer/mjpg-streamer-experimental && ./mjpg_streamer -i "input_file.so -f /tmp" -o "output_http.so -p 8080 -w ./www" &
cd /home/pi/Thermal_imager_touchscreen


while [ "0" = "0" ] ; do
    python LeptonFB.py
    case $? in
    1)
	echo "switching display"
	if [ "$VC_DISPLAY" = "5" ] ; then
	    export VC_DISPLAY=4
	    echo "Switching to touchscreen"
	else
	    export VC_DISPLAY=5
	    echo "Switching to HDMI"
	fi
	;;
    0) 
	echo "waiting 10 seconds to allow debugging"
	sleep 60
        break
	;;
    2)
	echo "Restarting"
	;;
    esac
done

