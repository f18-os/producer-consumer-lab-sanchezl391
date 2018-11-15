from ExtractFrames import *
import queue
from ConvertToGrayscale import *
from DisplayFrames import *
import threading
import asyncio
import numpy as np
import cv2

# Extract Frames/Grayscale
semColoredEmpty = asyncio.Semaphore(10) # Producer waits for
semColoredFull = asyncio.Semaphore(0) # Consumer waits for
semColoredMutex = asyncio.Semaphore()
 
# Grayscale/Display Frames
semGreyEmpty = asyncio.Semaphore(10) # Producer waits for
semGreyFull = asyncio.Semaphore(0) # Consumer waits for
semGreyMutex = asyncio.Semaphore()

coloredFrameBuffer = queue.Queue(maxsize=10) # Extracted Frames
grayscaleFrameBuffer = queue.Queue(maxsize=10) # Grayscale Frames

def extractFrames():
    # global image
    vidcap = cv2.VideoCapture('clip.mp4')
    success,image = vidcap.read()

    print("Starting to extract frames")
    
    print("Reading frame {} {} ".format(count, success))

    while True: 
        print("T1. acquiring semColoredEmpty")
        semColoredEmpty.acquire()
        print("T1. acquiring semColoredMutex")
        semColoredMutex.acquire()
        # Move frames into buffer
        s, jpgImage = cv2.imencode('.jpg', image)
        jpgAsText = base64.b64encode(jpgImage) 
        coloredFrameBuffer.put(jpgAsText)
        # extractFrame()
        success,image = vidcap.read()# get next frame


        print("T1. releasing semColoredMutex")
        semColoredMutex.release()
        print("T1. releasing semColoredFull")
        semColoredFull.release()

def makeGrayscale():
    # grayscaleFrame cant use GLOBAL VARIABLES, use buffers

    print("Starting to read/make grayscale frames")
    while True: 
        # Consumer. Get frame from colored frame buffer
        print("T2 Consumer. acquiring semColoredFull")
        semColoredFull.acquire()

        print("T2 Consumer. acquiring semColoredMutex")
        semColoredMutex.acquire()




        # decode the frame 
        frameAsText = coloredFrameBuffer.get()
        jpgRawImage = base64.b64decode(frameAsText)
        # convert the raw frame to a numpy array
        jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)
        img = cv2.imdecode( jpgImage ,cv2.IMREAD_UNCHANGED) # JPG encoded frame
        # makeGrayscaleFrame(img)
        grayscaleFrame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        a, greyJpgFrame = cv2.imencode('.jpg', grayscaleFrame)
        jpgAsText = base64.b64encode(greyJpgFrame)

        # Producer. Set grayscale frame into grayscale frame buffer
        print("T2 Producer. acquiring semGreyEmpty")
        semGreyEmpty.acquire()

        print("T2 Producer. acquiring semGreyMutex")
        semGreyMutex.acquire()

        grayscaleFrameBuffer.put(jpgAsText)

        print("T2 Producer. releasing semGreyMutex")
        semGreyMutex.release()

        print("T2 Producer. releasing semGreyFull")
        semGreyFull.release()





        











        print("T2 Consumer. releasing semColoredMutex")
        semColoredMutex.release()

        print("T2 Consumer. releasing semColoredEmpty")
        semColoredEmpty.release()

def displayImages():
    global frame, cv2
    print("Starting to display frames")
    while True: 
        print("T3. acquiring semGreyFull")
        semGreyFull.acquire()

        print("T3. acquiring semGreyMutex")
        semGreyMutex.acquire()

        # decode the frame 
        frameAsText = grayscaleFrameBuffer.get()
        jpgRawImage = base64.b64decode(frameAsText)
        # convert the raw frame to a numpy array
        jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)
        img = cv2.imdecode( jpgImage ,cv2.IMREAD_UNCHANGED) # this is what is used in DisplayFrames
        print("Displaying frame")
        cv2.imshow("Video", img)
        if cv2.waitKey(42) and 0xFF == ord("q"):
            break
        print("T3. releasing semGreyMutex")
        semGreyMutex.release()

        print("T3. releasing semGreyFull")
        semGreyEmpty.release()
    
# Extract Images
extractThread1 = threading.Thread(target=extractFrames)
extractThread1.start()

# Make greyscale images
makeGrayscaleThread2 = threading.Thread(target=makeGrayscale)
makeGrayscaleThread2.start()

# Display images
displayImagesThread3 = threading.Thread(target=displayImages)
displayImagesThread3.start()