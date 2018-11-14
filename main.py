from ExtractFrames import *
import queue
# from ConvertToGrayscale import *
# from DisplayFrames import *
import threading
import asyncio

# Extract Frames 
coloredFrameBuffer = queue.Queue()
semColoredEmpty = asyncio.Semaphore(10) # Producer waits for
semColoredFull = asyncio.Semaphore(0) # Consumer waits for
semColoredMutex = asyncio.Semaphore()

def extractFrames():
    print("Starting to extract frames")
    global success
    while success: 
    # loop
        print("acquiring semColoredFull")
        semColoredFull.acquire()
        print("acquiring semColoredMutex")
        semColoredMutex.acquire()
        
        # Move frames into buffer
        extractFrame()

        print("releasing semColoredMutex")
        semColoredMutex.release()
        print("releasing semColoredFull")
        semColoredFull.release()
        
# 1. Create buffers and semaphores
# 2. Place ExtractFrames while loop into function: run( )
# 3. extractFrames will contain the producer algorithm

extractThread1 = threading.Thread(target=extractFrames)
extractThread1.start()


