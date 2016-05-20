from grovepi import *
import csv
import datetime
import time

dht_sensor_port = 7


with open('/data.csv', 'w') as fp:
	a = csv.writer(fp, delimiter=',')
	data = [["Timestamp","Temperatura", "Humidade"]]
	a.writerows(data)	
	while True:
		try:
			[temp,hum]=dht(dht_sensor_port,1)		
			ts=datetime.datetime.now()
			data = [[ts, temp, hum]]			
			print "temperature = ", temp, " humidity = ", hum			
			a.writerows(data)
			time.sleep(5)
		except (IOError,TypeError) as e:
			print "ERROR!"
