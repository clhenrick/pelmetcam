#Picamera script
from GPSController import *
import picamera
import time
import datetime
import threading
import os
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

        #start gps controller
        #gpscontrol = GpsController()

        #create data folder
        if not os.path.exists(foldername): os.makedirs(foldername)
        print "data folder created: " + foldername

        #create data file
        datafile = open(foldername + "/data.csv", "w")

        #start recording
        with picamera.PiCamera(False) as camera:
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
            #wait for a bit, GPS data is little behind, give processer a rest`
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
            dataString += str(gpscontrol.fix.climb) + ","
            dataString += str(tempcontrol.temperature.C) + ","
            dataString += str(tempcontrol.temperature.F) + "\n"
            datafile.write(dataString)
            #debug, print data to screen
            #print(dataString)

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


