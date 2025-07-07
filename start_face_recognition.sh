#!/bin/bash

# Face Recognition UI Startup Script
# Ensures proper display environment and launches the application

echo "Starting Face Recognition UI..."

# Set display environment
export DISPLAY=:0
export QT_QPA_PLATFORM=xcb

# Check if display is available
if ! xset q &>/dev/null; then
    echo "Warning: X display not available. Trying to start X server..."
    # Try to start X server if not running
    if command -v startx &>/dev/null; then
        startx &
        sleep 3
    fi
fi

# Verify display is working
if xset q &>/dev/null; then
    echo "Display is available: $DISPLAY"
    echo "Screen resolution: $(xrandr | grep '*' | awk '{print $1}' | head -1)"
else
    echo "Error: Cannot connect to X display"
    echo "Please ensure X server is running or run: startx"
    exit 1
fi

# Launch the face recognition UI
echo "Launching Face Recognition UI..."
python3 face_recognition_ui.py 