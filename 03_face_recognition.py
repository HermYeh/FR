''''
Real Time Face Recogition
	==> Each face stored on dataset/ dir, should have a unique numeric integer ID as 1, 2, 3, etc                       
	==> LBPH computed model (trained faces) should be on trainer/ dir
Based on original code by Anirban Kar: https://github.com/thecodacus/Face-Recognition    

Developed by Marcelo Rovai - MJRoBot.org @ 21Feb18  

'''

import cv2
import numpy as np
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

# Check if trainer file exists
if not os.path.exists('trainer/trainer.yml'):
    print("Error: Trainer file 'trainer/trainer.yml' does not exist.")
    print("Please run 02_face_training.py first to train the model.")
    exit()

try:
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('trainer/trainer.yml')
except AttributeError:
    print("Error: OpenCV face recognition module not available.")
    print("Please install opencv-contrib-python: pip3 install opencv-contrib-python")
    exit()
except Exception as e:
    print(f"Error loading trainer file: {e}")
    exit()

# Load multiple cascade classifiers for different face angles
frontalCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
profileCascade = cv2.CascadeClassifier("haarcascade_profileface.xml")

# Check if cascade files exist
if frontalCascade.empty():
    print("Error: Could not load frontal face detector cascade file.")
    print("Please make sure 'haarcascade_frontalface_default.xml' is in the current directory.")
    exit()

if profileCascade.empty():
    print("Warning: Could not load profile face detector cascade file.")
    print("Profile face detection will be disabled.")
    print("Please make sure 'haarcascade_profileface.xml' is in the current directory.")
    profileCascade = None

font = cv2.FONT_HERSHEY_SIMPLEX

#iniciate id counter
id = 0

# names related to ids: example ==> Marcelo: id=1,  etc
names = ['None', 'Marcelo', 'Paula', 'Ilza', 'Z', 'W'] 

# Initialize and start realtime video capture
cam = cv2.VideoCapture(0)
if not cam.isOpened():
    print("Error: Could not open camera. Trying alternative camera index...")
    cam = cv2.VideoCapture(1)
    if not cam.isOpened():
        print("Error: Could not open any camera. Please check your camera connection.")
        exit()

cam.set(3, 1280) # set video width - increased for better recognition quality
cam.set(4, 720) # set video height - increased for better recognition quality

# Define min window size to be recognized as a face
minW = 0.1*cam.get(3)
minH = 0.1*cam.get(4)

print("\n [INFO] Starting face recognition. Press 'ESC' to exit.")

try:
    while True:

        ret, img = cam.read()
        if not ret:
            print("Error: Could not read frame from camera.")
            break
            
        img = cv2.flip(img, -1) # Flip vertically

        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

        # Detect frontal faces
        frontal_faces = frontalCascade.detectMultiScale( 
            gray,
            scaleFactor = 1.1,  # More sensitive - smaller scale factor
            minNeighbors = 3,    # More sensitive - fewer neighbors required
            minSize = (int(minW), int(minH)),  # Detect smaller faces (closer faces)
           )
        
        # Detect profile faces (side faces)
        profile_faces = []
        if profileCascade is not None:
            profile_faces = profileCascade.detectMultiScale( 
                gray,
                scaleFactor = 1.1,  # More sensitive - smaller scale factor
                minNeighbors = 3,    # More sensitive - fewer neighbors required
                minSize = (int(minW), int(minH)),  # Detect smaller faces (closer faces)
               )
        
        # Combine all detected faces
        faces = list(frontal_faces) + list(profile_faces)

        for(x,y,w,h) in faces:

            cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)

            id, confidence = recognizer.predict(gray[y:y+h,x:x+w])

            # Check if confidence is less them 100 ==> "0" is perfect match 
            if (confidence < 100):
                id = names[id]
                confidence = "  {0}%".format(round(100 - confidence))
            else:
                id = "unknown"
                confidence = "  {0}%".format(round(100 - confidence))
            
            cv2.putText(img, str(id), (x+5,y-5), font, 1, (255,255,255), 2)
            cv2.putText(img, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)  
        
        cv2.imshow('camera',img) 

        k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
        if k == 27:
            break

except Exception as e:
    print(f"Error during face recognition: {e}")

finally:
    # Do a bit of cleanup
    print("\n [INFO] Exiting Program and cleanup stuff")
    cam.release()
    cv2.destroyAllWindows()
