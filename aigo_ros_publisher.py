#!/usr/bin/python3
# -*- coding: utf-8 -*-
import rospy
import time
from actionlib_msgs.msg import GoalStatus
from sensor_msgs.msg import NavSatFix
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
import actionlib
import paho.mqtt.client as paho
import paho.mqtt.publish as publish
import threading
def edgeClient():
    client = paho.Client()
    client.on_message = on_message
    client.on_publish = on_publish

    client.connect("163.180.117.43", 1883, 60)

    client.subscribe("gps/current_lon", 0)
    client.subscribe("gps/current_lat", 0)
    #client.subscribe("adult/#", 0)
    #while True:
    #    if(client.loop()==0):
    #        pass
    #    else: break

def on_publish(mosq, obj, mid):
    pass

def on_message(mosq, obj, msg):
    #print("%-20s %d %s" % (msg.topic, msg.qos, msg.payload))
    global car, tl, cw, goal
    
    if(msg.topic == "/detect/car"):
        car = int(msg.payload.decode('utf-8'))

    elif(msg.topic == "/detect/tl"):
        tl = int(msg.payload.decode('utf-8'))

    elif(msg.topic == "/detect/cw"):
        cw = int(msg.payload.decode('utf-8'))
    elif(msg.topic == "/goal"):
        goal = int(msg.payload.decode('utf-8'))
    mosq.publish('pong', 'ack', 0)

def wait_for_signal():
    global car, tl, cw
    while (client.loop()==0):
        if (car == 1):
            rospy.loginfo("wait_for_signal loop break succeed")
            cw = 0
            car = 0
            break
        if (tl == 1):
            rospy.loginfo("tl = 1")
            cw = 0
            tl = 0
            break

def aigo_pub_gps(lat, long):
    gps_goal_msg = NavSatFix() # message type
    gps_goal_msg.longitude = long
    gps_goal_msg.latitude = lat
    gps_goal_pub.publish(gps_goal_msg)

if __name__ == '__main__':
    global point_check
    global car, tl, cw, goal
    car = 0
    tl = 0
    goal = 0
    cw = 0
    rospy.init_node('aigo_ros_publisher') # initialize node
    gps_goal_pub = rospy.Publisher('gps_goal_fix', NavSatFix, queue_size = 1)
    rospy.loginfo("Connecting to move_base...")
    move_base = actionlib.SimpleActionClient('move_base', MoveBaseAction)
    move_base.wait_for_server()
    rospy.loginfo("Connected.")
    point_check = 0
    client = paho.Client()
    client.on_message = on_message
    client.on_publish = on_publish

    client.connect("163.180.117.43", 1883, 60)

    client.subscribe("/detect/car", 0)
    client.subscribe("/detect/tl", 0)
    client.subscribe("/goal")
#    edgeClient()
    #t1 = threading.Thread(target=edgeClient)
    #t1.start()

    rospy.loginfo("Connecting to MQTT Broker...")
    
    rospy.loginfo("MQTT Connected.")


    with open("route_ros.txt", 'r') as points:
        currentline = points.readline()
        splitline = currentline.split(',')
        print(splitline[2], splitline[1])
        aigo_pub_gps(float(splitline[2]), float(splitline[1]))
        rospy.loginfo("Published First waypoint.")
        #print(move_base.get_state())
        
        print(move_base.get_goal_status_text())
        if(splitline[0] == 'p'):
            if(splitline[3].find("횡단보도") > 0):
                cw = 1
        time.sleep(5.0)
        while not rospy.is_shutdown():
            print(point_check)
            if(point_check == 1):
                point_check = 0
                currentline = points.readline()
                if(currentline == ''):
                    break
                splitline = currentline.split(',')
                print(splitline[2])
                print(splitline[1])
                aigo_pub_gps(float(splitline[2]), float(splitline[1]))
                rospy.loginfo("Published Next waypoint.")
                if(splitline[0]=='p'):
                    if(splitline[3].find("횡단보도")>0):
                        cw=1
            #move_base.wait_for_result()
            #print(GoalStatus.SUCCEEDED)
            #if(move_base.get_state()==GoalStatus.SUCCEEDED):
            while(client.loop()==0):
             #   print(goal)
                if(goal == 1):
                    goal = 0
                    point_check = 1
                    break

            if(cw == 1):
                publish.single(topic="/detect/cw", payload="1", hostname="163.180.117.43")
                rospy.loginfo("wait_for_signal loop start")
                wait_for_signal() 
            time.sleep(0.1)
        rospy.loginfo("Finish")
            

            
