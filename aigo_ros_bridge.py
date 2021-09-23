#!/usr/bin/env python

import time, rospy, re
from sensor_msgs.msg import NavSatFix
import paho.mqtt.publish as publish
#import subscriber_ros

def gps_callback(data):
    global aigo_long
    global aigo_lat
    aigo_long = data.longitude
    aigo_lat = data.latitude
    #print(aigo_long, aigo_lat)
    msgs = [{'topic': "gps/current_lon", 'payload': str(aigo_long)},
            {'topic': "gps/current_lat", 'payload': str(aigo_lat)}]
    publish.multiple(msgs, hostname="localhost")

def aigo_pub_gps(lat, long):
    if not rospy.is_shutdown():
        gps_goal_msg = NavSatFix() # message type
        gps_goal_msg.longitude = long
        gps_goal_msg.latitude = lat
        gps_goal_pub.publish(gps_goal_msg)

def aigo_call_coord():
    return aigo_long, aigo_lat

if __name__ == '__main__':
    rospy.init_node('aigo_ros_bridge') # initialize node

    gps_goal_pub = rospy.Publisher('gps_goal_fix', NavSatFix, queue_size = 1)
        
    current_gps_sub = rospy.Subscriber('fix', NavSatFix, gps_callback)
    
    while not rospy.is_shutdown():
        time.sleep(0.1)
