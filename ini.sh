#!/bin/bash

# define variables
grovepi=/root/grovepi/Software/Python
BMP=/root/grovepi/Software/Python/grove_barometer_sensors/barometric_sensor_bmp180
 
# define environment variables
export PYTHONPATH=$grovepi:$BMP

python csxp1/csxp1_collectdata.py