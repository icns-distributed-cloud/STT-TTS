import time
import threading
from queue import Queue
from ublox_gps import UbloxGps
import serial
import math
import playsound
def sender():
    port = serial.Serial('/dev/ttyACM0', baudrate=460800, timeout=1)
    gps = UbloxGps(port)
    point_check = 0
    with open('points.txt', 'r') as points:
        currentline = points.readline()
        splitline = currentline.split(',')
        while True:
            try: 
                coords = gps.geo_coords()
                print(coords.lon, coords.lat)
                current_location_lon = coords.lon
                current_location_lat = coords.lat
            except (ValueError, IOError) as err:
                print(err) 

            if(point_check == 1):
                currentline = points.readline()
                if(currentline == ''):
                    break
                splitline = currentline.split(',')
                point_check = 0

            point_lon = int(splitline[0])
            point_lat = int(splitline[1])
            route_info = splitline[2]

            PTCdistance = math.sqrt((point_lon-current_location_lon)**2 + (point_lat-current_location_lat)**2)
            if (PTCdistance<=0.00002):
                playsound.playsound(route_info)
                point_check = 1

    port.close()
t1 = threading.Thread(target=sender)
t1.start()
