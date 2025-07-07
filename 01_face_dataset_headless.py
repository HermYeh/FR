''''
Capture multiple Faces from multiple users to be stored on a DataBase (dataset directory)
	==> Faces will be stored on a directory: dataset/ (if does not exist, pls create one)
	==> Each face will have a unique numeric integer ID as 1, 2, 3, etc                       
	==> HEADLESS VERSION - No GUI display required

Based on original code by Anirban Kar: https://github.com/thecodacus/Face-Recognition    

Developed by Marcelo Rovai - MJRoBot.org @ 21Feb18    

'''

import cv2
import os
import time

# Fix locale issues
os.environ['LC_ALL'] = 'C'
os.environ['LANG'] = 'C'

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
print(" [INFO] This is a headless version - no GUI display will be shown")
print(" [INFO] The script will automatically capture faces when detected")
print(" [INFO] Press Ctrl+C to stop the capture process")

# Initialize individual sampling face count
count = 0
last_face_time = 0
face_detection_interval = 1.0  # Minimum time between face captures in seconds

try:
    while(True):
        ret, img = cam.read()
        if not ret:
            print("Error: Could not read frame from camera.")
            break
            
        img = cv2.flip(img, -1) # flip video image vertically
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, 1.3, 5)

        current_time = time.time()
        
        for (x,y,w,h) in faces:
            # Only capture face if enough time has passed since last capture
            if current_time - last_face_time >= face_detection_interval:
                count += 1
                last_face_time = current_time

                # Save the captured image into the datasets folder
                cv2.imwrite("dataset/User." + str(face_id) + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])
                print(f"Saved face {count}/30 - Face detected at position ({x},{y})")

                if count >= 30:  # Take 30 face sample and stop video
                    break

        # Show progress
        if count > 0 and count % 5 == 0:
            print(f"Progress: {count}/30 faces captured")

        # Small delay to reduce CPU usage
        time.sleep(0.1)

        if count >= 30:
            break

except KeyboardInterrupt:
    print("\n [INFO] Capture interrupted by user")

except Exception as e:
    print(f"Error during face capture: {e}")

finally:
    # Do a bit of cleanup
    print(f"\n [INFO] Exiting Program and cleanup stuff")
    print(f" [INFO] Total faces captured: {count}")
    cam.release() 