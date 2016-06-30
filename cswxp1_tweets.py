#tweet live updates from CSEXPLORER1
import tweepy
import subprocess, os
import datetime
import itertools

cswspacepeek_dir=os.path.dirname(os.path.abspath(__file__))
twiter_credentials_file=os.path.join(cswspacepeek_dir,"twiter_credentials.txt")
f1=open("C:\\temp\\help.txt")
html2text_file=os.path.join(cswspacepeek_dir,"extlibs","html2text.py")
raw_packets='http://aprs.fi/?c=raw&call=CT1EUS-11&limit=1000&view=normal'

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
	p=subprocess.Popen(["python",html2text_file,link],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	f1=open("C:\\temp\\help.txt","w+")
	f2=open("C:\\temp\\help2.txt","w+")	
	while p.stdout.readline()!='':
		f=p.stdout.readline()
		s=f.replace('\n', ' ').replace('\r', '').replace('WEST', '\n')
		if s.find('[Latitude ')<0 and s.find('[Duplicate ')<0 and s.find('longitude are both 0]')<0 and s.find("[Rate limited")<0:
			f2.write(s)

def get_text_from_rawpackets(rawfile):
	f1=open(rawfile)
	f2=open("C:\\temp\\help.txt","w+")	
	with f1 as f:
		for line in f:
			if line.find("A=")>0:
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
    
	altitude_marks_climbing=[200,1000,3000,6000,10000,15000,25000,30000,35000]
	tweets =[]
	
	while True:
		get_rawpackets(raw_packets)
		get_text_from_rawpackets("C:\\temp\\help2.txt")
		f1=open("C:\\temp\\help.txt")
		lastlines=tail(f1,lines=3)
		altitude_base=0
		for a, b, c in itertools.combinations(lastlines, 3):
			#Tweeting with the temperature values
			if b.strip()[-2:]==c.strip()[-2:]:
				temp=b.strip()[-2:].strip()
			try:
				if int(temp)<10:
					tweet = "#CSEXPLORER1 Its getting colder! - %sC" % (str(temp))
					if not tweet in tweets:
						tweets.append(tweet)
						status = api.update_status(status=tweet)	
				if int(temp)<0:
					tweet = "#CSEXPLORER1 Why didn't anyone send me a coat?! - %sC" % (str(temp))
					if not tweet in tweets:
						tweets.append(tweet)
						status = api.update_status(status=tweet)	
			except:
				continue				
			# #Tweeting with the altitude values
			try:
				altitude=(int(a[a.find("|")+1:a.find("/")].strip())+int(b[b.find("|")+1:b.find("/")].strip())+int(c[c.find("|")+1:c.find("/")].strip()))/3
				if altitude>altitude_base:
					for marks in altitude_marks_climbing:
						if altitude>=marks:
							tweet = "#CSEXPLORER1 I'm getting up! Nice view from up here! - alt: %sm" % (str(altitude))
							if not tweet in tweets:
								tweets.append(tweet)
								status = api.update_status(status=tweet)
					altitude_base=altitude
				elif altitude<altitude_base:
					for marks in altitude_marks_climbing:
						if altitude<=marks:
							tweet = "#CSEXPLORER1 Cause I'm free, free falling! - alt: %sm" % (str(altitude))
							if not tweet in tweets:
								tweets.append(tweet)
								status = api.update_status(status=tweet)
					altitude_base=altitude
			except:
				continue		
if __name__ == "__main__":
  main()