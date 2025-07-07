''''
Training Multiple Faces stored on a DataBase:
	==> Each face should have a unique numeric integer ID as 1, 2, 3, etc                       
	==> LBPH computed model will be saved on trainer/ directory. (if it does not exist, pls create one)
	==> for using PIL, install pillow library with "pip install pillow"

Based on original code by Anirban Kar: https://github.com/thecodacus/Face-Recognition    

Developed by Marcelo Rovai - MJRoBot.org @ 21Feb18   

'''

import cv2
import numpy as np
from PIL import Image
import os

# Fix locale issues
os.environ['LC_ALL'] = 'C'
os.environ['LANG'] = 'C'

# Path for face image database
path = 'dataset'

# Check if dataset directory exists
if not os.path.exists(path):
    print(f"Error: Dataset directory '{path}' does not exist.")
    print("Please run 01_face_dataset.py first to capture face images.")
    exit()

# Check if dataset directory has images
if len(os.listdir(path)) == 0:
    print(f"Error: Dataset directory '{path}' is empty.")
    print("Please run 01_face_dataset.py first to capture face images.")
    exit()

# Create trainer directory if it doesn't exist
if not os.path.exists('trainer'):
    os.makedirs('trainer')
    print("Created trainer directory")

try:
    recognizer = cv2.face.LBPHFaceRecognizer_create()
except AttributeError:
    print("Error: OpenCV face recognition module not available.")
    print("Please install opencv-contrib-python: pip3 install opencv-contrib-python")
    exit()

detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

# Check if cascade file exists
if detector.empty():
    print("Error: Could not load face detector cascade file.")
    print("Please make sure 'haarcascade_frontalface_default.xml' is in the current directory.")
    exit()

# function to get the images and label data
def getImagesAndLabels(path):

    imagePaths = [os.path.join(path,f) for f in os.listdir(path)]     
    faceSamples=[]
    ids = []

    print(f"Found {len(imagePaths)} images in dataset directory")

    for imagePath in imagePaths:
        try:
            PIL_img = Image.open(imagePath).convert('L') # convert it to grayscale
            img_numpy = np.array(PIL_img,'uint8')

            id = int(os.path.split(imagePath)[-1].split(".")[1])
            faces = detector.detectMultiScale(img_numpy)

            for (x,y,w,h) in faces:
                faceSamples.append(img_numpy[y:y+h,x:x+w])
                ids.append(id)
                
        except Exception as e:
            print(f"Error processing {imagePath}: {e}")
            continue

    return faceSamples,ids

print ("\n [INFO] Training faces. It will take a few seconds. Wait ...")
faces,ids = getImagesAndLabels(path)

if len(faces) == 0:
    print("Error: No faces found in the dataset images.")
    print("Please make sure the face images were captured correctly.")
    exit()

print(f" [INFO] Found {len(faces)} faces from {len(set(ids))} users")

try:
    recognizer.train(faces, np.array(ids))
    
    # Save the model into trainer/trainer.yml
    recognizer.write('trainer/trainer.yml') # recognizer.save() worked on Mac, but not on Pi
    
    # Print the number of faces trained and end program
    print("\n [INFO] {0} faces trained. Exiting Program".format(len(np.unique(ids))))
    print(" [INFO] Model saved to trainer/trainer.yml")
    
except Exception as e:
    print(f"Error during training: {e}")
    exit()
