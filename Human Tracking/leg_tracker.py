#!/usr/bin/env python
import rospy
from geometry_msgs.msg  import Twist
from geometry_msgs.msg import PoseArray
from nav_msgs.msg import Odometry
from math import pow,atan2,sqrt
import message_filters
import tf
class turtlebot():

    def __init__(self):
        #Creating our node,publisher and subscriber
        rospy.init_node('turtlebot_controller', anonymous=True)
        self.velocity_publisher = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        goal_pose_subscriber = message_filters.Subscriber('/to_pose_array/leg_detector', PoseArray)
        pose_subscriber = message_filters.Subscriber('/odom',Odometry)
        ts = message_filters.ApproximateTimeSynchronizer([goal_pose_subscriber,pose_subscriber],1,slop = 0.05)
        ts.registerCallback(self.callback)
        pose = Odometry()
        #print(pose)
        self.pose = pose.pose.pose.position
        goal_pose = PoseArray()
        #print(goal_pose)
        try:
            self.goal_pose = goal_pose.poses[0].position
        except IndexError:
            pass
        self.rate = rospy.Rate(1)

    #Callback function implementing the pose value received
    def callback(self,data1,data2):
        #print('a')
        try:
            self.goal_pose = data1.poses[0].position
        except IndexError:
            pass
        #print(self.goal_pose)
        self.pose=data2.pose.pose.position
        #print(self.pose.x)

        orientation = data2.pose.pose.orientation
        quaternion = (orientation.x,orientation.y,orientation.z,orientation.w)
        self.euler = tf.transformations.euler_from_quaternion(quaternion)
        #print(self.goal_pose.position.x)
        #goal_pose.position.x = round(self.goal_pose.position.x, 4)
        #goal_pose.position.y = round(self.goal_pose.position.y, 4)
        #print('step2')

    def get_distance(self, goal_x, goal_y):
        distance = sqrt(pow((goal_x - self.pose.x), 2) + pow((goal_y - self.pose.y), 2))
        return distance

    def move2goal(self):
        while(True):
            #distance_tolerance = input("Set your tolerance:")
            vel_msg = Twist()
            vel_msg.linear.x = 0
            try:
                goal_x = self.goal_pose.x
                goal_y = self.goal_pose.y
                print(goal_x)
                 
            except IndexError:
                goal_x = 0
                goal_y = 0
                vel_msg.linear.x = 0
                vel_msg.angular.z =0
                self.velocity_publisher.publish(vel_msg)
                #print('a')
                continue

            except AttributeError:
                goal_x = 0
                goal_y = 0
                vel_msg.linear.x = 0
                vel_msg.angular.z =0
                self.velocity_publisher.publish(vel_msg)
                #print('b')
                continue

            except:
                vel_msg.linear.x = 0
                vel_msg.angular.z =0
                self.velocity_publisher.publish(vel_msg)
                #print('c')
                continue

            distance_tolerance = 0.35
            #print('awesome')
            
            while sqrt(pow((goal_x - self.pose.x), 2) + pow((goal_y - self.pose.y), 2)) >= distance_tolerance:
                #print(sqrt(pow((goal_x - self.pose.x), 2) + pow((goal_y - self.pose.y), 2)))
                #Porportional Controller
                #linear velocity in the x-axis:
                vel_msg.linear.x = 0.1
                vel_msg.linear.y = 0
                vel_msg.linear.z = 0

                #angular velocity in the z-axis:
                try:
                    a
                except:
                    error_x = 0
                    error_1 = 0
                    error_2 = 0
              
	    
	            error_2 = error_1
	            error_1 = error_x 	
                error_x = atan2(goal_y - self.pose.y, goal_x - self.pose.x) - self.euler[2]
                a = error_x	
                vel_msg.angular.x = 0
                vel_msg.angular.y = 0
                vel_msg.angular.z = error_x - error_2/80

                #Publishing our vel_msg
                self.velocity_publisher.publish(vel_msg)
                self.rate.sleep()
                #print(vel_msg)
            #Stopping our robot after the movement is over
            #print('velocity',vel_msg)
            vel_msg.linear.x = 0
            vel_msg.angular.z = 0
            self.velocity_publisher.publish(vel_msg)
            #print(vel_msg)
      
        rospy.spin()

if __name__ == '__main__':
    try:
        #Testing our function
        x = turtlebot()
        x.move2goal()

    except rospy.ROSInterruptException: pass
