from grovepi import *
import csv
import datetime
import time

dht_sensor_port = 7

def main():
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