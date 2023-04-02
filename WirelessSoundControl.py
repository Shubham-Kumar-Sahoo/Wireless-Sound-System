import cv2
import mediapipe as mp
import math
import numpy as np
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


devices = AudioUtilities.GetSpeakers() 
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))


mp_hands = mp.solutions.hands# initialize the Hands class and store it in a variable
hands = mp_hands.Hands() #set the hands function which will hold the landmarks points
mp_draw = mp.solutions.drawing_utils # function to draw the hand landmarks on the image

cap= cv2.VideoCapture(0) # capture image from default camera i.e. 0 

while True:
    success,img=cap.read() # cap.read() returns boolean value in success if it is getting image or not and returns captured image in img
    imgRGB= cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # coverts the BGR image to RGB 
    results=hands.process(imgRGB) # process the RGB image
    # print(results.multi_hand_landmarks)  # print the hand landmarks

    if results.multi_hand_landmarks: # if the hand is presennt in  image

        for handlm in results.multi_hand_landmarks: # for hand landmarks in each hand
            lmlist=[]

            for id,lms in enumerate(handlm.landmark): # all the landmarks numeric values
                # print(id,lms,"\n")
                height,width,channel=img.shape # returns the 3 dimensions of the image
                cx,cy = int(lms.x*width),int(lms.y*height) # returns the x and y coordinates of the landmarks
                # print(id,cx,cy,"\n")
                lmlist.append([id,cx,cy]) 
            # print(lmlist)
            
            if lmlist: 
                x1,y1= lmlist[4][1] , lmlist[4][2] # storing 4th hand landmark dimension
                x2,y2= lmlist[8][1] , lmlist[8][2] # storing 8th hand landmark dimension

                cv2.circle(img,(x1,y1),10,(0,0,0), cv2.FILLED) # creates circles on 4th hand landmark 
                cv2.circle(img,(x2,y2),10,(0,0,0), cv2.FILLED) # creates circles on 8th hand landmark
                cv2.line(img,(x1,y1),(x2,y2),(0,0,0),4) # creates a line from 4th hand landmark to 8th hand landmark


                length = math.hypot((x2-x1),(y2-y1)) # calculates the length between 4th and 8th hand landmark
                # length = 20 ----> vol = 0 ----> vol range = -96.0
                # length = 200 ----> vol = 100 ----> vol range = 0.0

                volRange= volume.GetVolumeRange() # this function get the system volume range and store it in volRange list
                minVol= volRange[0] # min volume 
                maxVol= volRange[1] # max volume


                vol=np.interp(length,[20,200], [minVol,maxVol]) # convert [20,200] to [minVol,maxVol] range
                volume.SetMasterVolumeLevel(vol,None) # set volume level to vol 
                volBar = np.interp(length , [20 ,200] , [400 ,150]) # gives the length of the volume bar 
                volPer = np.interp(length , [25 ,200] , [0 ,100])  # gives the volume range from 0 to 100


                cv2.rectangle(img , (50 ,150) , (85 , 400) ,(0,0,0) ,3) # create a rectangle border for volume bar 
                cv2.rectangle(img , (50 , int(volBar)) , (85 ,400) ,(0, 231,23) ,cv2.FILLED) # create a filled rectangle bar for volume bar
                cv2.putText(img , str(int(volPer)) , (40, 450) ,cv2.FONT_HERSHEY_PLAIN ,4 , (0,0,0) , 3)  # create a text for showing volume level     



    cv2.imshow("Image",img) # display image in a new window, parameters:- Window name and captured image i.e. img
    cv2.waitKey(1) # camera will wait for 1 milliseconds before capturing again
    if not success:
        print("Ignore empty camera frame ")
        continue