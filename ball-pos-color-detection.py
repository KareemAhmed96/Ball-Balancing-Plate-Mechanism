import cv2
import numpy as np
import serial

cap = cv2.VideoCapture(0)
tracking = False #flag

A_serial = serial.Serial('/dev/ttyACM0', 9600)

while True:
    _,frame = cap.read()
    
    # "Height", "Width", "Depth (0,1,2) : corrosponding to RGB or any color space"
    h_frame,w_frame, d = frame.shape
    
    # Center of image returned from frame.shape function 
    h_frame = int(h_frame/2)  
    w_frame = int(w_frame/2)
	
    # For Debugging	
    # print(h_frame)
    # print(w_frame)
    
    # HSV Conversion
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV) #used in tracking
    
    # Region of interest [from height : to height , from width : to width , from color space : to color space]
    roi       = hsv_frame[ (h_frame - 50) : (h_frame + 50) , (w_frame - 50) : (w_frame + 50), : ] #croping
    hsv_roi   = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV) #used in min & max
   
    
    """Tracking"""
    
    if tracking == True:
        mask = cv2.inRange(hsv_frame, min_HSV, max_HSV)
        
        # neglect arguments (1 & 3), just use "cv2.CHAIN_APPROX_SIMPLE"
        # returns a list describing the contours "lines" surrounding the object
        _,contours,_ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	
	# Debugging
        # print(contours)
        
        for contour in contours:
            if cv2.contourArea(contour) > 500:
                x,y,w,h = cv2.boundingRect(contour) #returns coordinates ex: (x+w, y+h)
                frame = cv2.rectangle(frame, (x,y), (x+w,y+h), (255, 0, 0), 2) #drawing a rectangle
        
	# Debugging
        # cv2.imshow("FRAME",frame)

        """Ball Position"""

        pos_x = int(x+w/2)
        pos_y = int(y+h/2)
	
	# Debugging
        # print(pos_x)
        # print(pos_y)

        if ( (pos_x > (w_frame + 50)) and (pos_y > (h_frame - 50))):
            print("1 - Bottom Right Corner")
            try:
				A_serial.write("1".encode("utf-8"))
            except:
                print("Error_1")

        elif ( (pos_x > (w_frame + 50)) and (pos_y < (h_frame + 50))):
            print("2 - Top Right Corner")
            try:
                A_serial.write("2".encode("utf-8"))
            except:
                print("Error_2")

        elif ( (pos_x < (w_frame - 50)) and (pos_y > (h_frame - 50))):
            print("3 - Bottom Left Corner")
            try:
                A_serial.write("3".encode("utf-8"))
            except:
                print("Error_3")
  
        elif ( (pos_x < (w_frame - 50)) and (pos_y < (h_frame + 50))):
            print("4 - Top Left Corner")
            try:
                A_serial.write("4".encode("utf-8"))
            except:
                print("Error_4")

        else:
            print("Center")
            try:
                A_serial.write("5".encode("utf-8"))
            except:
                print("Error_5")
                       
        cv2.imshow("MASK",mask)
        
    cv2.imshow("Frame", frame)
    
    """"""
    
    # Tests
    cv2.imshow("roi", roi)
	
    # Showing HSV effect
    cv2.imshow("HSV",hsv_frame)
    
    k=cv2.waitKey(1)
    
    if k == ord('s'):
        
        """Range of Color"""
        
	# ROI -> Region of Interest
        # roi[ height , width , HSV ]
        # roi[ : , : , 0] # All hue
        
        h_min = roi[ : , : , 0].min() 			# Minimum hue value "using numpy array function"
        h_max = roi[ : , : , 0].max() 			# Maximum hue value "using numpy array function"
        
        s_min = roi[ : , : , 1].min()			# Minimum & Maximum values of saturation
        s_max = roi[ : , : , 1].max()
        
        v_min = roi[ : , : , 2].min() 			# Minimum & Maximum values of value
        v_max = roi[ : , : , 2].max()
        
        min_HSV = np.array([h_min, s_min, v_min]) 	# Minimum HSV array
        max_HSV = np.array([h_max, s_max, v_max]) 	# Maximum HSV array
        
	#flag
        tracking = True
        
        """"""
    if k == 27 : 		# value of ESC key
        break
    
    if k == ord('o'):
        tracking = False 	# stops tracking
        
cap.release() 			# release camera resource
cv2.destroyAllWindows() 	# close GUI
