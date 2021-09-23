#!/usr/bin/python3

# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Google Cloud Speech API sample application using the streaming API.

NOTE: This module requires the additional dependency `pyaudio`. To install
using pip:

    pip install pyaudio

Example usage:
    python transcribe_streaming_mic.py
"""

# [START speech_transcribe_streaming_mic]
from __future__ import division
import re
import sys
from google.cloud import speech
import pyaudio
from six.moves import queue
from posixpath import expanduser
import requests
import json
import settings
import playsound
import aigo_destination_speech
import threading
# import time, rospy, re
# from sensor_msgs.msg import NavSatFix
#from ublox_gps import UbloxGps
#import serial
import math
import wave
import paho.mqtt.client as paho
import os
# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms
#lock = threading.Lock()

def on_publish(mosq, obj, mid):
    pass

def on_message(mosq, obj, msg):
    #print("%-20s %d %s" % (msg.topic, msg.qos, msg.payload))
    global mqtt_lon,mqtt_lat

    if(msg.topic == "gps/current_lon"):
        mqtt_lon = float(msg.payload.decode('utf-8'))
    elif(msg.topic == "gps/current_lat"):
        mqtt_lat = float(msg.payload.decode('utf-8'))
    mosq.publish('pong', 'ack', 0)


def get_location(destination):
    
    center_lon, center_lat = mqtt_lon,mqtt_lat##  #currentgps.get_gps()
    print(center_lon, center_lat)
    tmap_location_url = "https://apis.openapi.sk.com/tmap/pois?version=1&format=json&callback=result"

    rest_api_key = settings.get_apiKey('rest_api_key')

    searchKeyword = destination               #일단 스타벅스 경희대국제캠퍼스점 하나로 코드 작성
    params = {
        "appKey" : rest_api_key,
        "searchKeyword" : searchKeyword,
        "resCoordType" : "WGS84GEO",    #EPSG3857
        "reqCoordType" : "WGS84GEO",    #WGS84GEO
        "radius" : 2, #주변 반경 설정
        "searchtypCd" : "A", #A : 관련도순, R: 거리순
        "centerLon" : center_lon,    #경도             현재 위치 해야 됨
        "centerLat" : center_lat,    #위도
        "count" : 1
    }
    
    res = requests.get(tmap_location_url, params=params)
    print(res.text)

    response_dict = json.loads(res.text)
    searchPoiInfo = response_dict['searchPoiInfo']
    location_pois = searchPoiInfo['pois']
    location_poi = location_pois['poi']
    #print(len(location_poi))
    #print(location_poi)
    for i in location_poi:
        poi_name = i['name']
        poi_Lon = i['frontLon']
        poi_Lat = i['frontLat']
        poi_radius = i['radius']
     #  print(f'poi_name = {poi_name}')
     #  print(f'poi_Lon = {poi_Lon}')
     #  print(f'poi_Lat = {poi_Lat}')
     #  print(f'poi_radius = {poi_radius}\n')

    return center_lon, center_lat, poi_Lon, poi_Lat

def get_route(destination):
    start_lon, start_lat, destination_lon, destination_lat = get_location(destination)


    tmap_route_url = "https://apis.openapi.sk.com/tmap/routes/pedestrian?version=1&format=json&callback=result"

    rest_api_key = settings.get_apiKey('rest_api_key')

    data = {
        "appKey" : rest_api_key,
        "startX" : start_lon,    #경도
        "startY" : start_lat,    #위도
        "endX" : destination_lon,
        "endY" : destination_lat,
        "reqCoordType" : "WGS84GEO",
        "resCoordType" : "WGS84GEO",
        "startName" : "start",
        "endName" : "end",
        "passList" : ""
    }

    res = requests.post(tmap_route_url, data=data)


    response_dict = json.loads(res.text)
    a = []
    with open('route.txt', 'w') as route_file:
        for i in response_dict['features']:
            route_geometry = i['geometry']
            route_properties = i['properties']
            route_type = route_geometry['type']
            route_coordinates = route_geometry['coordinates']
            route_description = route_properties['description']
            print(f'route_type = {route_type}')
            print(f'route_coordinates = {route_coordinates}')
            print(f'route_description = {route_description}\n')

            if route_type == 'LineString':
                for i in route_coordinates:
                    if a == i:
                        continue
                    else : route_file.write(f'l, {i[0]}, {i[1]} \n')
                a = i
            elif route_type == 'Point':
                route_file.write(f'p, {route_coordinates[0]}, {route_coordinates[1]}, {route_description}\n')

class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk
        self.status = 0
        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True
        
    def __enter__(self):                      #with 할 때 자동 실행
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        if self.status == 0 :
            self._buff.put(in_data)
            return None, pyaudio.paContinue
        elif self.status == 1:
            self._buff.put(b'')
            return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)


# def gps_thread(command):
#     lock.acquire()
#     try:
#         aigo_destination_route.get_route(command)
#     finally:
#         lock.release()

'''
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
'''
# def sender():

#     point_check = 0 
#     with open('route.txt', 'r') as points:
        
#         while True:
#             currentline = points.readline()
#             splitline = currentline.split(',')
#             if splitline[0] == 'p':
#                 current_location_lon,current_location_lat = aigo_call_coord()
#                 if(point_check == 0):
#                     point_check = 1
#                     point_lon = float(splitline[1])
#                     point_lat = float(splitline[2])
#                     route_info = splitline[3]
#                     aigo_pub_gps(point_lat, point_lon)
#                 PTCdistance = math.sqrt((point_lon-current_location_lon)**2 + (point_lat-current_location_lat)**2)
#                 if (PTCdistance<=0.00002):
#                     aigo_destination_speech.speech_route_information(route_info)
#                     playsound.playsound('./tts_output/route_information0_kor.wav')
#                     # t2 = threading.Thread(target=playInformationSound)
#                     # t2.start()
#                     point_check = 1
#             elif
#             elif(currentline == ''):
#                         break
#             else : continue
            

    #port.close()



def sender():

    point_check = 0
    with open('route.txt', 'r') as points:
        currentline = points.readline()
        splitline = currentline.split(',')
        while True:

            current_location_lon,current_location_lat = mqtt_lon, mqtt_lat
            print(current_location_lon,current_location_lat)
            if(point_check == 1):
                currentline = points.readline()
                if(currentline == ''):
                    break
                splitline = currentline.split(',')
                if(splitline[0] == 'l'):
                    # aigo_pub_gps(splitline[2], splitline[1])
                    continue
                # aigo_pub_gps(splitline[2], splitline[1])
                point_check = 0


            point_lon = float(splitline[1])
            point_lat = float(splitline[2])
            
            route_info = splitline[3]

            PTCdistance = math.sqrt((point_lon-current_location_lon)**2 + (point_lat-current_location_lat)**2)
            if (PTCdistance<=0.00002):
                aigo_destination_speech.speech_route_information(route_info)
                playsound.playsound('./tts_output/route_information0_kor.wav')
                point_check = 1


# def gps_callback(data):
#     global aigo_long
#     global aigo_lat
#     aigo_long = data.longitude
#     aigo_lat = data.latitude
#     print(aigo_long, aigo_lat)

# def aigo_pub_gps(lat, long):
#     gps_goal_msg = NavSatFix() # message type
#     gps_goal_msg.longitude = long
#     gps_goal_msg.latitude = lat
#     gps_goal_pub.publish(gps_goal_msg)
    
# def aigo_call_coord():
#     return aigo_long, aigo_lat

def listen_print_loop(responses, stream):
    """Iterates through server responses and prints them.

    The responses passed is a generator that will block until a response
    is provided by the server.

    Each response may contain multiple results, and each result may contain
    multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
    print only the transcription for the top alternative of the top result.

    In this case, responses are provided for interim results as well. If the
    response is an interim one, print a line feed at the end of it, to allow
    the next result to overwrite it, until the response is a final one. For the
    final one, print a newline to preserve the finalized transcription.
    """
    num_chars_printed = 0
    aigo_state = 0                         # state 1 : command waiting , state 2 : destination command waiting
    i = 0
    for response in responses:


        if not response.results:
            continue

        # The `results` list is consecutive. For streaming, we only care about
        # the first result being considered, since once it's `is_final`, it
        # moves on to considering the next utterance.
        result = response.results[0]
        if not result.alternatives:
            continue

        # Display the transcription of the top alternative.
        transcript = result.alternatives[0].transcript

        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.
        #
        # If the previous result was longer than this one, we need to print
        # some extra spaces to overwrite the previous result
        overwrite_chars = " " * (num_chars_printed - len(transcript))

        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + "\r")
            sys.stdout.flush()

            num_chars_printed = len(transcript)

        else:

            #print(transcript + overwrite_chars)
            #command = transcript + overwrite_chars
            
            print(transcript + overwrite_chars)
            command = transcript + overwrite_chars

            #print(len(command))
            
            
            if(aigo_state == 1):
                stream.status = 1
                if("길찾기" in command or "길 찾기" in command):
                    playsound.playsound('./tts_output/destination0_kor.mp3')   
                    aigo_state = 2
                elif("노래" in command):
                    playsound.playsound('./tts_output/iloveyoubaby.mp3')                    
                    aigo_state = 0
                else : 
                    playsound.playsound('./tts_output/commandNotFound0_kor.mp3')                    
                    aigo_state = 0
                stream.status = 0
            
            elif(aigo_state == 2):
                #my_thread = threading.Thread(target=gps_thread, args=(command,))
                #my_thread.start()
                get_route(command)
                aigo_destination_speech.speech_destination(command)
                stream.status = 1
                playsound.playsound('./tts_output/destination_speech0_kor.wav')
                t1 = threading.Thread(target=sender)
                t1.start()
                os.system("rosrun aigo_stt_tts aigo_ros_publisher.py")
                stream.status = 0    
                aigo_state = 0
                
                
                #gpsdatasend.point_detect()


            elif("아이고야" in command and aigo_state ==0):
                stream.status = 1
                playsound.playsound('./tts_output/parden0_kor.mp3')        # parden tts  and aigo has command waiting state                
                aigo_state = 1
                stream.status = 0

            else : continue
            # Exit recognition if any of the transcribed phrases could be
            # one of our keywords.
            if re.search(r"\b(exit|quit)\b", transcript, re.I):
                print("Exiting..")
                break

            num_chars_printed = 0



def main():
    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
    language_code = "ko-KR"  # a BCP-47 language tag

    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code,
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True
    )

    

    with MicrophoneStream(RATE, CHUNK) as stream:
        
        audio_generator = stream.generator()
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator
        )

        responses = client.streaming_recognize(streaming_config, requests)
        # Now, put the transcription responses to use.
        
        listen_print_loop(responses, stream)

# def ros_spin():
#     while True:
        
def gpsClient():
    client = paho.Client()
    client.on_message = on_message
    client.on_publish = on_publish

    client.connect("127.0.0.1", 1883, 60)

    client.subscribe("gps/current_lon", 0)
    client.subscribe("gps/current_lat", 0)
    #client.subscribe("adult/#", 0)
    while True:
        if(client.loop()==0):
            pass
        else: break
if __name__ == "__main__":
    #rospy.init_node('aigo_voice') # initialize node
    #gps_goal_pub = rospy.Publisher('gps_goal_fix', NavSatFix, queue_size = 1)
    #current_gps_sub = rospy.Subscriber('fix', NavSatFix, gps_callback)
    
    t1 = threading.Thread(target=gpsClient)
    t1.start()
    main()
    
# [END speech_transcribe_streaming_mic]
