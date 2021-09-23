#!/usr/bin/python3
import rospy
import paho.mqtt.client as paho
import time

def on_message(mosq, obj, msg):
    #print("%-20s %d %s" % (msg.topic, msg.qos, msg.payload))
 

    if(msg.topic == "/detect/car"):
        car = int(msg.payload.decode('utf-8'))
        print("car: ", car)

    elif(msg.topic == "/detect/tl"):
        tl = int(msg.payload.decode('utf-8'))
        print("tl: ", tl)

    elif(msg.topic == "detect/cw"):
        cw = int(msg.payload.decode('utf-8'))
    mosq.publish('pong', 'ack', 0)
 
def on_publish(mosq, obj, mid):
    pass



if __name__ == '__main__':
    global car, tl, cw
    car = 0
    tl = 0
    rospy.init_node('subscribe_test') # initialize node
    rospy.loginfo("Connecting to MQTT External Broker...")
    client = paho.Client()
    
    #client.on_publish = on_publish

    client.connect("163.180.117.43")

    client.subscribe("/detect/car")
    client.subscribe("/detect/tl")
    client.subscribe("detect/cw", 0)
    client.on_message = on_message
    rospy.loginfo("MQTT Connected.")
    print("car: ", car)
    print("tl: ", tl)
    while not rospy.is_shutdown():
        client.loop_forever()
            
