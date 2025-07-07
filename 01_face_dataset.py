''''
Capture multiple Faces from multiple users to be stored on a DataBase (dataset directory)
	==> Faces will be stored on a directory: dataset/ (if does not exist, pls create one)
	==> Each face will have a unique numeric integer ID as 1, 2, 3, etc                       

Based on original code by Anirban Kar: https://github.com/thecodacus/Face-Recognition    

Developed by Marcelo Rovai - MJRoBot.org @ 21Feb18    

'''

import time
import cv2
import os

# Fix Qt platform plugin issues
os.environ['QT_QPA_PLATFORM'] = 'xcb'
os.environ['QT_QPA_FONTDIR'] = '/usr/share/fonts'
os.environ['QT_LOGGING_RULES'] = 'qt.qpa.*=false'

# Fix locale issues
os.environ['LC_ALL'] = 'C'
os.environ['LANG'] = 'C'

# Set display backend to avoid Qt issues
os.environ['DISPLAY'] = ':0'
os.environ['QT_QPA_PLATFORM'] = 'xcb'

# Create dataset directory if it doesn't exist
if not os.path.exists('dataset'):
    os.makedirs('dataset')
    print("Created dataset directory")

# Try to open camera
cam = cv2.VideoCapture(0)
if not cam.isOpened():
    print("Error: Could not open camera. Trying alternative camera index...")
    cam = cv2.VideoCapture(1)
    if not cam.isOpened():
        print("Error: Could not open any camera. Please check your camera connection.")
        exit()

cam.set(3, 1280) # set video width - increased for better training quality
cam.set(4, 720) # set video height - increased for better training quality

# Load face detector
face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
if face_detector.empty():
    print("Error: Could not load face detector cascade file.")
    exit()

# For each person, enter one numeric face id
face_id = input('\n enter user id end press <return> ==>  ')

print("\n [INFO] Initializing face capture. Look the camera and wait ...")
# Initialize individual sampling face count
count = 0
minW = 0.1*cam.get(3)
minH = 0.1*cam.get(4)
try:
    while(True):
        ret, img = cam.read()
        if not ret:
            print("Error: Could not read frame from camera.")
            break
            
        img = cv2.flip(img, -1) # flip video image vertically
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale( 
            gray,
            scaleFactor = 1.2,
            minNeighbors = 5,
            minSize = (int(minW), int(minH)),
           )
        for (x,y,w,h) in faces:
         
            cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)

            count += 1

            # Save the captured image into the datasets folder
            cv2.imwrite("dataset/User." + str(face_id) + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])
            # Small delay
            time.sleep(0.2)
            print(f"Saved face {count}/15")


        cv2.imshow('image', img)

        k = cv2.waitKey(100) & 0xff # Press 'ESC' for exiting video
        if k == 27:
            break
        elif count >= 15: # Take 30 face sample and stop video
             break

except Exception as e:
    print(f"Error during face capture: {e}")

finally:
    # Do a bit of cleanup
    print("\n [INFO] Exiting Program and cleanup stuff")
    cam.release()
    cv2.destroyAllWindows()


