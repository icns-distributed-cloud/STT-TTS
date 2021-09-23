
import paho.mqtt.client as paho
import struct
import threading
def on_message(mosq, obj, msg):
    #print("%-20s %d %s" % (msg.topic, msg.qos, msg.payload))
    print(msg.topic,msg.payload.decode('utf-8'))
    #print(msg.topic,msg.payload)
    
    mosq.publish('pong', 'ack', 0)

def on_publish(mosq, obj, mid):
    pass

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

if __name__ == '__main__':
    
    t1 = threading.Thread(target=gpsClient)
    t1.start()
    print(1)
    