# Face Recognition UI Application

A comprehensive GUI application for face recognition with live webcam feed, face detection, and training capabilities.

## Features

- **Live Webcam Feed**: Real-time camera feed with face detection
- **Face Recognition**: Recognizes faces from the trained dataset
- **Face Training**: Capture and train new faces for recognition
- **Modern UI**: Clean, intuitive interface with status indicators
- **Progress Tracking**: Visual progress bar for capture process
- **Multi-threaded**: Training runs in background thread to keep UI responsive

## Requirements

- Python 3.7+
- OpenCV with contrib modules
- Camera/webcam
- Display (for GUI)

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Make sure you have the face detection cascade file:
   - `haarcascade_frontalface_default.xml` should be in the project directory

## Usage

### Running the Application

```bash
python face_recognition_ui.py
```

### How to Use

1. **Start the Application**: Run the script and the UI will open with live camera feed

2. **Face Recognition**: 
   - The application automatically detects faces in the camera feed
   - If a trained model exists, it will recognize known faces
   - Recognition results are displayed on the video feed and status panel

3. **Training New Faces**:
   - Click "Start Training" button (lower right)
   - Enter a User ID (1, 2, 3, etc.)
   - Look at the camera - the app will automatically capture 30 face images
   - Progress is shown in the progress bar
   - When complete, click "Train Model" to train the recognition system

4. **Training the Model**:
   - After capturing faces, click "Train Model"
   - Training runs in background - UI remains responsive
   - Training status is shown in the status panel
   - When complete, the model is automatically loaded

5. **Refresh Model**: Click "Refresh Model" to reload the trained model

### UI Components

- **Video Display**: 800x400 live camera feed with face detection rectangles
- **Status Panel**: Shows current status, recognition results, and capture progress
- **Control Buttons**: 
  - Start Training: Begin face capture process
  - Train Model: Train recognition model with captured faces
  - Refresh Model: Reload trained model
- **Progress Bar**: Shows capture progress (0-30 faces)

### File Structure

```
├── face_recognition_ui.py    # Main UI application
├── dataset/                  # Face images for training
│   ├── User.1.1.jpg
│   ├── User.1.2.jpg
│   └── ...
├── trainer/                  # Trained model files
│   └── trainer.yml
├── haarcascade_frontalface_default.xml  # Face detection cascade
└── requirements.txt          # Python dependencies
```

### Troubleshooting

1. **Camera not working**:
   - Check camera connection
   - Try different camera index (0 or 1)
   - Ensure camera permissions are granted

2. **Face detection not working**:
   - Ensure `haarcascade_frontalface_default.xml` is in the project directory
   - Check lighting conditions
   - Make sure face is clearly visible

3. **Training errors**:
   - Ensure you have opencv-contrib-python installed
   - Check that dataset directory contains valid face images
   - Verify image naming format: `User.{ID}.{number}.jpg`

4. **GUI issues**:
   - For headless systems, ensure X11 forwarding is enabled
   - Check display environment variables
   - Try running with `DISPLAY=:0 python face_recognition_ui.py`

### Advanced Usage

- **Custom Names**: Edit the `names` list in the code to customize recognized names
- **Capture Settings**: Modify `max_captures` variable to change number of face images captured
- **Recognition Threshold**: Adjust confidence threshold in the recognition logic
- **Video Settings**: Modify camera resolution and frame rate in `start_camera()` method

## Technical Details

- Uses OpenCV's LBPH (Local Binary Pattern Histogram) face recognizer
- Haar Cascade classifier for face detection
- Tkinter for GUI framework
- Multi-threading for non-blocking training
- PIL/Pillow for image processing and display

## License

Based on original code by Anirban Kar and Marcelo Rovai. 