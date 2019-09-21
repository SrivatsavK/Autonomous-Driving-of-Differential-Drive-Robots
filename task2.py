#!/usr/bin/env python
import rospy
import cv2
import numpy as np
from cv_bridge import CvBridge, CvBridgeError
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image
from move_robot_turtlebot3 import MoveKobuki


class BlobFollower(object):

    def __init__(self):
    
        self.bridge_object = CvBridge()
        self.image_sub = rospy.Subscriber("/raspicam_node/image_raw",Image,self.camera_callback)
        self.movekobuki_object = MoveKobuki()

    def camera_callback(self,data):
        
        try:
            # We select bgr8 because its the OpneCV encoding by default
            cv_image = self.bridge_object.imgmsg_to_cv2(data, desired_encoding="bgr8")
        except CvBridgeError as e:
            print(e)
        #print('I am awesome')
        # We get image dimensions and crop the parts of the image we dont need
        # Bare in mind that because its image matrix first value is start and second value is down limit.
        # Select the limits so that it gets the line not too close, not too far and the minimum portion possible
        # To make process faster.
        height, width, channels = cv_image.shape
	#print(height)
        descentre = -200
        rows_to_watch = 1000000
        crop_img = cv_image[(height)/2+descentre:(height)/2+(descentre+rows_to_watch)][1:width]
	cv2.imshow('crop',crop_img)
        
        # Convert from RGB to HSV
        hsv = cv2.cvtColor(crop_img, cv2.COLOR_BGR2HSV)
        
        # Define the Yellow Colour in HSV
        #[[[ 30 196 235]]]
        """
        To know which color to track in HSV, Put in BGR. Use ColorZilla to get the color registered by the camera
        >>> yellow = np.uint8([[[B,G,R]]])
        >>> hsv_yellow = cv2.cvtColor(yellow,cv2.COLOR_BGR2HSV)
        >>> print( hsv_yellow )
        [[[ 60 255 255]]]
        """
        lower_red = np.array([0,150,100])
        upper_red = np.array([30,255,255])
	lower_blue = np.array([90,100,5])
        upper_blue = np.array([120,255,255])

        # Threshold the HSV image to get only blue, red colors
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        mask2 = cv2.inRange(hsv, lower_red, upper_red)
        # Calculate centroid of the blob of binary image using ImageMoments
        m = cv2.moments(mask, False)
	m_red = cv2.moments(mask2, False)
        try:
            cx, cy = m['m10']/m['m00'], m['m01']/m['m00']
	    #print(cx,cy)
        except ZeroDivisionError:
            cx, cy = height/2, width/2
	try:
	    cx1, cy1 = m_red['m10']/m_red['m00'], m_red['m01']/m_red['m00']
	except:
	    cx1, cy1 = height/2, width/2
	    
        # Bitwise-AND mask and original image
        res = cv2.bitwise_and(crop_img,crop_img, mask= mask)
	res_red = cv2.bitwise_and(crop_img,crop_img, mask= mask2)
        
        # Draw the centroid in the resultut image
        # cv2.circle(img, center, radius, color[, thickness[, lineType[, shift]]]) 
        cv2.circle(res,(int(cx), int(cy)), 10,(0,0,255),-1)
	cv2.circle(res_red,(int(cx1), int(cy1)), 10,(0,0,255),-1)

        cv2.imshow("Original", cv_image)
        #cv2.imshow("HSV", hsv)
        #cv2.imshow("MASK", mask)
        cv2.imshow("Blue Mask", res)
	cv2.imshow("Red Mask",res_red)
        
        cv2.waitKey(1) 
	#Position control
 	twist_object = Twist();
	nonzero = res.nonzero()
	nonzeroy = np.array(nonzero[0])
	N_pix = len(nonzeroy)
	nonzero_red = res_red.nonzero()
	nonzeroy_red = np.array(nonzero_red[0])
	N_pix_red = len(nonzeroy_red)
	if N_pix_red > 100000:
		twist_object.linear.x = 0
	elif N_pix < 100000 and N_pix > 10000:
		twist_object.linear.x = 0.1
	elif N_pix > 100000:
		twist_object.linear.x = 0
	else:
		twist_object.linear.x = 0		
	
	print('length = ',N_pix)
	#print(res.nonzero())
	
	#Steering PID
        try:
            a
        except:
            error_x = 0
	    error_1 = 0
	    error_2 = 0
	    
	error_2 = error_1
	error_1 = error_x 	
        error_x = cx - width / 2;	
	a = error_x
        kp = -1/500
 	kd = 1
	ki = 0
	k1 =kp + ki + kd
	k2 = -kp -2*kd
	k3 = kd
	#print('0',error_x,'1',error_1,'2',error_2)
        twist_object.angular.z = -error_x/1150 -error_2/80 
	#k2*error_1 + k3*error_2;
        #rospy.loginfo("ANGULAR VALUE SENT===>"+str(twist_object.angular.z))
        # Make it start turning
        self.movekobuki_object.move_robot(twist_object)
        
    def clean_up(self):
        self.movekobuki_object.clean_class()
        cv2.destroyAllWindows()
        
        

def main():
    rospy.init_node('line_following_node', anonymous=True)
    error1 = 0
    error2 = 0
    error_x = 0
    
    
    line_follower_object = BlobFollower()

    
    rate = rospy.Rate(5)
    ctrl_c = False
    def shutdownhook():
        # works better than the rospy.is_shut_down()
        line_follower_object.clean_up()
        rospy.loginfo("shutdown time!")
        ctrl_c = True
    
    rospy.on_shutdown(shutdownhook)
    
    while not ctrl_c:
        rate.sleep()

    
    
if __name__ == '__main__':
    main()