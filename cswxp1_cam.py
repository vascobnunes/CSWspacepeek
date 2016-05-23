#!/usr/bin/env python
from time import sleep
from datetime import datetime
import os

PHOTO_WIDTH_RES=1920
PHOTO_HEIGHT_RES=1080
PHOTO_QUALITY=98
PHOTO_DIR="/home/pi/cswxp1/photo"

VIDEO_WIDTH_RES=1920
VIDEO_HEIGHT_RES=1080
VIDEO_DURATION_SECS=6
VIDEO_DIR="/home/pi/cswxp1/video"

def currentTimestamp():
    now = datetime.now()
    return str(now.year) + str(now.month) + str(now.day) + str(now.hour) + str(now.minute) + str(now.second)

def takePicture():
    print("Taking pretty picture")
    os.system("raspistill -w {} -h {} -q {} -t 200 -n -o {}/pic{}.jpg".format(PHOTO_WIDTH_RES, PHOTO_HEIGHT_RES, PHOTO_QUALITY, PHOTO_DIR, currentTimestamp())) 

def recordVideo():
    print("Recording nifty video")
    os.system("raspivid -w {} -h {} -t {} -n -o {}/vid{}.h264".format(VIDEO_WIDTH_RES, VIDEO_HEIGHT_RES, VIDEO_DURATION_SECS*1000, VIDEO_DIR, currentTimestamp()))

def mainLoop():
    while True:
        recordVideo()
        sleep(1)
        takePicture()
        sleep(1)

if __name__ == "__main__":
    if not os.path.exists(PHOTO_DIR):
        os.makedirs(PHOTO_DIR)
    
    if not os.path.exists(VIDEO_DIR):
        os.makedirs(VIDEO_DIR)
    
    mainLoop()