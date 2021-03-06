#tweet live updates from CSEXPLORER1
import tweepy
import subprocess, os
import datetime
import itertools
import random
import time
from lxml import html
import requests

phrases_climbing=["Nice view from up here!","Can I go back now? :/","Watch me mum!", "You can follow my ascent in http://goo.gl/WQLY0u"]
phrases_falling=["Cause I'm free, free falling!","This is fun!","Seriously, this is going too fast now...", "You can follow my fall in http://goo.gl/WQLY0u"]
cswspacepeek_dir=os.path.dirname(os.path.abspath(__file__))
twiter_credentials_file=os.path.join(cswspacepeek_dir,"twiter_credentials.txt")
f1=open("C:\\temp\\help.txt")
html2text_file=os.path.join(cswspacepeek_dir,"extlibs","html2text.py")
raw_packets='http://aprs.fi/?c=raw&call=CT1EUS-11&limit=50&view=normal'

def get_api(cfg):
  auth = tweepy.OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
  auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
  return tweepy.API(auth)

def tail(f, lines=1, _buffer=4098):
    """Tail a file and get X lines from the end"""
    # place holder for the lines found
    lines_found = []

    # block counter will be multiplied by buffer
    # to get the block size from the end
    block_counter = -1

    # loop until we find X lines
    while len(lines_found) < lines:
        try:
            f.seek(block_counter * _buffer, os.SEEK_END)
        except IOError:  # either file is too small, or too many lines requested
            f.seek(0)
            lines_found = f.readlines()
            break

        lines_found = f.readlines()

        # we found enough lines, get out
        if len(lines_found) > lines:
            break

        # decrement the block counter to get the
        # next X bytes
        block_counter -= 1

    return lines_found[-lines:]
  
def get_rawpackets(link):
	f2=open("C:\\temp\\help2.txt","w+")
	page = requests.get(link)
	tree = html.fromstring(page.content)
	raw=tree.xpath("//span[@class='raw_line']//text()")
	test=''
	for r in raw:
		r=r.encode('utf-8')
		test=test+r
	f2.write(test.replace("WEST","\n"))

def get_rawpackets_old(link):
	p=subprocess.Popen(["python",html2text_file,link],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	#f1=open("C:\\temp\\help.txt","w+")
	f2=open("C:\\temp\\help2.txt","w+")	
	while p.stdout.readline()!='':
		f=p.stdout.readline()
		s=f.replace('\n', ' ').replace('\r', '').replace('WEST', '\n')
		f2.write(f)
		if s.find('[Latitude ')<0 and s.find('[Duplicate ')<0 and s.find('longitude are both 0]')<0 and s.find("[Rate limited")<0:
			f2.write(s)

def get_text_from_rawpackets(rawfile,daydate):
	f1=open(rawfile)
	f2=open("C:\\temp\\help.txt","w+")	
	with f1 as f:
		for line in f:
			if line.find("A=")>0 and line.find(daydate)>0:
				altitude=int(int(line[line.find("A=")+2:line.find("A=")+8].strip())*0.3048)
				temperature=line[line.find("'C")-2:line.find("'C")]
				timestamp=line[-21:]
				f2.write(timestamp.replace('\n','')+"| " + str(altitude)+"/ "+temperature+'\n')
	

def main():
	# twiter credentials
	twiter_credentials=open(twiter_credentials_file)
	lines=twiter_credentials.readlines()
	cfg = { 
		"consumer_key"        : lines[0],
		"consumer_secret"     : lines[1],
		"access_token"        : lines[2],
		"access_token_secret" : lines[3] 
		}

	api = get_api(cfg)
    
	altitude_marks_climbing=[50,1000,3000,6000,10000,15000,25000,30000,35000]
	altitude_marks_falling=[50,1000,3000,6000,10000,15000,25000,30000,35000]	
	tweets =[]
	check_burst =0
	
	while True:
		time.sleep(60)
		today=time.strftime("%Y-%m-%d")
		get_rawpackets(raw_packets)
		get_text_from_rawpackets("C:\\temp\\help2.txt",today)
		f1=open("C:\\temp\\help.txt")
		lastlines=tail(f1,lines=3)
		altitude_base=0
		temp=25
		for a, b, c in itertools.combinations(lastlines, 3):
			#Tweeting with the temperature values
			if b.strip()[-2:]==c.strip()[-2:]:
				temp=b.strip()[-2:]
				try:
					if 0<int(temp)<10:
						tweet = "#CSEXPLORER1 : Its getting colder! - %sC" % (str(temp))
						if not tweet in tweets:
							tweets.append(tweet)
							status = api.update_status(status=tweet)
							print tweet
					if int(temp)<=0:
						tweet = "#CSEXPLORER1 : Why didn't anyone send me a coat?! - %sC" % (str(temp))
						if not tweet in tweets:
							tweets.append(tweet)
							status = api.update_status(status=tweet)
							print tweet
				except:
					print "Something went wrong! Code 01. Trying to continue..."			
					continue				
			#Tweeting with the altitude values
			try:
				altitude=(int(a[a.find("|")+1:a.find("/")].strip())+int(b[b.find("|")+1:b.find("/")].strip())+int(c[c.find("|")+1:c.find("/")].strip()))/3
				print str(altitude)
				if altitude>altitude_base:
					for marks in altitude_marks_climbing:
						if altitude>=marks:
							tweet = "#CSEXPLORER1 : %s - alt: %sm" % (random.choice(phrases_climbing),str(altitude))
							if not tweet in tweets:
								tweets.append(tweet)
								status = api.update_status(status=tweet)
								altitude_marks_climbing.remove(marks)
								print tweet
					altitude_base=altitude
				elif altitude<altitude_base:
					tweet = "#CSEXPLORER1 : Wow, Something happened... My balloon just bursteeeeeeed!"
					if not tweet in tweets and check_burst==0:
						tweets.append(tweet)
						status = api.update_status(status=tweet)
						print tweet
						check_burst=1
					for marks in altitude_marks_falling:
						if altitude<=marks:
							tweet = "#CSEXPLORER1 : %s - alt: %sm" % (random.choice(phrases_falling),str(altitude))
							if not tweet in tweets:
								tweets.append(tweet)
								status = api.update_status(status=tweet)
								altitude_marks_falling.remove(marks)
								print tweet
					altitude_base=altitude
			except:
				print "Something went wrong! Code 02. Trying to continue..."
				continue		
if __name__ == "__main__":
  main()