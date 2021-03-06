import cv2
import numpy as np
import serial
import config
import time


isConnected = True

try:
    arduino = serial.Serial("/dev/ttyACM0", 9600, timeout=50)
    time.sleep(1)
except:
    isConnected = False
    print("arduino non connesso")


cap = cv2.VideoCapture(0)
kernelOpen=np.ones((5,5))
kernelClose=np.ones((20,20))
font=cv2.FONT_HERSHEY_SIMPLEX

widthScreen= config.widthScreen                 #dimesioni schermo
heightScreen= config.heightScreen
central_zone = config.central_zone
isStopped=False

sensitivity = config.sensitivity
                                  #impostazioni colore
lower_red_0 = np.array([0, 100, 100]) 
upper_red_0 = np.array([sensitivity, 255, 255])
lower_red_1 = np.array([180 - sensitivity, 100, 100]) 
upper_red_1 = np.array([180, 255, 255])





def avanti():
    global isStopped
    isStopped=False
    arduino.write(b'w')  

def stops():
    global isStopped
    
    if not isStopped:
        arduino.write(b's')
    isStopped=True
    #time.sleep(0.05)#chiamata a funzione su arduino per fermare

def indietro():
    global isStopped
    isStopped=False
    arduino.write(b'x')
    #time.sleep(0.05)#chiamata a funzione su arduino per andare indietro
#
def destra():
    global isStopped
    isStopped=False
    arduino.write(b'd')
    #time.sleep(0.05)#chiamata a funzione su arduino per girare a dx

def sinistra():
    global isStopped
    isStopped=False
    arduino.write(b'a')
    #time.sleep(0.05)#chiamata a funzione su arduino per girare a sx

def draw(frame,central_zone,conts):
    cv2.drawContours(frame,conts,-1,(255,0,0),3)

    cv2.line(frame,(int(widthScreen * (1-central_zone)*0.5),0),(int(widthScreen * (1-central_zone)*0.5),220),(255,0,0),2)
    cv2.line(frame,(int(widthScreen * (1 + central_zone)*0.5),0),(int(widthScreen * (1 + central_zone)*0.5),220),(255,0,0),2)

def centroRettangolo():
    _, frame = cap.read()
    frame=cv2.resize(frame,(widthScreen,heightScreen))   #ridimensiona
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
    mask_0 = cv2.inRange(hsv, lower_red_0 , upper_red_0)        
    mask_1 = cv2.inRange(hsv, lower_red_1 , upper_red_1 )

    mask = cv2.bitwise_or(mask_0, mask_1)

    maskOpen=cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernelOpen)
    maskClose=cv2.morphologyEx(maskOpen,cv2.MORPH_CLOSE,kernelClose)

    maskFinal=maskClose

    im,conts,h=cv2.findContours(maskFinal.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)

    draw(frame,central_zone,conts)

    if len(conts) > 0:
        x,y,w,h=cv2.boundingRect(conts[0]) 
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255), 2) 
        cv2.putText(frame, str(0+1),(x,y+h),font,2.,(0,255,255)) 
        xCentroRett=x+w/2
        yCentroRett=y+h/2
    
    return xCentroRett,yCentroRett


while True:

    _, frame = cap.read()
        
    if(isConnected):
            if centroRettangolo() <= int(widthScreen * (1-central_zone)*0.5) :          #confronti per chiamare funzioni per movimento del robot
                sinistra()
            elif centroRettangolo() >= int(widthScreen * (1 + central_zone)*0.5): 
               destra()
            elif centroRettangolo() > int(widthScreen * (1-central_zone)*0.5) and centroRettangolo() < int(widthScreen * (1 + central_zone)*0.5):   
                avanti()
            else : 
                stops()  
    else:
        if(isConnected):
           stops()

    cv2.imshow('frame',frame)
    
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()
