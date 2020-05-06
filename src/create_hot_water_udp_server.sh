#!/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:

startServer(){
    cmd="/home/pi/repositories/telemetry/hot_water_udp_server.py &"
    eval "$cmd"

    if [ $? == 0 ];then
	echo UDP server started successfully
    else
        echo UDP server failed to start. Code was $?
    fi
}

# Check if process is running. If not then create one.
cmd="/bin/ps -ef | /bin/grep /hot_water_udp_server.py | grep -v grep"
eval "$cmd"
if [ $? -ne 0 ] ; then
  echo Creating new hot water udp server...
  startServer
else
  echo Server already running
fi
