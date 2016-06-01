from grovepi import *
import csv
import datetime
import time
import smbus
import sys
import RPi.GPIO as GPIO
sys.path.append('/root/grovepi/Software/Python/grove_barometer_sensors/barometric_sensor_bmp180')
from grove_i2c_barometic_sensor_BMP180 import BMP085

# Initialise the BMP085 and use STANDARD mode (default value)
# bmp = BMP085(0x77, 0)  # ULTRALOWPOWER Mode
bmp = BMP085(0x77, 1)  # STANDARD Mode
# bmp = BMP085(0x77, 2)  # HIRES Mode
# bmp = BMP085(0x77, 3)  # ULTRAHIRES Mode

# Initialise the dht sensor
dht_sensor_port = 7

# set bus port number according to rPI version
rev = GPIO.RPI_REVISION
if rev == 2 or rev == 3:
    bus = smbus.SMBus(1)
else:
    bus = smbus.SMBus(0)

def main():
	with open('/data.csv', 'w') as fp:
		a = csv.writer(fp, delimiter=',')
		data = [["Timestamp","Temperatura", "Humidade","Pressure","Altitude"]]
		a.writerows(data)	
		while True:
			try:
				[temp,hum]=dht(dht_sensor_port,1)
				pressure = bmp.readPressure()
				altitude = bmp.readAltitude(101560)
				ts=datetime.datetime.now()
				data = [[ts, temp, hum, pressure, altitude]]			
				print "temperature = ", temp, " humidity = ", hum, " pressure = ", pressure, " altitude = ", altitude
				if isinstance(temp,float) and isinstance(hum,float):
					a.writerows(data)
				time.sleep(5)
			except (IOError,TypeError) as e:
				print "ERROR!"

if __name__ == "__main__":
	try:
		main()
	except:		
		print "Unexpected error:", sys.exc_info()[1]
