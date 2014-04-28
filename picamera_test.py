#Picamera script
from createDataOverlay import *
from GPSController import *
import RPi.GPIO as GPIO
import picamera
import time
import datetime
import threading
import os
import sys
import argparse

# constants
VIDEOFPS = 25
VIDEOHEIGHT = 1080
VIDEOWIDTH = 1920
SLOWFLASHTIMES = [2,2]
FASTFLASHTIMES = [0.5,0.5]

if __name__ == "__main__":
    
    #Command line options
    parser = argparse.ArgumentParser(description="Pelmetcam")
    parser.add_argument("path", help="The location of the data directory")
    parser.add_argument("-d", "--dataoverlay", action="store_true", help="Output data overlay images at runtime")
    args = parser.parse_args()

    try:

        print "starting picamera"
        print "data path: " + args.path
        print "data overlay: " + str(args.dataoverlay)

        #start gps controller
        gpscontrol = GpsController()
        gpscontrol.start()
        print "GPS started controller"

        #infinite while loop, temporarily replace button functionality
        #while True: 

        #get time from GPS else use system time
        currenttime = gpscontrol.fixdatetime
        if (currenttime == None):
            currenttime = datetime.datetime.now()
        
        #create data folder
        foldername = args.path + "/" + "{0:02d}".format(currenttime.year) + "{0:02d}".format(currenttime.month) + "{0:02d}".format(currenttime.day) + "{0:02d}".format(currenttime.hour) + "{0:02d}".format(currenttime.minute) + "{0:02d}".format(currenttime.second)
        if not os.path.exists(foldername): os.makedirs(foldername)
        print "data folder created: " + foldername

        #create data file
        datafile = open(foldername + "/data.csv", "w")

        #create data overlay drawer class
        if args.dataoverlay: datadrawer = DataDrawer(foldername)

        #start recording
        with picamera.PiCamera() as camera:
            #setup camera
            camera.resolution = (VIDEOWIDTH, VIDEOHEIGHT)
            camera.framerate = VIDEOFPS
            camera.vflip = True
            camera.hflip = True
            camera.video_stabilization = True

            #start recording
            camera.start_recording(foldername+"/vid.h264", inline_headers=False)
            print "recording"
            
            #get frame number
            framenumber = camera.frame
            #wait for a bit, GPS data is little behind, give processer a rest
            time.sleep(0.1)
            #record data
            dataString = str(framenumber) + "," 
            dataString += str(gpscontrol.fix.mode) + "," 
            dataString += str(gpscontrol.fixdatetime) + "," 
            dataString += str(gpscontrol.fix.time) + "," 
            dataString += str(gpscontrol.fix.latitude) + "," 
            dataString += str(gpscontrol.fix.longitude) + ","
            dataString += str(gpscontrol.fix.altitude) + ","
            dataString += str(gpscontrol.fix.speed) + ","
            dataString += str(gpscontrol.fix.track) + ","
            dataString += str(gpscontrol.fix.climb) + "\n"
            # dataString += str(tempcontrol.temperature.C) + ","
            # dataString += str(tempcontrol.temperature.F) + "\n"
            datafile.write(dataString)
            #debug, print data to screen
            #print(dataString)
            if args.dataoverlay:
                dataitems = dataString.split(",")
                #create frame
                # newDataFrame(self, frameNo, mode, date, lat, lon, altitude speed, track, climb, tempC)
                datadrawer.newDataFrame(int(dataitems[0]),
                                        int(dataitems[1]),
                                        dataitems[2],
                                        float(dataitems[4]),                    
                                        float(dataitems[5]),
                                        float(dataitems[6]),
                                        float(dataitems[7]),
                                        float(dataitems[8]),
                                        float(dataitems[9]),
                                        float(dataitems[10]))

        #stop the camera
        camera.stop_recording()
        camera.close()

        #recording finished
        print "recording stopped"

        #close file
        datafile.close()

        #wait for a bit
        time.sleep(0.1)
        #debug, print dots to see code is running
        print "."
    
    except KeyboardInterrupt:
        print "user cancelled cntrl c"
        
    except:
        print "Unexpected error - ", sys.exc_info()[0], sys.exc_info()[1]
        raise

    finally:
        print "stopping picamera"


