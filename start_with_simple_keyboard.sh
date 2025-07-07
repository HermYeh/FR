#!/bin/bash

echo "Starting Face Recognition System with Simple Keyboard..."

# Check if DISPLAY is set
if [ -z "$DISPLAY" ]; then
    export DISPLAY=:0
    echo "Set DISPLAY to :0"
fi

# Check if we're in the right directory
if [ ! -f "face_recognition_ui.py" ]; then
    echo "Error: face_recognition_ui.py not found in current directory"
    exit 1
fi

# Check if simple keyboard is available
if [ ! -f "simple_keyboard.py" ]; then
    echo "Warning: simple_keyboard.py not found, will use system keyboard"
fi

# Start the face recognition UI
echo "Launching Face Recognition UI..."
python3 face_recognition_ui.py

echo "Face Recognition System closed." 