import time
import threading
from queue import Queue
from ublox_gps import UbloxGps
import serial
import math
def sender(q,stop):
    port = serial.Serial('/dev/ttyACM0', baudrate=460800, timeout=1)
    gps = UbloxGps(port)
    point_check = 0
    with open('points.txt', 'r') as points:
        currentline = points.readline()
        splitline = currentline.split(',')
        while stop.get() == 0:
            try: 
                coords = gps.geo_coords()
                print(coords.lon, coords.lat)
                current_location_lon = coords.lon
                current_location_lat = coords.lat
            except (ValueError, IOError) as err:
                print(err) 

            if(point_check == 1):
                currentline = points.readline()
                splitline = currentline.split(',')
                point_check = 0

            point_lon = int(splitline[0])
            point_lat = int(splitline[1])
            route_info = splitline[2]

            PTCdistance = math.sqrt((point_lon-current_location_lon)**2 + (point_lat-current_location_lat)**2)
            if (PTCdistance<=0.00002):
                point_check = 1
                q.put(route_info)

            print(f'* sender : {route_info}')
            print('* sender waiting ...')

    port.close()
    q.put(None)
    print('* sender done')

def receiver(q,stop):
    i = 0
    
    while True:
        data = q.get()
        

        if i>10:
            stop.put(1)
            break
        i+=1
        stop.put(0)
        print(f'** receiver : {data}')
        q.task_done()
    
    print('* receiver done')

def point_detect():
    q = Queue()
    stop = Queue()
    stop.put(0)
    t1 = threading.Thread(target=sender, args=(q,stop))
    t2 = threading.Thread(target=receiver, args=(q,stop))
    t1.start()
    t2.start()
