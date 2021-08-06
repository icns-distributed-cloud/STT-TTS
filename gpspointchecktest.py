import time
import threading
from queue import Queue
from ublox_gps import UbloxGps
import serial
import math
import aigo_destination_speech
import pyaudio  
import wave  

def playInformationSound():
    chunk = 1024  
    path = 'tts_output/route_information0_kor.wav'
    with wave.open(path, 'rb') as f:
        p = pyaudio.PyAudio()  
        stream = p.open(format = p.get_format_from_width(f.getsampwidth()),  
                        channels = f.getnchannels(),  
                        rate = f.getframerate(),  
                        output = True)
                        
        data = f.readframes(chunk)  
        while data:  
            stream.write(data)  
            data = f.readframes(chunk)  

        stream.stop_stream()  
        stream.close()  

        p.terminate()

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

            point_lon = float(splitline[0])
            point_lat = float(splitline[1])
            route_info = splitline[2]

            PTCdistance = math.sqrt((point_lon-current_location_lon)**2 + (point_lat-current_location_lat)**2)
            if (PTCdistance<=0.0001):
                aigo_destination_speech.speech_route_information(route_info)
                t2 = threading.Thread(target=playInformationSound)
                t2.start()
                point_check = 1
            

    port.close()



t1 = threading.Thread(target=sender)
t1.start()

