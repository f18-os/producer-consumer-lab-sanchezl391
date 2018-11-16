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
    vidcap = cv2.VideoCapture('clip.mp4')
    success,image = vidcap.read()

    print("Starting to extract frames")
    
    while success: 
        semColoredEmpty.acquire()
        semColoredMutex.acquire()
        # Move frames into buffer
        s, jpgImage = cv2.imencode('.jpg', image)
        jpgAsText = base64.b64encode(jpgImage) 
        coloredFrameBuffer.put(jpgAsText)
        success,image = vidcap.read()# get next frame
        if not success:
            print("Finished running T1")
            break
        semColoredMutex.release()
        semColoredFull.release()
    

def makeGrayscale():
    global extractThread1
    print("Starting to read/make grayscale frames")
    while True: 
        # Consumer. Get frame from colored frame buffer
        semColoredFull.acquire()

        semColoredMutex.acquire()

        # exit thread if done
        if coloredFrameBuffer.empty() and not extractThread1.isAlive():
            print("T2 finished running")
            break

        frameAsText = coloredFrameBuffer.get()
        jpgRawImage = base64.b64decode(frameAsText)
        # convert the raw frame to a numpy array
        jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)
        img = cv2.imdecode( jpgImage ,cv2.IMREAD_UNCHANGED) # JPG encoded frame
        grayscaleFrame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        a, greyJpgFrame = cv2.imencode('.jpg', grayscaleFrame)
        jpgAsText = base64.b64encode(greyJpgFrame)

        # Producer. Set grayscale frame into grayscale frame buffer
        semGreyEmpty.acquire()
        semGreyMutex.acquire()

        # decode the frame         
        grayscaleFrameBuffer.put(jpgAsText)
        semGreyMutex.release()
        semGreyFull.release()

        semColoredMutex.release()
        semColoredEmpty.release()

def displayImages():
    global frame, cv2
    global makeGrayscaleThread2
    print("Starting to display frames")
    while True: 
        semGreyFull.acquire()
        semGreyMutex.acquire()

        # exit thread if done
        if grayscaleFrameBuffer.empty() and not makeGrayscaleThread2.isAlive():
            print("T3 Finished running")
            break

        frameAsText = grayscaleFrameBuffer.get()
        jpgRawImage = base64.b64decode(frameAsText)
        # convert the raw frame to a numpy array
        jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)
        img = cv2.imdecode( jpgImage ,cv2.IMREAD_UNCHANGED) # this is what is used in DisplayFrames
        cv2.imshow("Video", img)

        if cv2.waitKey(42) and 0xFF == ord("q"):
            break
        semGreyMutex.release()
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

while True:
    if not extractThread1.isAlive() and not makeGrayscaleThread2.isAlive() and not displayImagesThread3.isAlive():
        print('Threads are dead. Finished displaying frames. Program Done.')
        break