#!/usr/bin/env python
import sys, getopt
sys.path.insert(1, '/root/GrovePi/Software/Python')
import RTIMU
import os.path
import time
import math
import datetime
import csv
from grovepi import *

SETTINGS_FILE = "RTIMULib"

#  computeHeight() - the conversion uses the formula:
#
#  h = (T0 / L0) * ((p / P0)**(-(R* * L0) / (g0 * M)) - 1)
#
#  where:
#  h  = height above sea level
#  T0 = standard temperature at sea level = 288.15
#  L0 = standard temperatur elapse rate = -0.0065
#  p  = measured pressure
#  P0 = static pressure = 1013.25
#  g0 = gravitational acceleration = 9.80665
#  M  = mloecular mass of earth's air = 0.0289644
#  R* = universal gas constant = 8.31432
#
#  Given the constants, this works out to:
#
#  h = 44330.8 * (1 - (p / P0)**0.190263)

def computeHeight(pressure):
    return 44330.8 * (1 - pow(pressure / 1013.25, 0.190263));

print("Using settings file " + SETTINGS_FILE + ".ini")
if not os.path.exists(SETTINGS_FILE + ".ini"):
    print("Settings file does not exist, will be created")

s = RTIMU.Settings(SETTINGS_FILE)
imu = RTIMU.RTIMU(s)
pressure = RTIMU.RTPressure(s)
#humidity = RTIMU.RTHumidity(s)
dht_sensor_port = 7

print("IMU Name: " + imu.IMUName())
print("Pressure Name: " + pressure.pressureName())
#print("Humidity Name: " + humidity.humidityName())

if (not imu.IMUInit()):
    print("IMU Init Failed")
    sys.exit(1)
else:
    print("IMU Init Succeeded");

# this is a good time to set any fusion parameters
imu.setSlerpPower(0.02)
imu.setGyroEnable(True)
imu.setAccelEnable(True)
imu.setCompassEnable(True)

if not pressure.pressureInit():
    print("Pressure sensor Init Failed")
else:
    print("Pressure sensor Init Succeeded")

if (dht(dht_sensor_port,1)==""):
    print("Humidity sensor Init Failed")
else:
    print("Humidity sensor Init Succeeded")

#poll_interval = imu.IMUGetPollInterval()
#print("Recommended Poll Interval: %dmS\n" % poll_interval)
poll_interval = 2

file = open('data-collected.csv', 'w')
csv_writer = csv.writer(file, delimiter=',')
row = [["Timestamp","Temperatura", "Humidade","Pressure","Altitude","x","y","z","r","p","y2"]]
csv_writer.writerows(row)

while True:
    if imu.IMURead():
        time.sleep(3)
        # print(imu.getAccel())
        x, y, z = imu.getFusionData()
        [temp,hum]=dht(dht_sensor_port,1)
        print("%f %f %f" % (x,y,z))
        data = imu.getIMUData()
        (data["pressureValid"], data["pressure"], data["temperatureValid"], data["temperature"]) = pressure.pressureRead()
        #(data["humidityValid"], data["humidity"], data["humidityTemperatureValid"], data["humidityTemperature"]) = humidity.humidityRead()
        fusionPose = data["fusionPose"]
        print("r: %f p: %f y: %f" % (math.degrees(fusionPose[0]),
            math.degrees(fusionPose[1]), math.degrees(fusionPose[2])))
        if (data["pressureValid"]):
            print("Pressure: %f, height above sea level: %f" % (data["pressure"], computeHeight(data["pressure"])))
        if (temp):
            print("Temperature: %f" % (temp))
        if (hum):
            print("Humidity: %f" % (hum))
        # if (data["humidityTemperatureValid"]):
            # print("Humidity temperature: %f" % (data["humidityTemperature"]))
        csv_writer.writerows([[datetime.datetime.now(), temp, hum, data["pressure"], computeHeight(data["pressure"]),x,y,z,math.degrees(fusionPose[0]),math.degrees(fusionPose[1]),math.degrees(fusionPose[2])]])
    time.sleep(poll_interval*1.0/10.0)
file.close()
